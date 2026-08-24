# W7D5_LAB_In_God_we_trust_everyone_else_bring_the_data
- Week 7 / Day 5
- Student: Andreas Papachristophorou
- Course: AI Consulting & Integration 2026-07
- Date: 2026-08-24
---

# Step 1: Find and Select a Dataset

## Dataset Name
Digital Marketing Campaign Dataset

## Source
Kaggle

## Dataset URL
https://www.kaggle.com/datasets/arpit2712/digital-marketing-company/data

# Step 2: Load and Explore Your Dataset

Dataset shape: (8000, 20)

Column names:
['CustomerID', 'Age', 'Gender', 'Income', 'CampaignChannel', 'CampaignType', 'AdSpend', 'ClickThroughRate', 'ConversionRate', 'WebsiteVisits', 'PagesPerVisit', 'TimeOnSite', 'SocialShares', 'EmailOpens', 'EmailClicks', 'PreviousPurchases', 'LoyaltyPoints', 'AdvertisingPlatform', 'AdvertisingTool', 'Conversion']

First five rows:

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>CustomerID</th>
      <th>Age</th>
      <th>Gender</th>
      <th>Income</th>
      <th>CampaignChannel</th>
      <th>CampaignType</th>
      <th>AdSpend</th>
      <th>ClickThroughRate</th>
      <th>ConversionRate</th>
      <th>WebsiteVisits</th>
      <th>PagesPerVisit</th>
      <th>TimeOnSite</th>
      <th>SocialShares</th>
      <th>EmailOpens</th>
      <th>EmailClicks</th>
      <th>PreviousPurchases</th>
      <th>LoyaltyPoints</th>
      <th>AdvertisingPlatform</th>
      <th>AdvertisingTool</th>
      <th>Conversion</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>8000</td>
      <td>56</td>
      <td>Female</td>
      <td>136912</td>
      <td>Social Media</td>
      <td>Awareness</td>
      <td>6497.870068</td>
      <td>0.043919</td>
      <td>0.088031</td>
      <td>0</td>
      <td>2.399017</td>
      <td>7.396803</td>
      <td>19</td>
      <td>6</td>
      <td>9</td>
      <td>4</td>
      <td>688</td>
      <td>IsConfid</td>
      <td>ToolConfid</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>8001</td>
      <td>69</td>
      <td>Male</td>
      <td>41760</td>
      <td>Email</td>
      <td>Retention</td>
      <td>3898.668606</td>
      <td>0.155725</td>
      <td>0.182725</td>
      <td>42</td>
      <td>2.917138</td>
      <td>5.352549</td>
      <td>5</td>
      <td>2</td>
      <td>7</td>
      <td>2</td>
      <td>3459</td>
      <td>IsConfid</td>
      <td>ToolConfid</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>8002</td>
      <td>46</td>
      <td>Female</td>
      <td>88456</td>
      <td>PPC</td>
      <td>Awareness</td>
      <td>1546.429596</td>
      <td>0.277490</td>
      <td>0.076423</td>
      <td>2</td>
      <td>8.223619</td>
      <td>13.794901</td>
      <td>0</td>
      <td>11</td>
      <td>2</td>
      <td>8</td>
      <td>2337</td>
      <td>IsConfid</td>
      <td>ToolConfid</td>
      <td>1</td>
    </tr>
    <tr>
      <th>3</th>
      <td>8003</td>
      <td>32</td>
      <td>Female</td>
      <td>44085</td>
      <td>PPC</td>
      <td>Conversion</td>
      <td>539.525936</td>
      <td>0.137611</td>
      <td>0.088004</td>
      <td>47</td>
      <td>4.540939</td>
      <td>14.688363</td>
      <td>89</td>
      <td>2</td>
      <td>2</td>
      <td>0</td>
      <td>2463</td>
      <td>IsConfid</td>
      <td>ToolConfid</td>
      <td>1</td>
    </tr>
    <tr>
      <th>4</th>
      <td>8004</td>
      <td>60</td>
      <td>Female</td>
      <td>83964</td>
      <td>PPC</td>
      <td>Conversion</td>
      <td>1678.043573</td>
      <td>0.252851</td>
      <td>0.109940</td>
      <td>0</td>
      <td>2.046847</td>
      <td>13.993370</td>
      <td>6</td>
      <td>6</td>
      <td>6</td>
      <td>8</td>
      <td>4345</td>
      <td>IsConfid</td>
      <td>ToolConfid</td>
      <td>1</td>
    </tr>
  </tbody>
</table>
</div>


## Marketing Channel Performance Summary:

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Records</th>
      <th>Average_AdSpend</th>
      <th>Average_CTR</th>
      <th>Average_ConversionRate</th>
      <th>Average_WebsiteVisits</th>
      <th>Binary_Conversion_Rate</th>
    </tr>
    <tr>
      <th>CampaignChannel</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Social Media</th>
      <td>1519</td>
      <td>4965.32</td>
      <td>15.55</td>
      <td>10.66</td>
      <td>25.13</td>
      <td>86.83</td>
    </tr>
    <tr>
      <th>Email</th>
      <td>1557</td>
      <td>5055.60</td>
      <td>15.56</td>
      <td>10.49</td>
      <td>24.88</td>
      <td>87.03</td>
    </tr>
    <tr>
      <th>PPC</th>
      <td>1655</td>
      <td>4954.22</td>
      <td>15.83</td>
      <td>10.41</td>
      <td>24.16</td>
      <td>88.28</td>
    </tr>
    <tr>
      <th>SEO</th>
      <td>1550</td>
      <td>4994.13</td>
      <td>15.32</td>
      <td>10.35</td>
      <td>24.74</td>
      <td>87.68</td>
    </tr>
    <tr>
      <th>Referral</th>
      <td>1719</td>
      <td>5034.04</td>
      <td>15.17</td>
      <td>10.31</td>
      <td>24.89</td>
      <td>88.31</td>
    </tr>
  </tbody>
</table>
</div>