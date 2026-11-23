# Reflection

## 1. What surprised me about the results?
How **similar** the six channels are. Every channel has a CPA of about $282–$285, a ROAS of about 6.0 and a conversion rate of about 8%, and the day-to-day noise (std about $24) is seven times bigger than the gap between the best and worst channel. The bigger surprise was that the **same conversion-rate data gave opposite answers** depending on the test: Fisher's exact test found 9 of 15 pairs "significant", while the t-test on daily rates found 0. The differences were only 0.01–0.06 percentage points. That showed me that with millions of observations, almost anything becomes significant. Finally, the first p-value heatmap (using the colour map from the hint) made non-significant pairs look red, so a chart can mislead even when the numbers are right.

## 2. How did multiple comparisons correction change my conclusions?
Less than I expected, but it confirmed the conclusion. We ran **45 tests**, so about 2 false positives were expected by chance. For CPA there was nothing to correct: 0 significant results before and after. For conversion rate, Bonferroni removed 2 of the 9 Fisher results (Email vs Google Ads and Google Ads vs Instagram) and BH removed none. The main lesson: **correction protects against false winners, but it does not fix tiny effects.** The surviving Fisher results are still too small to matter. For a budget decision I would use Bonferroni, because a false winner is expensive.

## 3. What are the limits of this analysis?
- The dataset is very likely **synthetic**, so the channels may be similar by construction.
- **Conversions and revenue were derived** (conversion rate × clicks; cost × (1 + ROI)), not observed.
- **Historical data shows correlation, not causation**: we do not know how many conversions each channel actually *caused* (incrementality).
- We ignored seasonality, campaign mix, audience, location and attribution.
- The power simulation assumes normal, stable daily CPA.
- We cannot see **diminishing returns**: a channel's CPA might rise if it got much more budget.

## 4. How would I explain the findings to a non-technical CMO in one minute?
"We checked a full year of data to see if any channel is a better use of money. The answer is no: every channel costs about the same per customer (around $284) and brings back about six times its cost. The small differences we see are the kind you'd get from day-to-day luck, and our data was big enough that a real difference of 5% or more would have shown up. So I would not move budget based on this. Instead, let's keep the split even and run a proper experiment, for example by pausing a channel in some regions, to measure which channel really brings extra sales. That gives us an answer we can bet $500K a month on."
