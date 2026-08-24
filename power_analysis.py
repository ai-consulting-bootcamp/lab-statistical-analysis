import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind

np.random.seed(42)

def empirical_power_cpa(true_diff_pct, base_cpa, n_days, n_sim=1000, alpha=0.05):
    rejections = 0
    std = base_cpa * 0.15
    cap = base_cpa * 0.5
    for _ in range(n_sim):
        a = np.random.normal(base_cpa, std, n_days)
        a = np.clip(a, base_cpa - cap, base_cpa + cap)
        b = np.random.normal(base_cpa * (1 + true_diff_pct), std, n_days)
        b = np.clip(b, base_cpa - cap, base_cpa + cap)
        _, p = ttest_ind(a, b)
        if p < alpha:
            rejections += 1
    return rejections / n_sim

base_cpa = 12500  # from group summary
effect_sizes = [0.05, 0.10, 0.15, 0.20]
sample_sizes = [30, 60, 90, 120, 180]

power_results = []
for eff in effect_sizes:
    for n in sample_sizes:
        power = empirical_power_cpa(eff, base_cpa, n, n_sim=500)
        power_results.append({'effect_size_pct': eff*100, 'n_days': n, 'power': power})
        print(f"Effect: {eff*100:.0f}%, N days: {n}, Power: {power:.3f}")

power_df = pd.DataFrame(power_results)

# Power curves
fig, ax = plt.subplots(figsize=(9, 6))
for eff in effect_sizes:
    subset = power_df[power_df['effect_size_pct'] == eff*100]
    ax.plot(subset['n_days'], subset['power'], marker='o', label=f"{eff*100:.0f}% effect")

ax.axhline(0.8, color='red', linestyle='--', label='80% power target')
ax.set_xlabel('Sample size (days)')
ax.set_ylabel('Power')
ax.set_title('Power Curves by Effect Size')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('power_analysis_cpa.png', dpi=150)
plt.close()
print("Saved power_analysis_cpa.png")

# Minimum sample size for 80% power
target_power = 0.80
print("\nMinimum days for 80% power:")
min_days_results = []
for eff in effect_sizes:
    subset = power_df[power_df['effect_size_pct'] == eff*100].sort_values('n_days')
    adequate = subset[subset['power'] >= target_power]
    min_days = adequate['n_days'].min() if not adequate.empty else None
    current_status = "Sufficient" if (min_days is not None and min_days <= 90) else "Insufficient"
    min_days_results.append({'effect_size_pct': eff*100, 'min_days_needed': min_days, 'current_90_days_status': current_status})
    print(f"Effect {eff*100:.0f}%: min days = {min_days}, current 90-day data = {current_status}")

min_days_df = pd.DataFrame(min_days_results)

# Assess power for observed significant differences
significant_pairs = [
    ('Google Ads', 'YouTube', 0.40),
    ('Google Ads', 'Instagram', 0.26),
    ('Google Ads', 'Email', 0.30),
    ('YouTube', 'Website', 0.61),
    ('YouTube', 'Facebook', 0.53),
    ('YouTube', 'Email', 0.70),
    ('Instagram', 'Website', 0.47),
    ('Instagram', 'Facebook', 0.39),
    ('Instagram', 'Email', 0.56)
]

print("Power to detect observed differences with 90 days of data:")
for a, b, pct_diff in significant_pairs:
    eff = abs(pct_diff) / 100
    power = empirical_power_cpa(eff, base_cpa, 90, n_sim=500)
    status = "Adequate" if power >= 0.8 else "Underpowered"
    print(f"{a} vs {b}: observed diff {pct_diff:.2f}%, power at 90 days = {power:.3f} ({status})")

    # Bootstrap confidence intervals for CPA by channel
def bootstrap_ci(data, n_bootstrap=1000, ci_level=0.95):
    boot_means = []
    for _ in range(n_bootstrap):
        sample = np.random.choice(data, size=len(data), replace=True)
        boot_means.append(sample.mean())
    lower = np.percentile(boot_means, (1 - ci_level) / 2 * 100)
    upper = np.percentile(boot_means, (1 + ci_level) / 2 * 100)
    return lower, upper

df = pd.read_csv('data/marketing_data_cleaned.csv')
ci_results = []
for ch in df['Channel_Used'].unique():
    data = df[df['Channel_Used'] == ch]['Acquisition_Cost'].dropna().values
    lower, upper = bootstrap_ci(data)
    ci_results.append({'channel': ch, 'mean_cpa': round(data.mean(),2), 'ci_lower': round(lower,2), 'ci_upper': round(upper,2)})

ci_df = pd.DataFrame(ci_results)
print(ci_df)

# Composite score: rank by CPA (lower better) and ROI (higher better)
summary = pd.read_csv('data/marketing_data_cleaned.csv').groupby('Channel_Used').agg(
    avg_cpa=('Acquisition_Cost', 'mean'),
    avg_roi=('ROI', 'mean')
)

summary['cpa_rank'] = summary['avg_cpa'].rank(ascending=True)  # lower cpa = better = lower rank
summary['roi_rank'] = summary['avg_roi'].rank(ascending=False)  # higher roi = better = lower rank
summary['composite_score'] = 0.5 * summary['cpa_rank'] + 0.5 * summary['roi_rank']
summary = summary.sort_values('composite_score')

# Equal allocation given no statistically meaningful differences
budget = 500000
n_channels = len(summary)
summary['allocation'] = budget / n_channels
summary['allocation_pct'] = 100 / n_channels

print(summary.round(2))