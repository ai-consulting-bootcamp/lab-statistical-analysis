"""End-to-end marketing lab. --source hf downloads public data; demo is smoke testing only."""
from __future__ import annotations
import argparse
import json
from datetime import date
from pathlib import Path
import numpy as np
import pandas as pd
from data_exploration import prepare,summarize,plot_metrics,SOURCE_URL
from statistical_analysis import compare_daily,compare_fisher,summarize_corrections,plot_stats
from power_analysis import power_simulation,recommend_sample_size,plot_power
from recommendations import allocate,bootstrap_ci,BUDGET

BASE=Path(__file__).resolve().parent

def md_table(df,cols=None,maxrows=10):
    if cols is not None:df=df[cols]
    try:return df.head(maxrows).to_markdown(index=False,floatfmt='.3g')
    except ImportError:
        x=df.head(maxrows);return x.to_string(index=False)

def run(source='hf',power_sims=350):
    is_demo=source=='demo'
    out=BASE/('demo_results' if is_demo else 'results')
    figs=BASE/('demo_figures' if is_demo else 'figures')
    out.mkdir(exist_ok=True);figs.mkdir(exist_ok=True)
    daily,audit=prepare(source=source,days=90)
    metrics=summarize(daily)
    if not is_demo:
        (BASE/'data').mkdir(exist_ok=True)
        daily.to_csv(BASE/'data/marketing_data.csv',index=False)
    else:
        (BASE/'demo_data').mkdir(exist_ok=True)
        daily.to_csv(BASE/'demo_data/marketing_data_demo.csv',index=False)
    metrics.to_csv(out/'channel_metrics.csv',index=False)
    plot_metrics(metrics,daily,figs)
    tests={'daily_cpa':compare_daily(daily,'cpa'), 'daily_roas':compare_daily(daily,'roas'), 'fisher_conversion':compare_fisher(daily)}
    for name,df in tests.items():
        if len(df)!=21:raise AssertionError(f'Expected 21 pairwise comparisons in {name}, got {len(df)}')
        df.to_csv(out/f'{name}_comparisons.csv',index=False)
    correction=summarize_corrections(tests)
    correction.to_csv(out/'multiple_comparisons_summary.csv',index=False)
    plot_stats(tests,figs)
    power=power_simulation(sims=power_sims)
    power.to_csv(out/'power_curve.csv',index=False)
    recommended=recommend_sample_size(power)
    recommended.to_csv(out/'power_sample_size.csv',index=False)
    plot_power(power,figs)
    ci=bootstrap_ci(daily)
    ci.to_csv(out/'bootstrap_cpa_confidence_intervals.csv',index=False)
    alloc=allocate(metrics,tests)
    alloc.to_csv(out/'budget_allocation_500k.csv',index=False)
    audit.update({'run_date_utc':str(date.today()),'analysis_type':'DEMONSTRATION — all rows locally generated' if is_demo else 'Externally downloaded, publisher-described SYNTHETIC dataset','budget_usd':BUDGET,'test_families':list(tests),'family_comparison_count':{k:len(v) for k,v in tests.items()},'data_independence_warning':'Campaign-day rows share context and are not random assignments; daily Welch/Fisher do not imply causality.','note':'Sales-only filtered; zero-conversion days omitted from daily CPA tests; selection bias possible.'})
    (out/'data_audit.json').write_text(json.dumps(audit,indent=2,default=str)+'\n')
    strongest=tests['daily_cpa'].iloc[0]
    sig=[f'{r.family}: {r.bh_significant}/{r.tests}' for r in correction.itertuples()]
    context='locally generated test data' if is_demo else 'public synthetic marketing dataset downloaded from Hugging Face'
    heading='DEMO ONLY — NOT A SOURCE-DATA SUBMISSION' if is_demo else 'Educational scenario — synthetic source data, not observed client outcomes'
    grouping_note=audit.get('grouping_strategy','Seven locally simulated platforms')
    exec_memo=f'''# Executive memo — Seven-channel $500,000 marketing decision

**Date:** {date.today()}  
**Prepared for:** CMO, fictional e-commerce business  
**Evidence status:** **{heading}**  
**Source:** {context}  
**Sample window:** {audit['date_min']} through {audit['date_max']}; {len(daily)} channel-days; 7 comparison groups.  
**How seven groups were defined:** {grouping_note}.  
**Source platform count:** {audit.get('observed_platform_count','seven locally generated demo platforms')}.

## Executive recommendation

Retain all seven **comparison groups** (which may be six platforms with one divided into two placements) and use the capped **scenario allocation** below as a *pilot-planning illustration*, not an optimized spend recommendation. Hold back major reallocations until comparable, randomized incremental-lift evidence exists. Aggregate conversion counts measure attributed outcomes rather than causal conversions. The $500K allocation totals exactly $500,000.

## Performance snapshot

{md_table(metrics,['channel','active_days','conversions','spend','revenue','conversion_rate','cpa','roas'],7)}

The dataset's **revenue is a synthetic proxy**. Revenue minus advertising spend is **not profit** because it excludes product costs, refunds, logistics, salaries, and other expenses. Differences in objectives, audiences, mix, attribution, and seasonality can confound cross-channel comparisons.

## Statistical evidence and uncertainty

We tested **21 unordered channel pairs per metric** (63 comparisons across three separately adjusted families). Welch tests compare **daily CPA** and **daily ROAS**, with Cohen's *d* (daily standard deviation); Fisher exact tests compare aggregate conversions vs nonconversions among clicks. For each family, p-values are adjusted by Bonferroni (FWER) and Benjamini–Hochberg (FDR). Independent daily observations and independent clicked-user conversions are simplifying assumptions, potentially violated here. Statistical significance does not establish business or causal significance.

{md_table(correction)}

The lowest raw p-value for daily CPA is **{strongest.group_a} vs {strongest.group_b}** (p={strongest.p_value:.3g}; BH-adjusted p={strongest.p_fdr_bh:.3g}; Cohen's d={strongest.cohens_d:.2f}). This is a comparison, not a treatment effect. Corrections reduce false-discovery claims; they do not prove that any particular raw significant finding was false.

## Power, adequacy, and confidence intervals

Monte Carlo planning assumes independent normal daily CPAs, 15% coefficient of variation, and 350+ replicates depending on invocation. It examines 5%, 10%, 15%, and 20% changes at 30–180 days/channel. These figures are **prospective assumption-driven sensitivity checks**, not observed power calculated from selected significant effects. Autocorrelation, changing campaign mix, and corrected test thresholds may require more days.

{md_table(recommended)}

Channel-specific **95% percentile bootstrap confidence intervals** for the mean of daily CPA (not the ratio-of-totals CPA) are saved in `results/bootstrap_cpa_confidence_intervals.csv`. The bootstrap assumes independent days, so intervals may be optimistic.

## Proposed monthly allocation (illustrative, $500,000)

{md_table(alloc,['channel','monthly_budget_usd','share_pct','cpa','roas'],7)}

Allocation policy: baseline equal-share across 7 observed comparison groups; if at least one of the *daily CPA or ROAS* comparison families retains a BH-significant pair, move cautiously using an exploratory 60% CPA / 40% ROAS rank score, capped at **10–20% budget share per channel**. The score is arbitrary, ignores capacity/saturation, and does not estimate incremental ROAS or marginal CPA. This is a stress-testable proposal, **not a recommendation to execute unchanged**.

## Next steps and limitations

1. Verify pixel tagging, deduplication, conversion windows, and that all channels use comparable sales attribution and costs.
2. Have Finance replace the synthetic proxies with first-party net contribution margin and **incremental** profit.
3. Run a randomized geo or audience holdout with prespecified primary outcome, MDE, fixed horizon, and multiple-testing plan.
4. Track cohort overlap and day/week correlation; use clustered or blocked modeling where appropriate.
5. Re-run power planning using actual baseline variance and holdout design before committing reallocations.

**Data licensing and provenance:** The publisher describes the dataset as synthetic; the Hugging Face dataset license is listed as unknown. This analysis is educational only. See `dataset_review.md` and `results/data_audit.json`.
'''
    (BASE/('executive_memo_demo.md' if is_demo else 'executive_memo.md')).write_text(exec_memo)
    proof=f'''# Lab proof — In God we trust, everyone else bring the data

**Evidence status:** {heading}

**Dataset:** [{SOURCE_URL}]({SOURCE_URL}) (external source used only in `--source hf` mode). Publisher explicitly describes the source as **synthetic**.

## Reproduction

```bash
python run_lab.py --source hf
python -m unittest discover -s tests -v
```

Demonstration mode: `python run_lab.py --source demo`. It writes only `demo_*` artifacts and is **not evidence of a Hugging Face dataset run**.

## Input → output and evidence

- Input: campaign-day marketing columns date, platform, objective, spend, impressions, clicks, conversions, revenue. Restrict to Sales where available; when six platforms are observed, split one actual platform by observed placement into two non-overlapping segments; otherwise select seven observed platforms. Aggregate to segment/day and use a 90-day window or available history as needed.
- Data quality / transformations: [`{'demo_results' if is_demo else 'results'}/data_audit.json`]({'demo_results' if is_demo else 'results'}/data_audit.json)
- Prepared input CSV: [`{'demo_data/marketing_data_demo.csv' if is_demo else 'data/marketing_data.csv'}]({'demo_data/marketing_data_demo.csv' if is_demo else 'data/marketing_data.csv'})
- KPI evidence: [`{'demo_results' if is_demo else 'results'}/channel_metrics.csv`]({'demo_results' if is_demo else 'results'}/channel_metrics.csv)
- Daily CPA tests + Cohen d: [`{'demo_results' if is_demo else 'results'}/daily_cpa_comparisons.csv`]({'demo_results' if is_demo else 'results'}/daily_cpa_comparisons.csv)
- Daily ROAS comparisons: [`{'demo_results' if is_demo else 'results'}/daily_roas_comparisons.csv`]({'demo_results' if is_demo else 'results'}/daily_roas_comparisons.csv)
- Fisher conversion tests: [`{'demo_results' if is_demo else 'results'}/fisher_conversion_comparisons.csv`]({'demo_results' if is_demo else 'results'}/fisher_conversion_comparisons.csv)
- Bonferroni + BH: [`{'demo_results' if is_demo else 'results'}/multiple_comparisons_summary.csv`]({'demo_results' if is_demo else 'results'}/multiple_comparisons_summary.csv)
- Power curve and sample-size plan: [`{'demo_results' if is_demo else 'results'}/power_curve.csv`]({'demo_results' if is_demo else 'results'}/power_curve.csv), [`{'demo_results' if is_demo else 'results'}/power_sample_size.csv`]({'demo_results' if is_demo else 'results'}/power_sample_size.csv)
- Intervals: [`{'demo_results' if is_demo else 'results'}/bootstrap_cpa_confidence_intervals.csv`]({'demo_results' if is_demo else 'results'}/bootstrap_cpa_confidence_intervals.csv)
- Final $500k allocation: [`{'demo_results' if is_demo else 'results'}/budget_allocation_500k.csv`]({'demo_results' if is_demo else 'results'}/budget_allocation_500k.csv)
- Figures: [`{'demo_figures' if is_demo else 'figures'}/`]({'demo_figures' if is_demo else 'figures'}/)
- Executive final output: [`{'executive_memo_demo.md' if is_demo else 'executive_memo.md'}]({'executive_memo_demo.md' if is_demo else 'executive_memo.md'})

## Observed execution

- Source platforms: {audit.get('observed_platform_count',7)}; observed comparison groups: {audit['unique_channels']}; analysis rows: {audit['analysis_rows']}; 21 comparisons/family.
- Grouping method: {grouping_note}.
- Corrected discoveries: {', '.join(sig)}.
- Expected output: reproducible reports, charts, $500k constrained allocation (not actual causal lift).

## Failure / limitation

The first source has an **unknown license** and is explicitly synthetic. It is not measured client performance. Rows are repeated, non-random marketing campaigns, and Fisher's independence assumptions can fail; day-wise Welch p-values ignore serial autocorrelation. Revenue is a proxy; no observational ranking should be interpreted as a causal uplift estimate. A real-client validation dataset and randomized incrementality test are prerequisites for acting on this budget.
'''
    (BASE/('lab_proof_demo.md' if is_demo else 'lab_proof.md')).write_text(proof)
    print(f'Completed {source} analysis: {len(daily)} channel-days, 7 observed comparison groups, 21 comparisons per family. Output: {out}')
    print(f'Budget sum: ${alloc.monthly_budget_usd.sum():,.0f}; corrected significance: {sig}')
    return {'audit':audit,'metrics':metrics,'tests':tests,'allocation':alloc,'power':power}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',choices=('hf','demo'),default='hf')
    parser.add_argument('--power-sims',type=int,default=350)
    arg=parser.parse_args()
    run(arg.source,arg.power_sims)
