"""Load, validate, normalize, and chart the public marketing campaign dataset."""
from __future__ import annotations
import hashlib
from pathlib import Path
import urllib.request
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent
SOURCE_URL = 'https://huggingface.co/datasets/jason1966/alinaboulsi_digital-marketing-performance-dataset/resolve/main/digital_marketing_dataset_30k.csv'
RAW = BASE / 'data' / 'digital_marketing_dataset_30k.csv'
CHANNELS_DEMO = ['Google Search','Meta','TikTok','YouTube','Email','Pinterest','LinkedIn']

def download_public_data(force=False):
    RAW.parent.mkdir(parents=True, exist_ok=True)
    if RAW.exists() and RAW.stat().st_size > 10000 and not force:
        return RAW
    request = urllib.request.Request(SOURCE_URL, headers={'User-Agent':'Mozilla/5.0 CompanyScope-educational-lab/1.0'})
    try:
        with urllib.request.urlopen(request, timeout=90) as response, RAW.open('wb') as f:
            while True:
                chunk = response.read(1024*1024)
                if not chunk: break
                f.write(chunk)
    except Exception:
        RAW.unlink(missing_ok=True)
        raise
    if RAW.stat().st_size < 10000:
        RAW.unlink(missing_ok=True)
        raise ValueError('Unexpectedly small source download')
    return RAW

def fixture_data():
    """Synthetic smoke-test rows, NOT the requested externally sourced dataset."""
    rng=np.random.default_rng(20261121)
    days=pd.date_range('2025-06-01',periods=90)
    out=[]
    for k,ch in enumerate(CHANNELS_DEMO):
        cvr=.034+(.014 if k==0 else 0)+(.008 if k==1 else 0) - (.004 if k in (5,6) else 0)
        for date in days:
            clicks=int(rng.integers(180,400))
            conv=int(rng.binomial(clicks,cvr))
            spend=round(float(clicks*rng.uniform(1.4,2.8)*(1+0.06*k)),2)
            rev=round(float(conv*rng.uniform(43,76)),2)
            out.append(dict(date=date.strftime('%Y-%m-%d'),channel=ch,impressions=int(clicks*rng.uniform(14,34)),clicks=clicks,conversions=conv,spend=spend,revenue=rev,source='DEMO_ONLY'))
    return pd.DataFrame(out)

