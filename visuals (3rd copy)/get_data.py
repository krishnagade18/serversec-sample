import boto.ec2
import json
import collections

#rs = [i.id,i. for i in conn.get_all_security_groups()]
def parse_dict(d):
	return_string=''
	for i,j in d.iteritems():
		return_string=return_string+i+'='+j+'|'
	return return_string
def parse_acl(acls):
	#import pdb;pdb.set_trace()
	return_string="<table><tr><td>RuleNumber</td><td>RuleAction</td><td>Protocol</td><td>Egress</td><td>CidrBlock</td><td>Icmpcode</td><td>Icmptype</td><td>PortRangeFrom</td><td>PortRangeTo</td></tr>"
	for acl in acls:
		return_string=return_string+'<tr><td>'+acl.rule_number+'</td><td>'+acl.rule_action+'</td><td>'+acl.protocol+'</td><td>'+acl.egress+'</td><td>'+acl.cidr_block+'</td><td>'+str(acl.icmp.code)+'</td><td>'+str(acl.icmp.type)+'</td><td>'+str(acl.port_range.from_port)+'</td><td>'+str(acl.port_range.to_port)+'</td></tr>'
	return_string=return_string+'</table>'
	return return_string
def parse_rtb(rtbs):
	#import pdb;pdb.set_trace()
	return_string="<table><tr><td>Destination</td><td>Target</td><td>Status</td></tr>"
	for rtb in rtbs:
		return_string=return_string+'<tr><td>'+str(rtb.destination_cidr_block)+'</td><td>'+str(rtb.interface_id)+'</td><td>'+str(rtb.state)+'</td></tr>'
	return_string=return_string+'</table>'
	return return_string
def parse_sg(sgs):
	#import pdb;pdb.set_trace()
	return_string="<table><tr><td>Protocol</td><td>from_port</td><td>to_port</td></tr>"
	for sg in sgs:
		return_string=return_string+'<tr><td>'+str(sg.ip_protocol)+'</td><td>'+str(sg.from_port)+'</td><td>'+str(sg.to_port)+'</td></tr>'
	return_string=return_string+'</table>'
	return return_string
def get_from_aws(key,secret,region):
	
	conn = boto.ec2.connect_to_region(region,aws_access_key_id=key,aws_secret_access_key=secret)
	from boto.vpc import VPCConnection
	myregion = boto.ec2.get_region(region_name=region)
	c = VPCConnection(region=myregion,aws_access_key_id=key,aws_secret_access_key=secret)
	rs = [(i.id,parse_dict({'name':i.name,'rules':parse_sg(i.rules)})) for i in conn.get_all_security_groups()]
	security_groups_dump=dict(rs)
	output_json={}
	tag_details={}
	tag_details['ec2']=tag_details['subnet']=tag_details['vpc']={}
	all_subnets=[]
	all_vpc=[[i.id,i.tags,i.instance_tenancy,i.is_default,i.cidr_block] for i in c.get_all_vpcs()]
	for vpc in all_vpc:
		subnet_json={}
		all_igw=[i.id+','+parse_dict(i.tags) for i in c.get_all_internet_gateways(filters={'attachment.vpc-id': vpc[0]})]
		try:
			all_cgw=[[i.id+','+parse_dict(i.tags)] for i in c.get_all_customer_gateways(filters={'vpc-id': vpc[0]})]
		except:
			all_cgw=[]
		all_subnets=[[i.id,i.tags,i.cidr_block] for i in c.get_all_subnets(filters={'vpc-id': vpc[0]})]
		tag_details['vpc'][vpc[0]]=vpc[1]
		tag_details['vpc'][vpc[0]]['instance_tenancy']=vpc[2]
		tag_details['vpc'][vpc[0]]['is_default']=str(vpc[3])
		tag_details['vpc'][vpc[0]]['cidr_block']=vpc[4]
		for subnet in all_subnets:
			all_acl=[i.id+','+parse_dict({'network_acl_entries':parse_acl(i.network_acl_entries)}) for i in c.get_all_network_acls(filters={'association.subnet_id': subnet[0]})]
			all_rt=[i.id+','+parse_dict({'routes':parse_rtb(i.routes).replace(',','  ')}) for i in c.get_all_route_tables(filters={'association.subnet_id': subnet[0]})]
			all_instances=conn.get_only_instances(filters={'subnet-id': subnet[0]})
			ec2_dict={}
			for ins in all_instances:
				sgs=[i.id for i in ins.groups]
				#sgs=[g.name+parse_dict({'rules':str(g.rules)}) for g in c.get_all_security_groups() if ins in g.instances() ]
				enis=[ i.id for i in c.get_all_network_interfaces(filters={'attachment.instance_id':ins.id})]
				ec2_dict[ins.id]=sgs
				tag_details['ec2'][ins.id]=ins.tags
				tag_details['ec2'][ins.id]['public_dns_name']=ins.public_dns_name
				tag_details['ec2'][ins.id]['network_interfaces']=str(enis)
			subnet_json[subnet[0]]=[all_acl+all_rt,ec2_dict]#{'all_acl':all_acl,'all_rt':all_rt,'ec2_dict':ec2_dict}
			tag_details['subnet'][subnet[0]]=subnet[1]
			tag_details['subnet'][subnet[0]]['cidr_block']=subnet[2]

		output_json[vpc[0]]=[all_igw+all_cgw,subnet_json]#{'igw':all_igw,'cgw':'all_cgw','subnets':subnet_json}
	with open('data/'+region+'.txt', "w") as f:
		f.write(json.dumps([output_json,tag_details,security_groups_dump],indent=4))
if __name__ == '__main__':
	key='AKIAIOYUNN7IX5AD24UA'
	secret='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'
	region='us-east-1'
	regions=['us-east-1','us-west-2','us-west-1','eu-west-1','eu-central-1','ap-southeast-1','ap-northeast-1','sa-east-1']
	# for region in regions:
	# 	get_from_aws(key,secret,region)
	get_from_aws(key,secret,region)