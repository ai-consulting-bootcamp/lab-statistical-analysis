# Reflection

**LAB | In God we trust, everyone else bring the data**
**Author:** Nnanyelugo Ahukannah

## What surprised me

That almost everything was significant, and that this made the p-values close to
useless. Fourteen of fifteen cost comparisons and thirteen of fifteen conversion
comparisons cleared p&lt;0.05, most of them at machine zero. With six to
twenty-two thousand impressions per campaign, significance stops discriminating
&mdash; it tells you the sample is large, which you already knew. **Six of the
fourteen significant cost differences had a negligible effect size.** If I had
reported only the test results, I would have handed over fourteen "real"
differences, six of which are not worth a meeting.

The second surprise was in the opposite direction. The two campaigns that were
*not* significantly different turned out to be the most useful finding in the set:
B and E are statistically indistinguishable, and so are C and D. That converts a
ranked list of six into two strong campaigns and two weak ones, which is a much
more honest thing to give a stakeholder than an ordering that implies precision
the data does not have.

## How multiple comparisons correction changed my conclusions

Once, and only once &mdash; which turned out to be more instructive than either
"not at all" or "a lot". On the conversion and cost-per-impression families,
Bonferroni and Benjamini-Hochberg withdrew nothing, because a correction only
bites when p-values sit near the threshold and at this sample size they sit at
zero. But on **CPA**, compared by bootstrap, the two methods disagreed:
Campaign E against Campaign F is significant on its own (p=0.042), survives
Benjamini-Hochberg, and fails Bonferroni (p=0.63). Their bootstrap intervals
overlap, and the honest reading is that the two campaigns have comparable
acquisition costs.

That is a textbook illustration of the difference between the two corrections.
Bonferroni controls the chance of *any* false positive and is brutal about it;
Benjamini-Hochberg controls the expected *proportion* of false discoveries and
keeps more. Which one you want depends on the cost of being wrong, and for a
budget decision worth five figures I would take the conservative reading.

Reporting "no change" alone would have been true but would have taught me
nothing, so I re-ran the same fifteen conversion tests on a realistic pilot-sized
subsample of 400 impressions per campaign. There, seven comparisons were
significant uncorrected, six survived Benjamini-Hochberg, and only four survived
Bonferroni &mdash; three specific pairs were withdrawn. That is the regime most
real marketing tests live in, and it is where running fifteen comparisons without
correction would have produced confident nonsense.

The practical lesson is about ordering: correction protects you from the
threshold, and effect size protects you from the sample size. They guard
different failures, and the big sample removed the first problem while making the
second one much worse.

## Limitations

The one that constrains everything is that this is **observational data, not an
experiment**. Campaigns were not randomly assigned to audiences, so every
difference is confounded with who each campaign reaches. I can say Campaign B
converted at 8.3%; I cannot say that budget moved into it would convert at 8.3%.
Every recommendation in the memo is therefore framed as a bounded test rather
than a reallocation.

Beyond that: the cost column is anonymised, so no figure can be expressed in
money; ROAS is not computable at all from the real data, because ad revenue is
commercially sensitive and effectively never published, which is why that one
metric comes from a clearly-labelled synthetic set; and the window is a single
30 days on a single ad network. I also deliberately did not test `cpo`, which
looked like an attractive continuous outcome until I checked and found it takes
only 8 to 510 distinct values per campaign &mdash; it is a campaign-period
attribute repeated down the rows, and t-testing it would have treated a few dozen
real observations as tens of thousands.

## Communicating this to non-technical stakeholders

Lead with the decision, not the method. The memo opens with "shift budget toward
two campaigns and test rather than assume", and the statistics appear underneath
as support. I would not say "p &lt; 0.001" out loud; I would say the gap is far
wider than the range of uncertainty, and show the confidence intervals as error
bars, because a bar with a whisker communicates precision without anyone needing
to know what a null hypothesis is.

The hardest thing to convey is the one that matters most: **significant does not
mean big, and observational does not mean causal.** For the first I would use the
comparison directly &mdash; six differences that pass the test and are still too
small to act on. For the second I would avoid the word "causal" entirely and put
it as a question: *would this campaign still convert at 8% if we pointed it at
the other campaign's audience?* Nothing in the data answers that, and framing it
as a question invites the right response &mdash; run the test &mdash; rather than
sounding like a statistician hedging.
