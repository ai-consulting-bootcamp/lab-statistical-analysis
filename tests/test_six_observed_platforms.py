"""Regression: real source may have six platforms, never invent a seventh."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import pandas as pd
from data_exploration import prepare


class SixObservedPlatformsTests(unittest.TestCase):
    def test_seven_real_nonoverlapping_delivery_segments(self):
        rows=[]
        for day in pd.date_range('2025-05-01',periods=40):
            for idx in range(6):
                for placement in ('Feed','Stories'):
                    rows.append({
                        'date':day.strftime('%d/%m/%Y'),
                        'platform':f'Actual platform {idx}',
                        'placement':placement,
                        'objective':'Sales',
                        'spend':100+idx*10,
                        'impressions':1500,
                        'clicks':90,
                        'conversions':4,
                        'revenue':400
                    })
        with tempfile.TemporaryDirectory() as tmp:
            csv=Path(tmp)/'dataset.csv'
            pd.DataFrame(rows).to_csv(csv,index=False)
            with patch('data_exploration.RAW',csv):
                daily,audit=prepare('hf',days=40)
        self.assertEqual(audit['observed_platform_count'],6)
        self.assertEqual(audit['unique_channels'],7)
        self.assertEqual(audit['date_format'],'DD/MM/YYYY')
        self.assertEqual(daily['clicks'].sum(),40*6*2*90)
        self.assertIn('split_platform',audit)
        self.assertIn('placement segments',audit['grouping_strategy'])


if __name__=='__main__':
    unittest.main()
