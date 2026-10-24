import hashlib,json
from .model import validate
from .contingency import evaluate,n_minus_one,corrective_study
from .factors import ptdf,lodf,screen
from .stability import pv,qv,continue_load
def run(model,action='analyze',options=None):
    m=validate(model);n=m['network'];options=options or {}
    if action=='analyze':result=evaluate(n,limits=m.get('limits'),**options)
    elif action=='n_minus_one':result=n_minus_one(n,limits=m.get('limits'),**options)
    elif action=='ptdf':result=ptdf(n)
    elif action=='lodf':result=lodf(n)
    elif action=='screen':result=screen(n)
    elif action=='pv':result=pv(n,options.get('scales',m.get('scales',[.5,1,1.5,2])))
    elif action=='qv':result=qv(n,options.get('bus',m.get('qv_bus')),options.get('injections_mvar',m.get('q_injections_mvar',[-10,0,10])))
    elif action=='continuation':result=continue_load(n,**options)
    elif action=='corrective':result=corrective_study(n,options['scenario'],options['actions'],limits=m.get('limits'))
    else:raise ValueError('Unknown study')
    result['provenance']={'sha256':hashlib.sha256(json.dumps(model,sort_keys=True,allow_nan=False).encode()).hexdigest(),'action':action,'options':options,'version':'1.0.0'}
    return result
