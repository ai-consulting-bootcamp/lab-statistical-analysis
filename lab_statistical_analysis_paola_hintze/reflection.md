# Reflection

## What surprised me?

Referral did not merely lead one metric; it was the only channel with clearly positive attributed profit and it led conversion rate, aggregate CPA, and ROAS. More surprising was how benign the weak channels looked when CPA was calculated only on successful days. Outbound Sales has an aggregate CPA of $3,785.71, yet its mean CPA across three conversion-positive days is $230.67. This shows why the estimand and missing-data mechanism matter as much as the p-value.

## How did correction change the conclusion?

With 42 pairwise tests, 2.10 false positives are expected at α=.05 if all null hypotheses hold. BH removed the uncorrected Outbound Sales–Partnerships CPA result (`p=.0397` → adjusted `p=.0555`). Bonferroni retained fewer results than BH in both test families. Correction did not change the main Referral conclusion, but it prevented me from treating every nominally significant contrast as equally reliable.

## Limitations

The dataset is synthetic, covers one company for only 90 days, and reports attributed rather than incremental revenue. Channels share calendar conditions, while the required pairwise tests treat observations as independent. Daily CPA is undefined on zero-conversion days and is highly sparse for several channels. Fisher aggregation ignores date and traffic-mix changes. Power analysis follows a simplified normal model whose 15% standard-deviation assumption does not match all empirical distributions. The ranking also assumes historical average performance will scale, which can fail under auction inflation or audience saturation.

## Communicating to non-technical stakeholders

I would lead with the decision boundary: “Referral deserves the largest controlled increase, but this is a test allocation, not proof of causal ROI.” I would show the budget chart, distinguish aggregate efficiency from conditional CPA tests, and explain correction as protection against finding winners by chance when comparing many pairs. I would avoid saying “statistically proven,” give absolute rates and dollars alongside adjusted p-values/effect sizes, and state the monitoring and stop rules before discussing methodological detail.

