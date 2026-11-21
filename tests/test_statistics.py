import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from data_exploration import fixture_data,prepare,summarize
from statistical_analysis import adjust,bh_adjust,compare_daily,compare_fisher
from power_analysis import power_simulation
from recommendations import allocate

class StatisticalLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.daily,cls.audit=prepare('demo')
        cls.a=summarize(cls.daily)
    def test_seven_groups(self):
        self.assertEqual(len(self.a),7)
        self.assertEqual(self.audit['analysis_rows'],630)
    def test_metric_ratios(self):
        a=self.a.iloc[0]
        self.assertAlmostEqual(a.cpa,a.spend/a.conversions)
        self.assertAlmostEqual(a.roas,a.revenue/a.spend)
    def test_bh_is_bounded_and_monotonic(self):
        p=np.array([.01,.02,.04,.9]);x=bh_adjust(p)
        self.assertTrue(np.all((x>=p)&(x<=1)))
        self.assertTrue(np.all(np.diff(x)>=-1e-9))
    def test_pairwise_welch_and_effects(self):
        t=compare_daily(self.daily)
        self.assertEqual(len(t),21)
        self.assertTrue(t.p_fdr_bh.ge(t.p_value).all())
        self.assertTrue(t.cohens_d.notna().all())
    def test_fisher_counts(self):
        f=compare_fisher(self.daily)
        self.assertEqual(len(f),21)
        self.assertTrue((f.clicks_a>=f.conversions_a).all())
    def test_budget(self):
        t={'daily_cpa':compare_daily(self.daily),'daily_roas':compare_daily(self.daily,'roas')}
        a=allocate(self.a,t)
        self.assertEqual(int(a.monthly_budget_usd.sum()),500000)
        self.assertTrue(a.share_pct.between(9.999,20.001).all())
    def test_simulated_power(self):
        p=power_simulation(sims=50)
        self.assertEqual(len(p),20)
        self.assertTrue(p.power.between(0,1).all())
if __name__=='__main__':unittest.main()
