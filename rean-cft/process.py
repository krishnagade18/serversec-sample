import json,sys
from jinja2 import Environment, FileSystemLoader
from filters import *
from optparse import OptionParser
from collections import OrderedDict
import pprint
parser = OptionParser()
parser.add_option("-i", "--input", dest="input_file",
                  help="It takes comma separated input file paths", metavar="FILE")
parser.add_option("-t", "--template", dest="main_template",
                  help="It takes main template file name", metavar="FILE")
parser.add_option("-o", "--output", dest="output_file",
                  help="It takes output file path", metavar="FILE")


(options, args) = parser.parse_args()
CFT_Map={
    'vpc':['VPC','Name','CidrBlock','EnableDnsSupport','EnableDnsHostnames','InstanceTenancy','Tags'],
    'subnet':['Subnet','Name','VpcId','AvailabilityZone','CidrBlock','Tags'],
    'internetgateway':['InternetGateway','igwname,','Tags'],
    'vpngateway':['VPNGateway','vpngwname','Type','Tags'],
    'customergateway':['CustomerGateway','cgwname','BgpAsn','IpAddress','Type','Tags'],
    'vpcgatewayattachment':['VPCGatewayAttachment','attachigwname','VpcId','GatewayType','GatewayId'],
    'vpngatewayroutepropagation':['VPNGatewayRoutePropagation','vpngwrpname','DependsOn','RouteTableIds','VpnGatewayId'],
    'networkacl':['NetworkAcl','aclname','VpcId','Tags'],
    'subnetnetworkaclassociation':['SubnetNetworkAclAssociation','subnetaclassocname','SubnetId','NetworkAclId'],
    'networkaclentry':['NetworkAclEntry','aclentry1name','NetworkAclId','RuleNumber','RuleAction','Protocol','Egress','CidrBlock','Icmpcode', 'Icmptype','PortRangeFrom','PortRangeTo'],
    'routetable':['RouteTable','routetablename','VpcId','Tags'],
    'route':['Route','routename','DependsOn','RouteTableId','DestinationCidrBlock','RType','RName'],
    'subnetroutetableassociation':['SubnetRouteTableAssociation', 'subnetrtaname','SubnetId', 'RouteTableId'],
    'securitygroup':['SecurityGroup', 'sgname','VpcId', 'GroupDescription'],
    'securitygroupegress':['SecurityGroupEgress','sgegressname','GroupId','Dtype','Dvalue','FromPort','ToPort'],
    'securitygroupingress':['SecurityGroupIngress','sgingressname','GroupId','Dtype','Dvalue','FromPort','ToPort'],
    'networkinterface':['NetworkInterface','name','SourceDestCheck','SubnetID','PrivateIpAddress','Tags', 'Description']
}

class GenerateCFT(object):

    def __init__(self):
        self.inputfile = []
        inputfiles=options.input_file.split(',')
        for inputfile in inputfiles:
            self.inputfile.append(open(inputfile))
        self.generate_cft()
    def noduplicates(self,seq): 
       # order preserving
       noDupes = []
       [noDupes.append(i) for i in seq if not noDupes.count(i)]
       return noDupes

    def parse_csv_file(self):
        '''
            function which is used to parse
            the contents from the csv file
        '''
        #inputfile = self.inputfile[0]
        try:
            input_data=[]
            #import pdb;pdb.set_trace()
            output_data=[]
            menu_obj=[]
            output_dict={}
            output_key=''
            resources=[]
            description=''
            desc=False
            #inputfile = self.inputfile[0]
            for inputfile in self.inputfile:
                for x in inputfile.readlines():
                    output_data=[]
                    if x[-1] == '\n':
                        x=x[:-1]
                    if desc:
                        description = x
                        desc=False
                        continue
                    if x== '#description':
                        desc=True
                        continue
                        # replace the below with regular expression match for /s*[\"#]
                    elif x[0] == '#' or x[0] == '"' :
                        continue
                    line_obj=x.strip().split(',')
                    #line_obj.strip()
                    menu_obj=CFT_Map[line_obj[0].lower()]
                    output_key=menu_obj[0]
                    resources.append(menu_obj[0])
                    temp_dict={}
                    tags_dicts=[]
                    tags_obj=[]
                    loopcount=0
                    for menu in menu_obj:
                        if loopcount == 0:
                            temp_dict['Type']=line_obj[loopcount]
                        elif loopcount == 1:
                            temp_dict['Name']=line_obj[loopcount]
                        else:
                            temp_dict[menu]=line_obj[loopcount]
                        loopcount+=1
                    if 'Tags' in menu_obj: 
                        tags_obj=temp_dict['Tags'].split('|')
                        for tag in tags_obj:
                            tag=tag.split('=')
                            tags_dicts.append({'Key':tag[0],'Value':tag[1]})
                        temp_dict['Tags']=tags_dicts
                    output_data.append(temp_dict)
                    if not output_key in output_dict:
                        output_dict[output_key]=[]
                    else:
                        pass   
                    output_dict[output_key].append(output_data[0])
        except Exception,e:
            print e
        #import pdb;pdb.set_trace()
        return {
            'csv_data':output_dict,
            #'resources':self.noduplicates(resources),
            'resources':output_dict.keys()
        }

    def render_jinja_templates(self, context):
        '''
            function which is used to render the jinja 
            templates from data taken from csv file
        '''
        
        env = Environment(loader=FileSystemLoader('templates/'))
        env.filters['inline'] = inline
        env.filters['route'] = route
        env.filters['route_menu'] = route_menu
        env.filters['check_cidr'] = check_cidr
        env.filters['RouteTableIds'] = RouteTableIds
        env.filters['instancetenancy'] = instancetenancy
        env.filters['gatewaytype'] = gatewaytype
        template = env.get_template(options.main_template)
        output = template.render(context)
        with open(options.output_file, "wb") as f:
            #output=json.loads(output)
            #f.write(json.dumps(OrderedDict(json.loads(output)),indent=4))
            #tempp=json.dumps(json.loads(output),indent=4)
            #f.write(output)
            #import pdb;pdb.set_trace()
            output=json.JSONDecoder(object_pairs_hook=OrderedDict).decode(output)
            f.write(json.dumps(output,indent=4))
    def generate_cft(self):
        '''
            function which is used to generate
            the CFT files by rendering jinja
            templates and stores the final CFT
            template in output folder
        '''
        context = self.parse_csv_file()
        pprint.pprint(context)
        self.render_jinja_templates(context)
        print "CFT Generated"

if __name__ == '__main__':
    if options.output_file is None:
        options.output_file="output/output.json"
    if options.main_template is None:
        options.main_template="cft.j2"
    if options.input_file is None:
        print 'please provide inputfile path and try again'
    else:
        GenerateCFT()
    # import pdb;pdb.set_trace()