def prepare(source='hf',days=90):
    """Return clean day/channel rows. Keep only Sales campaigns in source data."""
    if source=='demo':
        raw=fixture_data()
        audit={'source':'Synthetic in-repo fixture; NOT the Hugging Face dataset','raw_rows':len(raw),'filter':'none','licensing_note':'test data only'}
    else:
        path=download_public_data()
        raw=pd.read_csv(path,low_memory=False)
        audit={'source':SOURCE_URL,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'raw_rows':int(len(raw)),'license':'Source license unverified / stated unknown','synthetic':True}
        required={'date','platform','spend','impressions','clicks','conversions','revenue'}
        if not required.issubset(raw.columns):
            raise ValueError(f'Source columns missing: {sorted(required-set(raw.columns))}; got {list(raw.columns)}')
        if 'objective' in raw.columns and raw['objective'].astype(str).str.casefold().eq('sales').sum()>100:
            raw=raw[raw['objective'].astype(str).str.casefold().eq('sales')].copy()
            audit['filter']='Sales objective only, because revenue is not meaningful for all awareness/traffic objectives'
        else:
            audit['filter']='All objectives; revenue not necessarily comparable; inspect data carefully'
        raw=raw.rename(columns={'platform':'channel'})
    fields=['spend','impressions','clicks','conversions','revenue']
    for c in fields:
        raw[c]=pd.to_numeric(raw[c],errors='coerce')
    # This mirror includes DD/MM/YYYY dates despite the dictionary's ISO description.
    # Parse explicitly instead of silently swapping month/day on ambiguous records.
    sample = raw['date'].dropna().astype(str).iloc[0] if raw['date'].notna().any() else ''
    if len(sample) >= 10 and sample[2] == '/' and sample[5] == '/':
        raw['date'] = pd.to_datetime(raw['date'],format='%d/%m/%Y',errors='coerce')
        audit['date_format'] = 'DD/MM/YYYY'
    elif len(sample) >= 10 and sample[4] == '-' and sample[7] == '-':
        raw['date'] = pd.to_datetime(raw['date'],format='%Y-%m-%d',errors='coerce')
        audit['date_format'] = 'YYYY-MM-DD'
    else:
        raw['date'] = pd.to_datetime(raw['date'],dayfirst=True,errors='coerce')
        audit['date_format'] = 'inferred, dayfirst=True'
    raw['channel']=raw['channel'].astype(str).str.strip()
    raw=raw.dropna(subset=['date','channel']+fields)
    before=len(raw)
    valid=(raw['spend']>0)&(raw['impressions']>0)&(raw['clicks']>0)&(raw['clicks']<=raw['impressions'])&(raw['conversions']>=0)&(raw['conversions']<=raw['clicks'])&(raw['revenue']>=0)
    raw=raw[valid].copy()
    audit.update({'dropped_invalid':int(before-len(raw)),'clean_rows':int(len(raw))})
    n_platforms=int(raw['channel'].nunique())
    if source=='hf':
        audit['observed_platform_count']=n_platforms
        audit['observed_platforms']=sorted(raw['channel'].unique().tolist())
        if n_platforms < 6:
            raise ValueError(f'Only {n_platforms} observed platforms after Sales/quality filters; cannot construct seven defensible groups from this source.')
        if n_platforms >= 7:
            channels=raw.groupby('channel')['spend'].sum().nlargest(7).index.tolist()
            raw=raw[raw.channel.isin(channels)].copy()
            audit['grouping_strategy']='Seven observed platforms, selected by total spend'

    end=raw.date.max().normalize()
    cutoff=end-pd.Timedelta(days=days-1)
    recent=raw[raw.date>=cutoff].copy()
    min_active_days=25

    if source=='hf' and n_platforms==6:
        # The publisher's actual CSV has only SIX platforms, so a seventh
        # *platform* cannot honestly be claimed. Instead create seven distinct,
        # non-overlapping delivery segments by splitting ONE observed platform
        # into a specific observed placement and its other observed placements.
        # Do not invent a single campaign row or a new advertising platform.
        if 'placement' not in raw.columns:
            raise ValueError('Six platforms but no placement column: cannot derive seven observed segments.')
        for frame in (raw,recent):
            frame['placement']=frame['placement'].fillna('Unknown').astype(str).str.strip().replace('', 'Unknown')

        def candidate_split(frame):
            options=[]
            for platform, group in frame.groupby('channel',sort=True):
                by_placement=group.groupby('placement')
                if by_placement.ngroups<2:continue
                total_days=group.date.nunique()
                if total_days<min_active_days:continue
                for placement,subset in by_placement:
                    if placement=='Unknown':continue
                    other=group[group.placement.ne(placement)]
                    days_one=int(subset.date.nunique());days_other=int(other.date.nunique())
                    if min(days_one,days_other)<min_active_days:continue
                    # Prefer balanced calendar coverage then observed spend.
                    options.append((min(days_one,days_other),float(group.spend.sum()),
                                    -abs(days_one-days_other),str(platform),str(placement)))
            return max(options,default=None)

        chosen=candidate_split(recent)
        if chosen is None:
            recent=raw.copy()
            audit['window_fallback']='Full observed history: latest window had no placement split with 25 active days on both sides'
            chosen=candidate_split(recent)
        else:
            audit['window_fallback']='None'
        if chosen is None:
            raise ValueError('Six platforms found, but no observed placement split has >=25 active days in both subgroups. Choose another supported dataset; do not fabricate a seventh channel.')
        _,_,_,platform,placement=chosen
        mask=recent.channel.eq(platform)
        chosen_mask=mask & recent.placement.eq(placement)
        recent.loc[chosen_mask,'channel']=f'{platform} | {placement}'
        recent.loc[mask & ~chosen_mask,'channel']=f'{platform} | other placements'
        audit['grouping_strategy']='Six actual platforms; one split into two observed, mutually exclusive placement segments (seven allocation groups, NOT seven platforms)'
        audit['split_platform']=platform
        audit['split_placement']=placement
        audit['derived_segment_names']=[f'{platform} | {placement}',f'{platform} | other placements']
    else:
        if recent.groupby('channel').date.nunique().min()<min_active_days:
            recent=raw.copy()
            audit['window_fallback']='Full observed history because latest window lacked 25 active days per channel'
        else:
            audit['window_fallback']='None'
    daily=recent.groupby(['date','channel'],as_index=False)[fields].sum().sort_values(['date','channel'])
    daily['cpa']=daily.spend/daily.conversions.replace(0,np.nan)
    daily['roas']=daily.revenue/daily.spend.replace(0,np.nan)
    daily['cvr']=daily.conversions/daily.clicks.replace(0,np.nan)
    daily['ctr']=daily.clicks/daily.impressions.replace(0,np.nan)
    audit.update({'analysis_rows':int(len(daily)),'unique_channels':int(daily.channel.nunique()), 'channels':sorted(daily.channel.unique().tolist()),'date_min':str(daily.date.min().date()),'date_max':str(daily.date.max().date()),'active_days_by_channel':{k:int(v) for k,v in daily.groupby('channel').date.nunique().to_dict().items()}, 'source_rows_in_window':int(len(recent))})
    if daily.channel.nunique()!=7: raise AssertionError('Expected seven distinct observed channel/placement groups')
    return daily,audit

