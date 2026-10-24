from copy import deepcopy
from ._gridflow.model import validate as network_validate
from .constraints import violations
def validate(model):
    m=deepcopy(model);m['network']=network_validate(m['network']);violations({},**m.get('limits',{}));return m
