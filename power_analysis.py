"""Prospective Monte Carlo power calculations under explicitly stated assumptions."""
import numpy as np
import pandas as pd
from scipy.stats import ttest_ind
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def power_simulation(effects=(.05,.10,.15,.20),sample_sizes=(30,60,90,120,180),sims=350,seed=21,alpha=.05):
    """Independent 15%-CV normal daily CPA; sim is pedagogical, not time-series empirical power."""
    rng=np.random.default_rng(seed);result=[]
    for effect in effects:
        for n in sample_sizes:
            # Vectorized experiment generation with fixed price units and 15% CV.
            aa=np.maximum(.5,rng.normal(1,.15,size=(sims,n)))
            bb=np.maximum(.5,rng.normal(1+effect,.15,size=(sims,n)))
            p=ttest_ind(aa,bb,axis=1,equal_var=False).pvalue
            result.append({'effect_size_pct':round(effect*100,1),'n_days_per_group':n,'power':float(np.mean(p<alpha)),'simulations':sims,'alpha':alpha,'assumed_daily_CV':.15,'replicates_independent':True})
    return pd.DataFrame(result)

def recommend_sample_size(df):
    out=[]
    for e,g in df.groupby('effect_size_pct'):
        valid=g[g.power>=.8]
        needed=int(valid.n_days_per_group.min()) if len(valid) else None
        out.append({'effect_size_pct':e,'minimum_tested_days_for_80pct_power':needed,'n_90_days_sufficient':bool(needed is not None and needed<=90)})
    return pd.DataFrame(out)

def plot_power(df,fig_dir):
    fig_dir.mkdir(parents=True,exist_ok=True)
    fig,ax=plt.subplots(figsize=(9,5.5))
    for e,g in df.groupby('effect_size_pct'):
        ax.plot(g.n_days_per_group,g.power,marker='o',label=f'{e:g}% CPA difference')
    ax.axhline(.8,linestyle='--',label='80% target')
    ax.set_ylim(0,1.02);ax.set_xlabel('Independent days per channel');ax.set_ylabel('Simulated power')
    ax.set_title('Power for daily CPA comparison (CV=15%, α=0.05)');ax.legend()
    fig.tight_layout();fig.savefig(fig_dir/'power_analysis_cpa.png',dpi=145);plt.close(fig)