def summarize(daily):
    a=daily.groupby('channel',as_index=False)[['impressions','clicks','conversions','spend','revenue']].sum()
    a['ctr']=a.clicks/a.impressions
    a['conversion_rate']=a.conversions/a.clicks
    a['cpa']=a.spend/a.conversions.replace(0,np.nan)
    a['roas']=a.revenue/a.spend.replace(0,np.nan)
    a['revenue_minus_ad_spend']=a.revenue-a.spend
    a['proxy_margin']=a.revenue_minus_ad_spend/a.revenue.replace(0,np.nan)
    a['active_days']=a.channel.map(daily.groupby('channel').date.nunique())
    return a.sort_values('cpa').reset_index(drop=True)

def plot_metrics(a,daily,fig_dir):
    fig_dir.mkdir(parents=True,exist_ok=True)
    for metric,title,label in [
        ('cpa','Cost per attributed conversion by channel','$ / conversion'),
        ('roas','Revenue proxy / advertising spend','ratio'),
        ('conversion_rate','Conversions / clicks by channel','share'),
        ('revenue_minus_ad_spend','Revenue minus advertising spend (not profit)','$')]:
        fig,ax=plt.subplots(figsize=(9,5))
        subset=a.sort_values(metric,ascending=True)
        ax.barh(subset.channel,subset[metric]);ax.set_xlabel(label);ax.set_title(title)
        fig.tight_layout();fig.savefig(fig_dir/f'{metric}_by_channel.png',dpi=145);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,5))
    for label,g in daily.groupby('channel'):
        v=g.cpa.dropna()
        if len(v): ax.hist(v,bins=24,alpha=.35,label=label)
    ax.set_xlabel('Daily cost per conversion ($)');ax.set_ylabel('Days');ax.set_title('Daily CPA variability (only days with conversions)');ax.legend(fontsize=8)
    fig.tight_layout();fig.savefig(fig_dir/'daily_cpa_distributions.png',dpi=145);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,5))
    values=[g.cpa.dropna().to_numpy() for _,g in daily.groupby('channel')]
    names=[ch for ch,_ in daily.groupby('channel')]
    ax.boxplot(values,tick_labels=names,showfliers=False)
    ax.tick_params(axis='x',rotation=35); ax.set_ylabel('Daily CPA ($)');ax.set_title('CPA variation by channel')
    fig.tight_layout();fig.savefig(fig_dir/'daily_cpa_boxplot.png',dpi=145);plt.close(fig)
