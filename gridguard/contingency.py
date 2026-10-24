from ._gridflow.model import validate
from .scenarios import enumerate_outages,outage,corrective
from .islands import analyze_islands
from .constraints import violations,reactive_reserve,real_power_adequacy
def evaluate(network,method='newton',limits=None,promote=True):
    n=validate(network);result=analyze_islands(n,method,promote);rows=[];reserve=[];adequacy=[]
    for island in result['islands']:
        if island['status']=='solved':
            rows.append(violations(island['result'],**(limits or {})));reserve+=reactive_reserve(n,island['result']);adequacy+=real_power_adequacy(n,island['result'])
    unknown=any(r['status'] in ['failed','nonconverged'] for r in result['islands']);violation_count=sum(r['count'] for r in rows);capacity_fail=sum(r['adequate'] is False for r in adequacy);reactive_fail=sum(r['outside_limits'] for r in reserve)
    secure=result['solved'] and violation_count==0 and capacity_fail==0 and reactive_fail==0
    return dict(result,secure=secure,violations=rows,violation_count=violation_count,reactive_reserve=reserve,real_power_adequacy=adequacy,unknown=unknown,severity=sum(r['severity'] for r in rows)+capacity_fail+reactive_fail,capacity_bounds_complete=all(r['adequate'] is not None for r in adequacy))
def n_minus_one(network,method='newton',limits=None,include_generators=True,promote=True):
    n=validate(network);base=evaluate(n,method,limits,promote);rows=[]
    for scenario in enumerate_outages(n,include_generators):
        modified=outage(n,scenario['kind'],scenario['id']);r=evaluate(modified,method,limits,promote);rows.append({'scenario':scenario,'result':r})
    rows.sort(key=lambda r:(r['result']['unsupplied_mw']>0,r['result']['unsupplied_mw'],r['result']['unknown'],r['result']['severity']),reverse=True)
    return {'base':base,'contingencies':rows,'secure_count':sum(r['result']['secure'] for r in rows),'scenario_count':len(rows),'assumptions':['Static balanced AC/DC N-1 with explicit reference promotion.','Unknown or nonconverged scenarios are never marked secure.','Security is conditional on supplied equipment ratings and generator capacity bounds.']}
def corrective_study(network,scenario,actions,limits=None):
    damaged=outage(network,scenario['kind'],scenario['id']);before=evaluate(damaged,limits=limits);rows=[]
    if len(actions)>100:raise ValueError('At most 100 corrective candidates')
    for action in actions:
        changed=corrective(damaged,action.get('load_fraction',0),action.get('redispatch'));rows.append({'action':action,'result':evaluate(changed,limits=limits)})
    return {'before':before,'actions':rows,'assumption':'Candidate evaluation, not a corrective-action optimizer.'}
