# Executive memo — Seven-channel $500,000 marketing decision

**Date:** 2026-11-21  
**Prepared for:** CMO, fictional e-commerce business  
**Evidence status:** **Educational scenario — synthetic source data, not observed client outcomes**  
**Source:** public synthetic marketing dataset downloaded from Hugging Face  
**Sample window:** 2025-10-03 through 2025-12-31; 305 channel-days; 7 comparison groups.  
**How seven groups were defined:** Six actual platforms; one split into two observed, mutually exclusive placement segments (seven allocation groups, NOT seven platforms).  
**Source platform count:** 6.

## Executive recommendation

Retain all seven **comparison groups** (which may be six platforms with one divided into two placements) and use the capped **scenario allocation** below as a *pilot-planning illustration*, not an optimized spend recommendation. Hold back major reallocations until comparable, randomized incremental-lift evidence exists. Aggregate conversion counts measure attributed outcomes rather than causal conversions. The $500K allocation totals exactly $500,000.

## Performance snapshot

                channel  active_days  conversions    spend    revenue  conversion_rate        cpa      roas
          Google Search           51        13375 47996.92 1181333.02         0.046548   3.588555 24.612684
            Meta | Feed           35         1277 23935.10   92167.69         0.023675  18.743226  3.850733
Meta | other placements           37         1245 25172.71   82150.61         0.022076  20.219044  3.263479
               Snapchat           45         1593 34474.04   87750.07         0.015396  21.640954  2.545396
                 TikTok           54         1683 38096.47   99940.33         0.017673  22.636049  2.623349
         Google Display           29          409 15517.18   28268.49         0.010129  37.939315  1.821754
               LinkedIn           54          141 47276.44   24603.58         0.008669 335.293901  0.520419

The dataset's **revenue is a synthetic proxy**. Revenue minus advertising spend is **not profit** because it excludes product costs, refunds, logistics, salaries, and other expenses. Differences in objectives, audiences, mix, attribution, and seasonality can confound cross-channel comparisons.

## Statistical evidence and uncertainty

We tested **21 unordered channel pairs per metric** (63 comparisons across three separately adjusted families). Welch tests compare **daily CPA** and **daily ROAS**, with Cohen's *d* (daily standard deviation); Fisher exact tests compare aggregate conversions vs nonconversions among clicks. For each family, p-values are adjusted by Bonferroni (FWER) and Benjamini–Hochberg (FDR). Independent daily observations and independent clicked-user conversions are simplifying assumptions, potentially violated here. Statistical significance does not establish business or causal significance.

           family  tests  expected_false_positives_under_all_nulls  uncorrected_significant  bonferroni_significant  bh_significant  bonferroni_alpha
        daily_cpa     21                                      1.05                       15                      15              15          0.002381
       daily_roas     21                                      1.05                       18                      16              18          0.002381
fisher_conversion     21                                      1.05                       19                      19              19          0.002381

The lowest raw p-value for daily CPA is **Google Search vs TikTok** (p=2.44e-18; BH-adjusted p=5.13e-17; Cohen's d=2.40). This is a comparison, not a treatment effect. Corrections reduce false-discovery claims; they do not prove that any particular raw significant finding was false.

## Power, adequacy, and confidence intervals

Monte Carlo planning assumes independent normal daily CPAs, 15% coefficient of variation, and 350+ replicates depending on invocation. It examines 5%, 10%, 15%, and 20% changes at 30–180 days/channel. These figures are **prospective assumption-driven sensitivity checks**, not observed power calculated from selected significant effects. Autocorrelation, changing campaign mix, and corrected test thresholds may require more days.

 effect_size_pct  minimum_tested_days_for_80pct_power  n_90_days_sufficient
             5.0                                  180                 False
            10.0                                   60                  True
            15.0                                   30                  True
            20.0                                   30                  True

Channel-specific **95% percentile bootstrap confidence intervals** for the mean of daily CPA (not the ratio-of-totals CPA) are saved in `results/bootstrap_cpa_confidence_intervals.csv`. The bootstrap assumes independent days, so intervals may be optimistic.

## Proposed monthly allocation (illustrative, $500,000)

                channel  monthly_budget_usd  share_pct        cpa      roas
          Google Search               85714    17.1428   3.588555 24.612684
            Meta | Feed               80952    16.1904  18.743226  3.850733
Meta | other placements               76191    15.2382  20.219044  3.263479
               Snapchat               69524    13.9048  21.640954  2.545396
                 TikTok               68571    13.7142  22.636049  2.623349
         Google Display               61905    12.3810  37.939315  1.821754
               LinkedIn               57143    11.4286 335.293901  0.520419

Allocation policy: baseline equal-share across 7 observed comparison groups; if at least one of the *daily CPA or ROAS* comparison families retains a BH-significant pair, move cautiously using an exploratory 60% CPA / 40% ROAS rank score, capped at **10–20% budget share per channel**. The score is arbitrary, ignores capacity/saturation, and does not estimate incremental ROAS or marginal CPA. This is a stress-testable proposal, **not a recommendation to execute unchanged**.

## Next steps and limitations

1. Verify pixel tagging, deduplication, conversion windows, and that all channels use comparable sales attribution and costs.
2. Have Finance replace the synthetic proxies with first-party net contribution margin and **incremental** profit.
3. Run a randomized geo or audience holdout with prespecified primary outcome, MDE, fixed horizon, and multiple-testing plan.
4. Track cohort overlap and day/week correlation; use clustered or blocked modeling where appropriate.
5. Re-run power planning using actual baseline variance and holdout design before committing reallocations.

**Data licensing and provenance:** The publisher describes the dataset as synthetic; the Hugging Face dataset license is listed as unknown. This analysis is educational only. See `dataset_review.md` and `results/data_audit.json`.
