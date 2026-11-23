# Reflection

**1. What surprised you about the results?**
How similar the six channels are. Looking only at the totals, Facebook "wins" on CPA, ROAS, conversion rate and profit, and a simple ranking would give it almost six times Instagram's budget. But the whole CPA spread is about 5%, and none of the CPA differences survives a proper test. I was also surprised that Fisher's test called 8 pairs "significant" for gaps of 0.05 percentage points — with 8 million clicks per channel, almost anything becomes significant.

**2. How did multiple-comparison correction change your conclusions?**
Before correction I had 14 "significant" results out of 45 tests; with 45 tests about 2 false positives are expected by chance. After Bonferroni or BH, the only CPA result (Instagram vs Website) and all daily conversion-rate results disappeared. That changed the conclusion from "Website is cheaper than Instagram" to "we can't say any channel is cheaper".

**3. What are the limits of this analysis?**
- The data looks simulated, and conversions and revenue are derived, not measured.
- The power simulation uses a 15% daily spread, but the real spread is 35–96%, so the real detectable effect is 2–3× larger than the simulation says.
- Daily CPA has strong outliers (days with few conversions), which push the mean up and make the t-tests noisier.
- No information on seasonality, attribution, audience overlap or whether a channel can absorb more budget at the same CPA.
- The composite score ranks channels even when their differences aren't significant, so it creates false precision.

**4. How would you explain the findings to a non-technical CMO in one minute?**
"All six channels cost about the same per customer — around $50 — and the differences we see are small enough to be luck. If we move money based on these numbers, we're as likely to be chasing noise as finding a better channel. My recommendation is to keep the budget evenly split for now and run a proper test on the two or three channels where a decision would really change our spend. If one of them is really at least 10% cheaper, that test will show it."
