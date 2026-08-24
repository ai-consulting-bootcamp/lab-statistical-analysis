import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind, fisher_exact, false_discovery_control
from itertools import combinations

df = pd.read_csv('data/marketing_data_cleaned.csv')

channels = df['Channel_Used'].unique()
metric = 'Conversion_Rate'

results = []
for a, b in combinations(channels, 2):
    data_a = df[df['Channel_Used'] == a][metric].dropna()
    data_b = df[df['Channel_Used'] == b][metric].dropna()

    t_stat, p_val = ttest_ind(data_a, data_b)

    mean_a, mean_b = data_a.mean(), data_b.mean()
    diff = mean_b - mean_a
    pct_diff = (diff / mean_a) * 100

    pooled_std = np.sqrt((data_a.var() + data_b.var()) / 2)
    cohens_d = diff / pooled_std

    if abs(cohens_d) < 0.2:
        effect = 'negligible'
    elif abs(cohens_d) < 0.5:
        effect = 'small'
    elif abs(cohens_d) < 0.8:
        effect = 'medium'
    else:
        effect = 'large'

    results.append({
        'group_a': a, 'group_b': b,
        'mean_a': round(mean_a, 4), 'mean_b': round(mean_b, 4),
        'diff': round(diff, 4), 'pct_diff': round(pct_diff, 2),
        't_stat': round(t_stat, 4), 'p_value': p_val,
        'cohens_d': round(cohens_d, 4), 'effect_size': effect,
        'significant': p_val < 0.05
    })

ttest_results = pd.DataFrame(results)
print(ttest_results)
print(f"\nTotal comparisons: {len(ttest_results)}")
print(f"Significant at 0.05: {ttest_results['significant'].sum()}")

# Heatmap of p-values
matrix = pd.DataFrame(1.0, index=channels, columns=channels)
for r in results:
    matrix.loc[r['group_a'], r['group_b']] = r['p_value']
    matrix.loc[r['group_b'], r['group_a']] = r['p_value']

fig, ax = plt.subplots(figsize=(8, 6))
im = ax.imshow(matrix.values, cmap='RdYlGn_r', vmin=0, vmax=1)
ax.set_xticks(range(len(channels)))
ax.set_yticks(range(len(channels)))
ax.set_xticklabels(channels, rotation=45, ha='right')
ax.set_yticklabels(channels)

for i in range(len(channels)):
    for j in range(len(channels)):
        ax.text(j, i, f"{matrix.values[i,j]:.2f}", ha='center', va='center', fontsize=8)

plt.colorbar(im, label='p-value')
plt.title('Conversion Rate: P-value Heatmap')
plt.tight_layout()
plt.savefig('metric_comparison_heatmap.png', dpi=150)
plt.close()
print("Saved metric_comparison_heatmap.png")

# Derive conversion counts for Fisher's exact test
df['Conversions'] = (df['Clicks'] * df['Conversion_Rate']).round().astype(int)

fisher_summary = df.groupby('Channel_Used').agg(
    total_conversions=('Conversions', 'sum'),
    total_clicks=('Clicks', 'sum')
)
fisher_summary['non_conversions'] = fisher_summary['total_clicks'] - fisher_summary['total_conversions']
fisher_summary['rate'] = fisher_summary['total_conversions'] / fisher_summary['total_clicks']
print(fisher_summary)

fisher_results = []
for a, b in combinations(channels, 2):
    conv_a = fisher_summary.loc[a, 'total_conversions']
    nonconv_a = fisher_summary.loc[a, 'non_conversions']
    conv_b = fisher_summary.loc[b, 'total_conversions']
    nonconv_b = fisher_summary.loc[b, 'non_conversions']

    table = [[conv_a, nonconv_a], [conv_b, nonconv_b]]
    odds_ratio, p_val = fisher_exact(table, alternative='two-sided')

    rate_a = conv_a / (conv_a + nonconv_a)
    rate_b = conv_b / (conv_b + nonconv_b)
    diff = rate_b - rate_a
    pct_diff = (diff / rate_a) * 100

    fisher_results.append({
        'group_a': a, 'group_b': b,
        'rate_a': round(rate_a, 4), 'rate_b': round(rate_b, 4),
        'diff': round(diff, 4), 'pct_diff': round(pct_diff, 2),
        'odds_ratio': round(odds_ratio, 4), 'p_value': p_val,
        'significant': p_val < 0.05
    })

