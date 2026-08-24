# Reflection

**What surprised you about the results?**
How cleanly the `total_ads` comparisons split into "statistically significant" (19 of 21, both
before and after correction) while every single one had a negligible Cohen's d. It's one thing
to be told large samples inflate significance; it's another to see 90% of a comparison family
clear a corrected p-value threshold while the effect sizes sit at |d| < 0.1 across the board.
Multiple comparisons correction did essentially nothing to that family — it took checking effect
size, not just correcting p-values, to catch it.

**How did multiple comparisons correction change your conclusions?**
Less than expected, and that itself was the lesson. With ~80,000 users per day-of-week group,
Bonferroni only knocked the `total_ads` family down from 19 to 16 significant pairs, and FDR
barely moved it (19 to 19). At smaller sample sizes correction usually does the heavy lifting;
here, sample size alone was already enough to make almost everything "significant," so effect
size review had to do the work correction couldn't.

**What are the limitations of this analysis?**
The biggest one is structural: this dataset has no cost or revenue data, so CPA and ROAS —
the metrics the lab scenario is actually built around — could not be computed at all. The
day-of-week grouping is also correlational, not from a randomized experiment, so confounding by
campaign timing or audience mix can't be ruled out, unlike the `ad` vs. `psa` comparison which
is a real randomized test. Power analysis relied on a normal/binomial simulation model rather
than the real (heavily right-skewed) `total_ads` distribution.

**How would you communicate these findings to non-technical stakeholders?**
Lead with the one number that matters most and is causally trustworthy: showing real ads instead
of a PSA lifts conversion by about 30%, and that result is extremely unlikely to be chance. Then
frame the day-of-week finding as a scheduling tweak, not a budget reallocation — "shift ad
delivery weight toward Monday and Tuesday" is concrete and actionable without requiring
stakeholders to parse p-values or Cohen's d. Explicitly flag that "more ads shown doesn't mean
more revenue" here — the ad-exposure findings, despite being statistically significant, aren't a
lever to pull, since we don't know what those ads cost or returned.
