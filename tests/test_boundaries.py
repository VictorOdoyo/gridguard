import unittest,copy
from gridguard.cli import load_case
from gridguard.factors import ptdf,lodf
from gridguard.scenarios import outage,corrective
from gridguard.contingency import evaluate,n_minus_one
from gridguard.constraints import reactive_reserve,real_power_adequacy
from gridguard.stability import qv
class Boundaries(unittest.TestCase):
    def setUp(self):self.n=load_case('example:industrial')['network']
    def test_unknown_outage(self):
        with self.assertRaises(ValueError):outage(self.n,'branch','unknown')
    def test_outage_repeat_rejected(self):
        with self.assertRaises(ValueError):outage(outage(self.n,'branch','sb'),'branch','sb')
    def test_negative_reactance_factors(self):
        self.n['branches'][0]['x']=-.1
        with self.assertRaises(ValueError):ptdf(self.n)
    def test_multi_island_ptdf_rejected(self):
        self.n=outage(outage(self.n,'branch','sb'),'branch','ab')
        with self.assertRaises(ValueError):ptdf(self.n)
    def test_qv_controlled_bus(self):
        with self.assertRaises(ValueError):qv(self.n,'s',[1])
    def test_invalid_shedding(self):
        with self.assertRaises(ValueError):corrective(self.n,1.1)
    def test_redispatch_capacity(self):
        with self.assertRaises(ValueError):corrective(self.n,redispatch={'ga':1000})
    def test_unknown_bounds_explicit(self):
        r=real_power_adequacy({'generators':[{'bus':'s'}]},{'buses':[{'id':'s','required_generation_mw':10}]})[0];self.assertIsNone(r['adequate'])
    def test_dc_reactive_unknown(self):
        r=reactive_reserve({'generators':[{'bus':'s'}]},{'buses':[{'id':'s','p_injection_mw':10}]})[0];self.assertIsNone(r['q_required_mvar'])
    def test_dc_colocated_load(self):
        r=real_power_adequacy({'generators':[{'bus':'s','pmax_mw':20}],'loads':[{'bus':'s','p_mw':15}]},{'buses':[{'id':'s','p_injection_mw':10}]})[0];self.assertFalse(r['adequate']);self.assertEqual(r['required_mw'],25)
    def test_rank_source_loss_present(self):
        r=n_minus_one(self.n);self.assertEqual(r['scenario_count'],5);self.assertTrue(any(x['scenario']['id']=='gs' for x in r['contingencies']))
    def test_unknown_solver_rejected(self):
        r=evaluate(self.n,method='invalid');self.assertTrue(r['unknown']);self.assertFalse(r['secure'])
