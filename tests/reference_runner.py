import math
import numpy as np
from gridguard.scenarios import outage,corrective,enumerate_outages
from gridguard.islands import analyze_islands
from gridguard.factors import ptdf,lodf,screen
from gridguard.stability import pv,qv,continue_load
from gridguard.constraints import violations,reactive_reserve,real_power_adequacy
from gridguard._gridflow.dc import solve_dc
def verify(test,c):
    f=c['family'];a=c['inputs'];e=c['expected'];n=a.get('network')
    if f=='branch_outage':actual=outage(n,'branch','l')['branches'][0]['status'];test.assertNotIn('status',n['branches'][0])
    elif f=='generator_outage':actual=outage(n,'generator','g')['buses'][0]['kind'];test.assertEqual(actual,e);return
    elif f in ['unsupplied_island','reference_promotion','promotion_disabled']:
        r=analyze_islands(outage(n,'branch','l'),allow_reference_promotion=f!='promotion_disabled');actual=r['unsupplied_mw']
        if f=='reference_promotion':test.assertTrue(any(x['promoted_reference']=='d' for x in r['islands']))
    elif f=='dc_angle':r=solve_dc(n);actual=r['buses'][1]['va_deg'];test.assertAlmostEqual(r['branches'][0]['p_from_mw'],n['loads'][0]['p_mw'])
    elif f=='ptdf_triangle':r=ptdf(n);actual=np.array(r['matrix'])[:,r['bus_ids'].index('b')]
    elif f=='lodf_triangle':actual=lodf(n)['matrix']
    elif f=='dc_screen':
        r=screen(n);error=0
        for row in r['screening']:
            direct=solve_dc(outage(n,'branch',row['outage']))
            for b in direct['branches']:error=max(error,abs(b['p_from_mw']-row['predicted_flow_mw'][b['id']]))
        actual=error
    elif f=='pv_resistive':actual=pv(n,[a['scale']])['points'][0]['result']['buses'][1]['vm_pu']
    elif f=='qv_reactive':actual=qv(n,'d',[a['injection']])['points'][0]['voltage_pu']
    elif f=='reactive_reserve':
        r=reactive_reserve({'generators':[{'bus':'s','qmin':a['qmin'],'qmax':a['qmax']}]},{'buses':[{'id':'s','required_generation_mvar':a['required']}]})[0];actual=[r['upward_mvar'],r['downward_mvar']]
    elif f=='voltage_severity':actual=violations({'buses':[{'id':'d','vm_pu':a['voltage']}],'branches':[]})['severity']
    elif f=='overload_severity':actual=violations({'buses':[],'branches':[{'id':'l','loading_percent':a['loading']}]})['severity']
    elif f=='real_adequacy':actual=real_power_adequacy({'generators':[{'bus':'s','pmax_mw':a['maximum']}]},{'buses':[{'id':'s','required_generation_mw':a['required']}]})[0]['adequate']
    elif f=='corrective_shedding':r=corrective(n,a['fraction']);actual=[r['loads'][0][k] for k in ['p_mw','q_mvar']];test.assertEqual(n['loads'][0]['p_mw'],100)
    elif f=='n1_count':actual=len(enumerate_outages(n))
    elif f=='bridge_lodf':r=lodf(n);test.assertEqual([r['inapplicable_outages'],r['matrix']],e);return
    elif f=='continuation_residual':
        r=continue_load(n,steps=a['steps']);test.assertEqual(len(r['points']),a['steps']+1);test.assertLess(max(p['mismatch_pu'] for p in r['points']),e);return
    else:
        r=ptdf(n);h=np.array(r['matrix']);ids=r['bus_ids'];transfer=h[:,ids.index('b')]-h[:,ids.index('a')];balance={b:0. for b in ids}
        for line,value in zip(n['branches'],transfer):balance[line['from']]+=value;balance[line['to']]-=value
        actual=balance['b'];test.assertAlmostEqual(balance['a'],-1);test.assertAlmostEqual(balance['s'],0)
    np.testing.assert_allclose(actual,e,rtol=1e-7,atol=1e-7)
