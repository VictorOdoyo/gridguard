import numpy as np
from ._gridflow.model import validate
from ._gridflow.topology import require_references,islands
from .scenarios import outage
def ptdf(network):
    n=validate(network);groups=require_references(n)
    if len(groups)!=1:raise ValueError('PTDF currently requires one connected island')
    ids=[b['id'] for b in n['buses']];index={b:i for i,b in enumerate(ids)};active=[b for b in n['branches'] if b['status']]
    reference=next(i for i,b in enumerate(n['buses']) if b['kind']=='Slack');free=[i for i in range(len(ids)) if i!=reference]
    incidence=np.zeros((len(active),len(ids)));susceptance=[]
    for i,b in enumerate(active):
        if b['x']<=0:raise ValueError('PTDF requires positive nonzero branch reactance')
        incidence[i,index[b['from']]]=1;incidence[i,index[b['to']]]=-1;susceptance.append(1/(b['x']*b['tap']))
    d=np.asarray(susceptance);bmat=incidence.T@np.diag(d)@incidence;h=np.zeros_like(incidence)
    try:h[:,free]=np.diag(d)@incidence[:,free]@np.linalg.inv(bmat[np.ix_(free,free)])
    except np.linalg.LinAlgError as exc:raise ValueError('Singular DC factor matrix') from exc
    return {'bus_ids':ids,'branch_ids':[b['id'] for b in active],'slack_bus':ids[reference],'matrix':h.tolist(),'assumptions':['Incremental lossless DC sensitivity in MW/MW.','Fixed taps and phase shifts; phase shifts contribute only to base flow.','Single slack withdrawal, zero slack column.']}
def lodf(network):
    n=validate(network);factors=ptdf(n);h=np.array(factors['matrix']);active=[b for b in n['branches'] if b['status']];index={b:i for i,b in enumerate(factors['bus_ids'])};columns=[];inapplicable=[]
    for k,branch in enumerate(active):
        modified=outage(n,'branch',branch['id'])
        if len(islands(modified))!=1:columns.append([None]*len(active));inapplicable.append(branch['id']);continue
        transfer=h[:,index[branch['from']]]-h[:,index[branch['to']]];denom=1-transfer[k]
        if abs(denom)<1e-10:columns.append([None]*len(active));inapplicable.append(branch['id']);continue
        column=transfer/denom;column[k]=-1;columns.append(column.tolist())
    matrix=[[columns[k][i] for k in range(len(active))] for i in range(len(active))]
    return {'branch_ids':factors['branch_ids'],'matrix':matrix,'inapplicable_outages':inapplicable,'assumptions':['LODF invalid for island-forming outages; those columns are null.','Post-outage prediction = base flow + LODF column times pre-outage flow on removed branch.']}
def screen(network):
    from ._gridflow.dc import solve_dc
    result=solve_dc(network);factors=lodf(network);byid={b['id']:b for b in result['branches']};rows=[]
    for k,key in enumerate(factors['branch_ids']):
        if key in factors['inapplicable_outages']:rows.append({'outage':key,'applicable':False,'reason':'islanding or singular transfer'});continue
        predictions={branch:byid[branch]['p_from_mw']+factors['matrix'][i][k]*byid[key]['p_from_mw'] for i,branch in enumerate(factors['branch_ids'])}
        rows.append({'outage':key,'applicable':True,'predicted_flow_mw':predictions})
    return {'screening':rows,'assumption':'DC line-outage screening is not an AC security certificate.'}