fisher_df = pd.DataFrame(fisher_results)
print(fisher_df)
print(f"\nTotal comparisons: {len(fisher_df)}")
print(f"Significant at 0.05: {fisher_df['significant'].sum()}")

fig, ax = plt.subplots(figsize=(8, 5))
sorted_summary = fisher_summary.sort_values('rate', ascending=True)
bars = ax.barh(sorted_summary.index, sorted_summary['rate'])
for bar, rate in zip(bars, sorted_summary['rate']):
    ax.text(bar.get_width() + 0.0002, bar.get_y() + bar.get_height()/2,
             f"{rate*100:.2f}%", va='center', fontsize=9)
ax.set_xlabel('Conversion Rate')
ax.set_title('Conversion Rate by Channel (derived from clicks)')
plt.tight_layout()
plt.savefig('rate_comparison.png', dpi=150)
plt.close()
print("Saved rate_comparison.png")

# Multiple comparisons problem
total_comparisons = len(ttest_results) + len(fisher_df)
expected_false_positives = total_comparisons * 0.05
print(f"Total comparisons: {total_comparisons}")
print(f"Expected false positives at alpha=0.05: {expected_false_positives:.2f}")

# Bonferroni correction
alpha = 0.05
alpha_bonf_ttest = alpha / len(ttest_results)
alpha_bonf_fisher = alpha / len(fisher_df)

ttest_results['significant_bonferroni'] = ttest_results['p_value'] < alpha_bonf_ttest
fisher_df['significant_bonferroni'] = fisher_df['p_value'] < alpha_bonf_fisher

print(f"\nBonferroni alpha (t-test): {alpha_bonf_ttest:.6f}")
print(f"Significant after Bonferroni (t-test): {ttest_results['significant_bonferroni'].sum()}")
print(f"Bonferroni alpha (Fisher): {alpha_bonf_fisher:.6f}")
print(f"Significant after Bonferroni (Fisher): {fisher_df['significant_bonferroni'].sum()}")
print(fisher_df[fisher_df['significant_bonferroni']][['group_a','group_b','p_value']])

# Benjamini-Hochberg FDR correction
ttest_results['p_value_fdr'] = false_discovery_control(ttest_results['p_value'], method='bh')
ttest_results['significant_fdr'] = ttest_results['p_value_fdr'] < alpha

fisher_df['p_value_fdr'] = false_discovery_control(fisher_df['p_value'], method='bh')
fisher_df['significant_fdr'] = fisher_df['p_value_fdr'] < alpha

print(f"\nSignificant after FDR (t-test): {ttest_results['significant_fdr'].sum()}")
print(f"Significant after FDR (Fisher): {fisher_df['significant_fdr'].sum()}")
print(fisher_df[fisher_df['significant_fdr']][['group_a','group_b','p_value','p_value_fdr']])

# Correction comparison chart
correction_summary = pd.DataFrame({
    'Uncorrected': [0, 9],
    'Bonferroni': [0, 7],
    'FDR': [0, 9]
}, index=['Conversion_Rate (t-test)', 'Conversion_Rate (Fisher)'])

fig, ax = plt.subplots(figsize=(8, 5))
correction_summary.plot(kind='bar', ax=ax)
ax.set_ylabel('Number of significant comparisons')
ax.set_title('Effect of Multiple Comparisons Correction')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig('correction_comparison.png', dpi=150)
plt.close()
print("Saved correction_comparison.png")