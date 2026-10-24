from copy import deepcopy
from ._gridflow.model import validate
from ._gridflow.solver import solve
from ._gridflow.continuation import continuation
from .constraints import reactive_reserve
from .numeric import finite
def pv(network,scales):
    n=validate(network);rows=[]
    if not 1<=len(scales)<=200:raise ValueError('PV scan requires 1..200 points')
    for scale in scales:
        finite(scale,'load scale',0,20);case=deepcopy(n)
        for load in case['loads']:load['p_mw']*=scale;load['q_mvar']*=scale
        r=solve(case);rows.append({'scale':scale,'converged':r['converged'],'min_voltage_pu':min(b['vm_pu'] for b in r['buses']) if r['converged'] else None,'reserve':reactive_reserve(case,r) if r['converged'] else [],'result':r})
    return {'points':rows,'assumption':'Independent fixed-load AC solutions; a failed solve is not proof of collapse.'}
def qv(network,bus,injections_mvar):
    n=validate(network);target=next((b for b in n['buses'] if b['id']==bus),None)
    if target is None or target['kind']!='PQ':raise ValueError('QV injection scan requires a PQ bus')
    if not 1<=len(injections_mvar)<=200:raise ValueError('QV scan requires 1..200 points')
    rows=[]
    for q in injections_mvar:
        finite(q,'reactive injection',-1e5,1e5);case=deepcopy(n);case['loads'].append({'id':'__qv_probe__','bus':bus,'p_mw':0,'q_mvar':-q})
        r=solve(case);value=next(b['vm_pu'] for b in r['buses'] if b['id']==bus) if r['converged'] else None;rows.append({'q_injection_mvar':q,'voltage_pu':value,'converged':r['converged']})
    return {'bus':bus,'points':rows,'assumption':'Reactive injection versus voltage sweep; not a full controlled-voltage QV continuation.'}
def continue_load(network,steps=50,step_size=.05):return continuation(network,steps=steps,step_size=step_size)
