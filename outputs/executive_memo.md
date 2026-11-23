# Executive memo — Marketing budget allocation

**To** CMO  
**From** Marketing Analytics  
**Date** 2026-11-23  
**Dataset** Synthetic SaaS Growth Pack, AlphaFlow  
**Period** 2026-01-01 to 2026-03-31

## Executive summary

Use the $500,000 allocation as a starting point for a controlled budget test.
The CPA and ROAS ranking assigns the largest proposed share to Referral
at $123,148 (24.6%).

## Key findings

- 2 daily CPA comparisons remained significant after BH. The pair with the lowest adjusted p-value was Referral versus SEO. The mean daily CPA gap was $262.13 (adjusted p = 5.56e-15).
- 14 pooled conversion rate comparisons remained significant after BH. The pair with the lowest adjusted p-value showed Referral ahead of Paid Search by 2.94 percentage points (adjusted p = 3.15e-12).
- For a 5% CPA difference, the simulation estimated
  140 usable days per channel for 80% power.
  The smallest channel sample had 1 usable days.

## Proposed monthly allocation

- Referral: $123,148 (24.6%)
- SEO: $105,556 (21.1%)
- Partnerships: $70,370 (14.1%)
- Content: $61,574 (12.3%)
- Outbound Sales: $61,574 (12.3%)
- Paid Search: $52,778 (10.6%)
- LinkedIn Ads: $25,000 (5.0%)

## Statistical caveats

- The data are synthetic. Historical attributed revenue can reflect audience mix,
  seasonality and attribution rules.
- BH was applied within each test family. The budget ranks also distinguish
  channels with small or uncertain differences.
- Bootstrap intervals describe mean daily CPA on days with conversions.
  Budget ranks use total CPA, which includes spend on days without conversions.
- The power estimate assumes independent days, 15% relative daily CPA variation
  and a 5% threshold for a single test.

## Next steps

Set a minimum worthwhile improvement before the test. Increase spend in stages,
use a control group where feasible, and measure incremental conversions and
the cost per additional conversion before scaling.
