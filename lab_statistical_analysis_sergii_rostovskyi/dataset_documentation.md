# Dataset and methods

## Selection

| Candidate | Assessment |
| --- | --- |
| [Sales Conversion Optimization, Kaggle](https://www.kaggle.com/datasets/loveall/clicks-conversion-tracking) | The inspected CSV had 1,143 ads across three campaigns, with spend and approved conversions. Seventy-two ads had more approved conversions than clicks, and the file had no dates. This limited post-click comparison and day-level power analysis. |
| [Criteo Attribution Modeling for Bidding Dataset, Hugging Face](https://huggingface.co/datasets/criteo/criteo-attribution-dataset) | The selected dataset contains anonymized, subsampled live display advertising traffic, with one row per impression. Timestamped impressions, clicks, conversion IDs, attribution flags, and transformed display costs support seven campaign-level comparisons over the same observation period. |

The source is Criteo AI Lab's [public dataset release](https://ailab.criteo.com/criteo-attribution-modeling-bidding-dataset/). The [gzip archive](https://huggingface.co/datasets/criteo/criteo-attribution-dataset/resolve/main/criteo_attribution_dataset.tsv.gz) is 653,015,824 bytes. Its published SHA-256 is recorded in [the data audit](data/data_quality.json) and verified by the source build.

Eustache Diemert, Julien Meynet, Pierre Galland, and Damien Lefortier. *Attribution Modeling Increases Efficiency of Bidding in Display Advertising*. AdKDD & TargetAd Workshop, 2017. [Paper](https://arxiv.org/abs/1707.06409).

The derived campaign-day data are distributed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/). Changes include column selection, validation, attribution deduplication, conversion assignment, and daily aggregation. The analysis and budget scenario are for educational use.

## Preparation and quality

- The archive contains 16,468,027 impression records, 22 fields, and 675 observed campaign IDs. The eight fields used in analysis had no missing values, invalid binary flags, or invalid base rows. The publisher's headline conversion count and the rule-specific count below differ. All reported results use the pinned archive and the explicit attribution rule.
- A conversion is credited once across the full log. Eligible rows have `click=1`, `conversion=1`, `attribution=1`, a nonnegative conversion ID, and a conversion timestamp at or after the click. The most recent eligible click receives the credit. Across campaigns, a tie at the latest second would exclude the ID. The audit found zero such IDs and counted 236,331 IDs under this rule across the full archive.
- The observation unit is one campaign on one elapsed 86,400-second day. Conversion credit is assigned to the click's day, so the daily click denominator and conversion numerator use the same cohort rule. Days 0–29 cover the full observed intervals. Day 30 was partial and was dropped from the campaign-day output. The source provides relative timestamps.
- The seven highest-impression campaigns among those present on all 30 included days were selected using traffic volume alone. The resulting 210 campaign-day rows have no missing metrics or zero-conversion days. Because the release lacks a standalone impression ID, records with equal analyzed fields were retained as impressions. The exported CSV contains campaign-day aggregates.
- Valid extremes were retained. The [distribution summary](tables/group_variability.csv) reports standard deviations, ranges, interquartile ranges, and counts beyond 1.5 interquartile ranges. Campaign 5061834 has the largest absolute daily CPA standard deviation (0.02049 cost units). Campaign 30801593 has the largest relative daily CPA variation (35.2%). Campaign 15184511 has the most variable daily post-click conversion rate (2.36 percentage points SD), with a high day at 17.41%.

## Metrics and inference

| Metric | Definition |
| --- | --- |
| CTR | Clicks divided by impressions |
| Attributed post-click CVR | Unique credited conversions divided by clicks |
| CPA | Transformed display costs divided by unique credited conversions |
| ROAS, profit, and profit margin | Unavailable because the release has no observed sales revenue and the cost-per-order field is transformed. |

Aggregate metrics are ratios of summed numerators and denominators. Daily means weight each day equally. Zero denominators produce missing ratios. Campaign spend and CPA are in transformed cost units. Only the hypothetical budget table uses dollars.

### Step 4 — Primary CPA comparison

The primary two-sided Welch t-tests compare the mean of daily CPA ratios between campaigns. One observation is one campaign-day ratio: that day's transformed display cost divided by its credited conversions. Every valid day has equal weight in its campaign's comparison mean. This is different from aggregate CPA, calculated as total transformed cost divided by total credited conversions; aggregate CPA weights days according to their credited conversion counts.

Review the complete [primary CPA pairwise results](tables/cpa_pairwise.csv) and the [CPA p-value heatmap](figures/metric_comparison_heatmap.png). The table includes raw p-values, Bonferroni and Benjamini–Hochberg decisions, effect sizes, and same-day paired statistics. Heatmap cells display raw p-values; their colors use the CPA family's Bonferroni threshold and unadjusted 0.05 threshold. Same-day paired CPA t-tests are sensitivity checks for common calendar shocks and are not the primary Step 4 test.

The daily conversion-rate Welch tests appear separately in [their pairwise table](tables/daily_conversion_rate_pairwise.csv). The pooled-click Fisher exact tests are also separate in [their pairwise table](tables/fisher_conversion_rate_pairwise.csv); these test a click-weighted rate and do not replace the Step 4 CPA deliverable. Serial dependence remains a limitation of the daily tests. CPA intervals include an ordinary percentile bootstrap for the daily mean and a seven-day moving-block bootstrap for aggregate CPA.

Fisher's exact test uses clicks with a credited conversion versus other clicks, pooled across the observation period. Its odds ratio is A over B. Its Cohen's *d* uses Bernoulli variances. Fisher tests the pooled click-weighted rate and can overstate precision if clicks from repeat users or shared delivery conditions are dependent. Daily Welch and paired tests treat calendar days as the comparison unit and target average daily rates. A numeric zero in the Fisher p-value exports denotes floating-point underflow. The full Fisher table flags these cases and reports raw p-values on a log10 scale.

Bonferroni and Benjamini–Hochberg (BH) are applied separately to the 21 comparisons in each primary family and to the paired sensitivity families. Bonferroni controls family-wise error within a family. BH is used for exploratory ranking and assumes independence or suitable positive dependence for its standard FDR guarantee. Pairwise tests share campaigns, so the guarantee cannot be established from these comparisons alone.

The planning model simulates future independent daily CPA observations with a shared default SD of 15% of baseline CPA and two-sided Welch tests. For each arm, simulated CPA values are clipped symmetrically around that arm's mean, using the same half-width of 50% of baseline CPA: `clip(value, arm_mean - 0.50 × base_cpa, arm_mean + 0.50 × base_cpa)`. This is the chosen interpretation of the assignment's ambiguous instruction to “cap at 50% of base”; it applies the same symmetric bound width to both arms rather than imposing a one-sided floor. The arm means are `base_cpa` and `base_cpa × (1 + true_diff_pct)`.

Power curves use 8,000 seeded simulations per effect and sample-size combination, with effect gaps of 5%, 10%, 15%, and 20%, and sample sizes of 30, 60, 90, 120, and 180 days per arm. At the 30 observed days, empirical power is 24.2%, 72.4%, 97.3%, and 100.0% for those gaps. The 90-day hypothetical scenario estimates 60.8%, 99.5%, 100.0%, and 100.0%. The 80% minimum sample sizes are equal-variance noncentral-*t* reference-model estimates of 143, 37, 17, and 10 days per arm; empirical power at those sizes is 80.5%, 81.1%, 80.7%, and 79.7%, respectively. The final value is below 80% as calculated. The per-pair assessment makes the same distinction: 21 BH-significant pairs have empirical power of 98.25% to 100.0% at the 30 observed days, while empirical power at their reference-model minimum sizes ranges from 72.2% to 100.0%, with four estimates below 80%. Thirty days are the observed campaign period; 90 days is a hypothetical future planning scenario, not observed data. Campaign-level variability may exceed the shared 15% planning SD, and actual delivery may change over time.
