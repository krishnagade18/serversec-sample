import re
import json

def inline(value):
    '''
        jinja filter which converts to 
        aws ref function, if variable startswith ref-
    '''
    if value.startswith('ref:'):
        return '{"Ref": "'+value.replace('ref:','')+'"}'
    elif value.startswith('getatt:'):
        attr = value.split(":")
        return '{"Fn::GetAtt":["'+attr[1]+'","'+attr[2]+'"]}'
    else:
        return '"'+value+'"'
def route(value):
    if value.startswith('gateway:'):
        return '"'+value.replace('gateway:','')+'"'
    elif value.startswith('eni:'):
    	return '"'+value.replace('eni:','')+'"'
    elif value.startswith('ec2:'):
    	return '"'+value.replace('ec2:','')+'"'
    elif value.startswith('rt:'):
    	return '"'+value.replace('rt:','')+'"'
    else:
        return '"'+value+'"'
def route_menu(value):
    if value.startswith('gateway:'):
        return '"GatewayId"'
    elif value.startswith('eni:'):
    	return '"NetworkInterfaceId"'
    elif value.startswith('ec2:'):
    	return '"InstanceId"'
    elif value.startswith('rt:'):
    	return '"RouteTableId"'
    else:
        return '"'+value+'"'
def check_cidr(value):
    a = re.compile("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/([0-9]|[1-2][0-9]|3[0-2]))$")
    if a.match(value):
        return '"CidrIp"'
    else:
        return '"DestinationSecurityGroupId"'
def RouteTableIds(value):
    Rids=value.split("|")
    return_str=[]
    for rid in Rids:
    	if rid.startswith('ref:'):
    		return_str.append({"Ref": rid.replace('ref:','')})
    	else:
    		return_str.append(rid)
    return json.dumps(return_str).encode('utf8')
def instancetenancy(value):
    if value.startswith('dedicated'):
        return '"dedicated"'
    else:
        return '"default"'
def gatewaytype(value):
    if value.startswith('vpn'):
        return '"vpn"'
    else:
        return '"internet"'