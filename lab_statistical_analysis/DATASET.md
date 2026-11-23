# Dataset Documentation

## Selection

**Name:** Marketing Campaign Performance Dataset (200k)  
**Source:** Hugging Face mirror of a Kaggle marketing dataset  
**URL:** https://huggingface.co/datasets/federicomoreno/marketing-campaign-performance-200k  
**Original Kaggle attribution:** manishabhatt22 / Marketing Campaign Performance Dataset

I selected this dataset because it contains a large, manageable number of campaign observations, six marketing channels, conversion and cost fields, and a full-year date range. It supports both continuous and binary-outcome comparisons.

## Structure

- Original rows: 200,000
- Original columns: 16
- Channel count: 6
- Period: 2021-01-01 through 2021-12-31
- Channel observations: approximately 33,000 rows per channel

## Relevant fields

- `Channel_Used`: grouping variable
- `Acquisition_Cost`: campaign acquisition cost
- `Conversion_Rate`: reported campaign conversion rate
- `Clicks`: number of clicks
- `Impressions`: number of impressions
- `ROI`: reported campaign ROI
- `Date`: campaign date

## Preparation

The original acquisition-cost text was converted to numeric dollars. Dates were parsed. `Conversions` were estimated as `round(clicks * conversion_rate)`, with no value allowed to exceed clicks. Revenue was derived as `acquisition_cost * (1 + ROI)`, because the dataset does not include an explicit revenue column.

Additional calculated fields:

- CTR = clicks / impressions
- Conversion rate = conversions / clicks
- CPA = cost / conversions
- ROAS = revenue / cost
- Profit = revenue - cost
- Profit margin = profit / revenue

Infinite values were replaced with missing values and rows missing channel, date, cost, clicks, or conversions were excluded. The cleaned, prepared result is saved as `marketing_data.csv`.
