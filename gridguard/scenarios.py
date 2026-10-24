from copy import deepcopy
from ._gridflow.model import validate
from .numeric import finite
def outage(network,kind,equipment_id):
    if kind not in ['branch','generator']:raise ValueError('Outage kind must be branch or generator')
    n=validate(network);collection=n['branches' if kind=='branch' else 'generators'];found=[d for d in collection if d['id']==equipment_id]
    if not found:raise ValueError('Unknown outage equipment')
    if not found[0]['status']:raise ValueError('Equipment is already offline')
    found[0]['status']=False
    # An offline controlled generator cannot retain a fictitious voltage reference.
    for bus in n['buses']:
        if bus['kind'] in ['Slack','PV'] and not any(d['status'] and d['bus']==bus['id'] for d in n['generators']):bus['kind']='PQ'
    return n
def enumerate_outages(network,include_generators=True):
    n=validate(network);rows=[{'kind':'branch','id':d['id']} for d in n['branches'] if d['status']]
    if include_generators:rows += [{'kind':'generator','id':d['id']} for d in n['generators'] if d['status']]
    return rows
def corrective(network,load_fraction=0,redispatch=None):
    finite(load_fraction,'load shedding fraction',0,1);n=deepcopy(network)
    for d in n.get('loads',[]):d['p_mw']*=1-load_fraction;d['q_mvar']*=1-load_fraction
    for key,value in (redispatch or {}).items():
        targets=[d for d in n.get('generators',[]) if d['id']==key and d.get('status',True)]
        if not targets:raise ValueError('Redispatch requires an online known generator')
        gen=targets[0];finite(value,'redispatch',gen.get('pmin_mw',0),gen.get('pmax_mw',1e9));gen['p_mw']=value
    return validate(n)
