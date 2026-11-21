"""Cautious, explicitly illustrative allocation of a $500k monthly budget."""
from __future__ import annotations
import numpy as np
import pandas as pd

BUDGET=500_000

def allocate(metrics,tests,budget=BUDGET):
    """Weights are discussion starters, not causal estimates or uplift predictions."""
    df=metrics.copy().reset_index(drop=True)
    n=len(df)
    assert n==7, 'Scenario specifies exactly seven channels'
    # rank: high ROAS and low CPA are good; preserve tie handling.
    rank_cpa=df.cpa.rank(ascending=True,method='average')
    rank_roas=df.roas.rank(ascending=False,method='average')
    df['relative_rank_score']=.6*(n+1-rank_cpa)+.4*(n+1-rank_roas)
    # Evidence guardrail: do not reallocate on rank alone when no BH-significant differences.
    signal=bool(any(tests[k].sig_fdr_bh.any() for k in ('daily_cpa','daily_roas')))
    if signal:
        # Cautious ± 20% relative to equal-share budget; not a causal optimization.
        base=np.ones(n)/n
        centered=(df.relative_rank_score-df.relative_rank_score.mean()).to_numpy(float)
        shift=.2*centered/max(np.max(abs(centered)),1e-12)
        raw=base*(1+shift)
        weights=raw/raw.sum()
        # enforce within 10% to 20% of overall budget, while maintaining total.
        lo,hi=.10,.20
        weights=np.clip(weights,lo,hi)
        for _ in range(100):
            residual=1-weights.sum()
            if abs(residual)<1e-12:break
            free=(weights<hi-1e-12) if residual>0 else (weights>lo+1e-12)
            if not free.any():break
            weights[free]+=residual/free.sum()
            weights=np.clip(weights,lo,hi)
    else:weights=np.ones(n)/n
    allocation=np.floor(weights*budget).astype(int)
    residue=int(budget-allocation.sum())
    order=np.argsort(-(weights*budget-allocation))
    for i in order[:residue]:allocation[i]+=1
    df['monthly_budget_usd']=allocation
    df['share_pct']=allocation/budget*100
    df['allocation_basis']='exploratory capped ranking; no causal evidence' if signal else 'equal exploratory allocation; insufficient corrected evidence'
    assert int(df.monthly_budget_usd.sum())==budget
    return df.sort_values('monthly_budget_usd',ascending=False)


def bootstrap_ci(daily,seed=17,n_boot=1200):
    rng=np.random.default_rng(seed);out=[]
    for name,g in daily.groupby('channel'):
        v=g.cpa.replace([np.inf,-np.inf],np.nan).dropna().to_numpy(float)
        if len(v)<2:continue
        draws=rng.choice(v,(n_boot,len(v)),replace=True).mean(axis=1)
        a,b=np.quantile(draws,[.025,.975])
        out.append({'channel':name,'daily_mean_cpa':v.mean(),'bootstrap_ci_low':a,'bootstrap_ci_high':b,'n_observed_days':len(v),'bootstrap_replicates':n_boot})
    return pd.DataFrame(out)
