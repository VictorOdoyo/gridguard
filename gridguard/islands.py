from copy import deepcopy
from ._gridflow.model import validate
from ._gridflow.topology import islands
from ._gridflow.solver import solve
def analyze_islands(network,method='newton',allow_reference_promotion=True):
    n=validate(network);groups=islands(n);rows=[];total_unsupplied=0
    for group in groups:
        subset=deepcopy(n);subset['buses']=[b for b in n['buses'] if b['id'] in group]
        for key in ['generators','loads']:subset[key]=[d for d in n[key] if d['bus'] in group]
        subset['branches']=[b for b in n['branches'] if b['from'] in group and b['to'] in group]
        demand=sum(max(0,d['p_mw']) for d in subset['loads'] if d['status'])
        online=[d for d in subset['generators'] if d['status']];refs=[b for b in subset['buses'] if b['kind']=='Slack']
        promoted=None
        if not refs and allow_reference_promotion:
            eligible=[d for d in online if d.get('reference_capable',True)]
            if eligible:
                promoted=eligible[0]['bus'];next(b for b in subset['buses'] if b['id']==promoted)['kind']='Slack';refs=[promoted]
        if len(refs)!=1:
            total_unsupplied+=demand;rows.append({'buses':group,'status':'unsupplied','unsupplied_mw':demand,'promoted_reference':promoted,'reason':'No unique dispatchable voltage reference'});continue
        try:
            result=solve(subset,method=method);status='solved' if result['converged'] else 'nonconverged'
            rows.append({'buses':group,'status':status,'unsupplied_mw':0,'promoted_reference':promoted,'result':result})
        except (ValueError,ArithmeticError) as exc:rows.append({'buses':group,'status':'failed','unsupplied_mw':0,'promoted_reference':promoted,'error':str(exc)})
    return {'islands':rows,'unsupplied_mw':total_unsupplied,'solved':all(r['status']=='solved' for r in rows),'island_count':len(groups),'assumptions':['Reference promotion is an explicit static islanding assumption.','Unsupplied means no valid reference, not a probabilistic reliability estimate.','Nonconverged islands are unknown, not secure or automatically unsupplied.','No frequency dynamics or generator real-power redispatch optimization.']}
