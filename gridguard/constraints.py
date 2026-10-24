from .numeric import finite
def violations(result,vmin=.95,vmax=1.05,loading_limit=100):
    finite(vmin,'vmin',.1,2);finite(vmax,'vmax',vmin,2);finite(loading_limit,'loading limit',1,1000)
    volts=[{'bus':b['id'],'voltage_pu':b['vm_pu'],'deviation_pu':max(vmin-b['vm_pu'],b['vm_pu']-vmax,0)} for b in result.get('buses',[]) if b['vm_pu']<vmin or b['vm_pu']>vmax]
    thermal=[{'branch':b['id'],'loading_percent':b['loading_percent'],'excess_percent':b['loading_percent']-loading_limit} for b in result.get('branches',[]) if b.get('loading_percent') is not None and b['loading_percent']>loading_limit]
    return {'voltage':volts,'thermal':thermal,'count':len(volts)+len(thermal),'severity':sum(x['deviation_pu']/.05 for x in volts)+sum(x['excess_percent']/100 for x in thermal)}
def reactive_reserve(network,result):
    rows=[]
    for bus in result.get('buses',[]):
        generators=[d for d in network.get('generators',[]) if d.get('status',True) and d['bus']==bus['id']]
        if not generators:continue
        if 'required_generation_mvar' not in bus:
            rows.append({'bus':bus['id'],'q_required_mvar':None,'upward_mvar':None,'downward_mvar':None,'outside_limits':None,'reason':'Reactive output unavailable in this solver approximation'})
            continue
        lo=sum(d.get('qmin',-1e6) for d in generators);hi=sum(d.get('qmax',1e6) for d in generators);used=bus['required_generation_mvar']
        rows.append({'bus':bus['id'],'q_required_mvar':used,'upward_mvar':hi-used,'downward_mvar':used-lo,'outside_limits':used<lo-1e-6 or used>hi+1e-6})
    return rows
def real_power_adequacy(network,result):
    rows=[]
    for bus in result.get('buses',[]):
        generators=[d for d in network.get('generators',[]) if d.get('status',True) and d['bus']==bus['id']]
        if not generators:continue
        # An absent bound remains unknown instead of implying unlimited capacity.
        bounded=all('pmax_mw' in d for d in generators)
        load=sum(d['p_mw'] for d in network.get('loads',[]) if d.get('status',True) and d['bus']==bus['id'])
        required=bus.get('required_generation_mw',bus.get('p_injection_mw',0)+load)
        maximum=sum(d.get('pmax_mw',0) for d in generators) if bounded else None
        rows.append({'bus':bus['id'],'required_mw':required,'maximum_mw':maximum,'adequate':required<=maximum+1e-6 if bounded else None})
    return rows
