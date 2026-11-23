# Reflection

## 1. What surprised me about the results?

- abc had the lowest CPA ($0.21), highest ROAS (268x), and highest conversion rate (41.8%), but its total cost was only $131.66 over 91 days. It had CPA on just 22 days.
- The ROAS values ranged from 92x to 268x. I would use them to compare placements, not as a forecast of incremental profit.
- Fisher's exact test called the 0.7 percentage-point gap between ghi and jkl significant. The daily conversion-rate test did not, which shows how much the test unit matters.
- The rank formula assigned jkl 26.7% of the $500,000 budget even though its CPA difference from ghi and mno was not significant.

## 2. How did multiple-comparison correction change my conclusions?

- There were 23 uncorrected significant results among 30 tests. Bonferroni retained 20 and BH retained all 23.
- Bonferroni removed def vs ghi and def vs jkl for daily CPA, plus ghi vs mno for daily conversion rate. BH removed none.
- I would use Bonferroni for the final budget move because a false winner could send real money to a channel that is not better. I would use BH while exploring and shortlisting channels to test.
- The results still support moving money away from def, while the CPA ranking among ghi, jkl, and mno is not supported.

## 3. What are the limitations of this analysis?

- I have data from one advertiser and three months in 2020. Daily totals also hide the campaign, banner, and engagement mix within each placement.
- Post-click sales are attributed to ads, but that does not prove the ads caused the sales. Fisher's test also treats clicks as independent, even though clicks on the same day may share conditions.
- The power model assumes daily CPA spread is 15% of the mean. The observed CV is about 45% to 63%, so the simulated power is too high.
- The composite score does not account for statistical significance or channel scale. abc has CPA data on only 22 days, and the formula gives it 33.3% of the budget.

## 4. How would I explain the findings to a non-technical CMO in one minute?

"I would move budget away from def, which has the highest cost per sale, and keep ghi, jkl, and mno as the established group. abc looks unusually efficient, but it spent only about $132 in three months and had CPA data on 22 days, so I would test it with small, capped increases. This data covers one advertiser and three months, and it cannot prove that the ads caused every recorded sale. I would scale abc only if its cost per sale holds as spend rises."
