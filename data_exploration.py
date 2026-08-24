import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import fisher_exact, false_discovery_control

# Load dataset
df = pd.read_csv('data/marketing_campaign_dataset.csv')

# Basic structure
print(df.shape)
print(df.columns.tolist())
print(df.dtypes)
print(df.head())


# Clean Acquisition_Cost
df['Acquisition_Cost'] = df['Acquisition_Cost'].replace('[\$,]', '', regex=True).astype(float)

# Check missing values
print(df.isnull().sum())

# Check grouping variable
print(df['Channel_Used'].value_counts())

# Check date range
print(df['Date'].min(), df['Date'].max())

# Group summary
group_summary = df.groupby('Channel_Used').agg(
    n_campaigns=('Campaign_ID', 'count'),
    avg_conversion_rate=('Conversion_Rate', 'mean'),
    avg_acquisition_cost=('Acquisition_Cost', 'mean'),
    avg_roi=('ROI', 'mean'),
    avg_clicks=('Clicks', 'mean'),
    avg_impressions=('Impressions', 'mean'),
    avg_engagement=('Engagement_Score', 'mean')
).round(2)

print(group_summary)

# Save cleaned dataset
df.to_csv('data/marketing_data_cleaned.csv', index=False)
print("Saved cleaned dataset.")

#visualize group metrics
fig, axes = plt.subplots(2, 3, figsize=(16, 10))

group_summary['avg_acquisition_cost'].plot(kind='barh', ax=axes[0,0], title='Avg Acquisition Cost by Channel')
group_summary['avg_roi'].plot(kind='barh', ax=axes[0,1], title='Avg ROI by Channel')
group_summary['avg_conversion_rate'].plot(kind='barh', ax=axes[0,2], title='Avg Conversion Rate by Channel')
group_summary['n_campaigns'].plot(kind='barh', ax=axes[1,0], title='Campaign Count by Channel')
group_summary['avg_clicks'].plot(kind='barh', ax=axes[1,1], title='Avg Clicks by Channel')
group_summary['avg_engagement'].plot(kind='barh', ax=axes[1,2], title='Avg Engagement Score by Channel')

plt.tight_layout()
plt.savefig('group_metrics_overview.png', dpi=150)
plt.close()
print("Saved group_metrics_overview.png")

#distribution plots
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

df.boxplot(column='Conversion_Rate', by='Channel_Used', ax=axes[0])
axes[0].set_title('Conversion Rate Distribution by Channel')
axes[0].set_xlabel('Channel')
axes[0].tick_params(axis='x', rotation=45)

df.boxplot(column='ROI', by='Channel_Used', ax=axes[1])
axes[1].set_title('ROI Distribution by Channel')
axes[1].set_xlabel('Channel')
axes[1].tick_params(axis='x', rotation=45)

plt.suptitle('')
plt.tight_layout()
plt.savefig('group_distributions.png', dpi=150)
plt.close()
print("Saved group_distributions.png")