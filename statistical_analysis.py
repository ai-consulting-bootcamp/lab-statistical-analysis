"""Defensible channel comparisons at daily and conversion-count levels."""
from itertools import combinations
from math import sqrt
import numpy as np
import pandas as pd
from scipy.stats import ttest_ind,fisher_exact
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ALPHA=.05

def bh_adjust(p):
    p=np.asarray(p,float);m=len(p)
    if not m:return p
    sort=np.argsort(p); ranks=np.arange(1,m+1)
    adj=np.minimum.accumulate((p[sort]*m/ranks)[::-1])[::-1]
    out=np.empty(m);out[sort]=np.minimum(1,adj);return out

def adjust(df):
    df=df.copy();n=len(df)
    if not n:return df
    df['p_bonferroni']=np.minimum(1,df['p_value'].to_numpy()*n)
    df['p_fdr_bh']=bh_adjust(df.p_value.to_numpy())
    df['sig_unadjusted']=df.p_value<ALPHA
    df['sig_bonferroni']=df.p_bonferroni<ALPHA
    df['sig_fdr_bh']=df.p_fdr_bh<ALPHA
    return df.sort_values('p_value')

def compare_daily(daily,metric='cpa'):
    rows=[]
    for a,b in combinations(sorted(daily.channel.unique()),2):
        x=daily.loc[daily.channel.eq(a),metric].replace([np.inf,-np.inf],np.nan).dropna().to_numpy(float)
        y=daily.loc[daily.channel.eq(b),metric].replace([np.inf,-np.inf],np.nan).dropna().to_numpy(float)
        if min(len(x),len(y))<10:continue
        t,p=ttest_ind(x,y,equal_var=False)
        pooled=np.sqrt((np.var(x,ddof=1)+np.var(y,ddof=1))/2)
        diff=float(np.mean(y)-np.mean(x))
        d=diff/pooled if pooled else 0.
        rows.append({'group_a':a,'group_b':b,'metric':metric,'n_a_days':len(x),'n_b_days':len(y),'mean_a':float(np.mean(x)),'mean_b':float(np.mean(y)),'difference_b_minus_a':diff,'pct_difference':diff/np.mean(x)*100 if np.mean(x) else np.nan,'t_statistic':float(t),'p_value':float(p),'cohens_d':float(d),'effect_magnitude': ('negligible' if abs(d)<.2 else 'small' if abs(d)<.5 else 'medium' if abs(d)<.8 else 'large')})
    return adjust(pd.DataFrame(rows))

def compare_fisher(daily):
    total=daily.groupby('channel')[['clicks','conversions']].sum()
    rows=[]
    for a,b in combinations(sorted(total.index),2):
        c1,n1=map(int,[total.loc[a,'conversions'],total.loc[a,'clicks']]);c2,n2=map(int,[total.loc[b,'conversions'],total.loc[b,'clicks']])
        odds,p=fisher_exact([[c1,n1-c1],[c2,n2-c2]],alternative='two-sided')
        rows.append({'group_a':a,'group_b':b,'conversions_a':c1,'clicks_a':n1,'conversions_b':c2,'clicks_b':n2,'rate_a':c1/n1,'rate_b':c2/n2,'rate_diff_b_minus_a':c2/n2-c1/n1,'odds_ratio_a_vs_b':float(odds),'p_value':float(p)})
    return adjust(pd.DataFrame(rows))

def summarize_corrections(tests):
    out=[]
    for family,df in tests.items():
        if df is None or not len(df):continue
        out.append({'family':family,'tests':len(df),'expected_false_positives_under_all_nulls':len(df)*ALPHA,'uncorrected_significant':int(df.sig_unadjusted.sum()),'bonferroni_significant':int(df.sig_bonferroni.sum()),'bh_significant':int(df.sig_fdr_bh.sum()),'bonferroni_alpha':ALPHA/len(df)})
    return pd.DataFrame(out)

def plot_stats(tests,fig_dir):
    fig_dir.mkdir(parents=True,exist_ok=True)
    df=tests['daily_cpa']
    channels=sorted(set(df.group_a).union(df.group_b))
    vals=np.ones((len(channels),len(channels)))
    for _,r in df.iterrows():
        i=channels.index(r.group_a);j=channels.index(r.group_b)
        vals[i,j]=vals[j,i]=r.p_fdr_bh
    fig,ax=plt.subplots(figsize=(8,7))
    m=ax.imshow(-np.log10(np.maximum(vals,1e-16)),cmap='viridis')
    ax.set_xticks(range(len(channels)),channels,rotation=45,ha='right');ax.set_yticks(range(len(channels)),channels)
    ax.set_title('Daily CPA Welch tests: -log10(BH-adjusted p)')
    fig.colorbar(m,ax=ax,label='-log10(p adjusted)')
    fig.tight_layout();fig.savefig(fig_dir/'cpa_pvalue_heatmap.png',dpi=145);plt.close(fig)
    summary=summarize_corrections(tests).set_index('family')
    fig,ax=plt.subplots(figsize=(9,5))
    summary[['uncorrected_significant','bonferroni_significant','bh_significant']].plot.bar(ax=ax)
    ax.set_ylabel('Significant pairwise contrasts');ax.set_title('Multiple-testing correction changes findings');ax.tick_params(axis='x',rotation=0)
    fig.tight_layout();fig.savefig(fig_dir/'correction_comparison.png',dpi=145);plt.close(fig)
