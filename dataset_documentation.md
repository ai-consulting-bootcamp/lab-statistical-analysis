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

The two-sided Welch tests use one daily ratio per campaign and test equality of campaign means. Effects and confidence intervals are reported as B minus A. Cohen's *d* uses the difference divided by the square root of the average of the two sample variances. Matching on day in a paired t-test checks sensitivity to common calendar shocks. Serial dependence remains a limitation of both tests. The CPA intervals include an ordinary percentile bootstrap for the daily mean and a seven-day moving-block bootstrap for aggregate CPA.

Fisher's exact test uses clicks with a credited conversion versus other clicks, pooled across the observation period. Its odds ratio is A over B. Its Cohen's *d* uses Bernoulli variances. Fisher tests the pooled click-weighted rate and can overstate precision if clicks from repeat users or shared delivery conditions are dependent. Daily Welch and paired tests treat calendar days as the comparison unit and target average daily rates. A numeric zero in the Fisher p-value exports denotes floating-point underflow. The full Fisher table flags these cases and reports raw p-values on a log10 scale.

Bonferroni and Benjamini–Hochberg (BH) are applied separately to the 21 comparisons in each primary family and to the paired sensitivity families. Bonferroni controls family-wise error within a family. BH is used for exploratory ranking and assumes independence or suitable positive dependence for its standard FDR guarantee. Pairwise tests share campaigns, so the guarantee cannot be established from these comparisons alone.

The planning model simulates future independent daily CPA observations with 15% SD relative to baseline CPA, two-sided Welch tests, and a lower bound at 50% of baseline. Minimum sample sizes use the equal-variance noncentral-*t* reference with simulations as a check. A campaign's actual day-to-day variation can be larger. These estimates describe prospective designs under stated assumptions.
