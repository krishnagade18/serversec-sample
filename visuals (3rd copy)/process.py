import json
import collections
from optparse import OptionParser
from collections import OrderedDict
parser = OptionParser()
parser.add_option("-r", "--region", dest="region",
                  help="(Optional) It takes Region String. possible options us-east-1,us-west-2,us-west-1,eu-west-1,eu-central-1,ap-southeast-1,ap-southeast-,ap-northeast-1,sa-east-1", metavar="String")
parser.add_option("-m", "--mode", dest="mode",
                  help="(Optional) It takes process mode. possible options F , R", metavar="String")
parser.add_option("-i", "--id", dest="rc_id",
                  help="(Optional) It takes ID of Resource", metavar="String")
# parser.add_option("-o", "--output", dest="output_file",
#                   help="It takes output file path", metavar="FILE")
(options, args) = parser.parse_args()
output_file_path='out/result.txt'
space=['','    ']
from copy import copy
source={}
security_groups={}
result = []
path = []
def make_empty(file):
	with open(file, "w") as f:
		f.write('')
def get_keys(d, target):
    #import pdb;pdb.set_trace()
    type(d)
    for k, v in d.iteritems():
    	if k == target:
        	result.append(copy(path))
        	break
        path.append(k)
        if isinstance(v, dict):
            get_keys(v, target)
        elif isinstance(v, list):
        	for l1 in v:
        		if isinstance(l1, list):
		            if target in l1:
		            	result.append(copy(path))
		        elif isinstance(l1, dict):
		            get_keys(l1, target)
		        elif l1 == target:
		        	result.append(copy(path))
        elif v == target:
            result.append(copy(path))
            #print k

        path.pop()
       
def parse_dict(d):
	return_string=''
	for i,j in d.iteritems():
		return_string=return_string+i+'='+j+'|'
	return return_string

def pri(text):
	global output_file_path
	with open(output_file_path, "ab") as f:
		#f.write(space[0]+text+'\n')
		global source
		str1='<table><tr><td><b>'+'id'+'</td><td>'+text+'</td></tr>'
		if text[0]== 'i':
			str1='<html><h2> EC2</h2>'+str1
			tags=parse_dict(source['ec2'][text])
			tags=tags.split('|')
		elif text[0]== 'v':
			str1='<html><h2> VPC</h2>'+str1
			tags=parse_dict(source['vpc'][text])
			tags=tags.split('|')
		elif text[0]== 's':
			str1='<html><h2> Subnet</h2>'+str1
			tags=parse_dict(source['subnet'][text])
			tags=tags.split('|')
		for tag in tags:
			tag=tag.split('=')
			if len(tag)==2 and not tag[0].startswith('aws:cloudformation:'):
				str1=str1+'<tr><td><b>'+tag[0]+'</td><td>'+tag[1]+'</td></tr>'
		str1=str1+'</html>'	
		f.write(space[0]+str1+'\n')


def pri2(text):
	global output_file_path
	with open(output_file_path, "ab") as f:
		text=text.split(',')
		#print text[0]
		str1=''
		if text[0][:3]== 'igw':
			str1='<html><h2> Internet Gate Way</h2>'+str1
		elif text[0][:3]== 'cgw':
			str1='<html><h2> Customar Gate Way</h2>'+str1
			
		elif text[0][:3]== 'acl':
			str1='<html><h2> Network ACL</h2>'+str1
		elif text[0][:3]== 'rtb':
			str1='<html><h2> Route Table</h2>'+str1
		elif text[0][:2]== 'sg':
			str1='<html><h2> Security Group</h2>'+str1
					
		str1=str1+'<table><tr><td><b>'+'id'+'</td><td>'+text[0]+'</td></tr>'
		if len(text)==2: 
			tags=text[1].split('|')
			for tag in tags:
				tag=tag.split('=')
				if len(tag)==2 and not tag[0].startswith('aws:cloudformation:'):
					str1=str1+'<tr><td><b>'+tag[0]+'</td><td>'+tag[1]+'</td></tr>'
		if text[0][:2]== 'sg':
			sgdata=security_groups[text[0]]
			sgdata=sgdata.split('|')
			for tag in sgdata:
				tag=tag.split('=')
				if len(tag)==2 and not tag[0].startswith('aws:cloudformation:'):
					str1=str1+'<tr><td><b>'+tag[0]+'</td><td>'+tag[1].replace('IPPermissions:','')+'</td></tr>'

		str1=str1+'</html>'	
		f.write(space[0]+str1+'\n')	

def recursive_text(data,head=''):
	if head != '':
		pri(head)
		space[0]=space[0]+space[1]
	if type(data) == type({}):
		space[0]=space[0]+space[1]
		for i in data:
			space[0]=space[0][:-4]
			pri(i)
			space[0]=space[0]+space[1]
			recursive_text(data[i])
		space[0]=space[0][:-4]
	if type(data) == type([]):
		for i in data:
			recursive_text(i)
	if type(data) == type(['k'][0]) or type(data) == type(u'MyString'):
		pri2(data)
def recursive_rev_text(data,keys,count):
	if type(data) == type({}):
		for i in data:
			if len(keys) != 0 and i == keys[0]:
				
				keys=keys[1:]
				count=count+1
				space[0]=space[1]*count
				pri(i)
				space[0]=space[0]+space[1]
				recursive_rev_text(data[i],keys,count)
			else:
				pass
	if type(data) == type([]):
		for i in data:
			recursive_rev_text(i,keys,count)
	if type(data) == type('k') or type(data) == type(u'MyString'):
		pri2(data)
	
def validation():
	global source
	global security_groups
	if options.region is None:
		#print 'all'
		regions=['us-east-1','us-west-2','us-west-1','eu-west-1','eu-central-1','ap-southeast-1','ap-northeast-1','sa-east-1']
		for region in regions:
			global output_file_path
			output_file_path='temp/'+region+'.txt'
			with open('data/'+region+'.txt', "r") as f:
				data=json.load(f)
			source=data[1]
			security_groups=data[2]
			make_empty(output_file_path)
			recursive_text(data[0])
		
		output_file_path='out/result.txt'
		make_empty(output_file_path)
		for region in regions:
			with open(output_file_path, "ab") as f:
				f.write(region+'\n')
				with open('temp/'+region+'.txt', "r") as f1:
					for x in f1:
						f.write('    '+x+'\n')
		print 'Success'
	elif options.mode is None:
		#print 'all in '+options.region
		with open('data/'+options.region+'.txt', "r") as f:
			data=json.load(f)
		source=data[1]
		security_groups=data[2]
		make_empty(output_file_path)
		recursive_text(data[0])
		print 'Success'
	elif not options.mode is None:
		if options.rc_id is None:
			print 'If you specify Mode then Resource ID is required.'
		else:
			if options.mode == 'F':
				#print 'id:'+options.rc_id+ 'mode: Forwd'
				with open('data/'+options.region+'.txt', "r") as f:
					data=json.load(f)
				get_keys(data[0],options.rc_id)
				security_groups=data[2]
				# if len(result)==0:
				# 	print 'Please check Resource ID'
				print result
				for res in result:
					if len(res) == 0:
						source=data[1]
						make_empty(output_file_path)
						recursive_text(data[0][options.rc_id],head=options.rc_id)
					elif len(res) == 1:
						source=data[1]
						#import pdb;pdb.set_trace()
						make_empty(output_file_path)
						recursive_text(data[0][res[0]][1][options.rc_id],head=options.rc_id)
					elif len(res) == 2:
						source=data[1]
						make_empty(output_file_path)
						recursive_text(recursive_text(data[0][res[0]][1][res[1]][1][options.rc_id],head=options.rc_id))
				if len(result)==0:
					print 'Please check Resource ID'
				else:
					print 'Success'
			elif options.mode == 'R':
				with open('data/'+options.region+'.txt', "r") as f:
					data=json.load(f)
				security_groups=data[2]
				get_keys(data[0],options.rc_id)
				print result
				for res in result:
					space[0]=''
					if len(res) == 0:
						source=data[1]
						make_empty(output_file_path)
						res.append(options.rc_id) 
						recursive_rev_text(data[0],res,0)
					elif len(res) == 1:
						source=data[1]
						make_empty(output_file_path)
						res.append(options.rc_id) 
						recursive_rev_text(data[0],res,0)
					elif len(res) == 2:
						source=data[1]
						make_empty(output_file_path)
						res.append(options.rc_id) 
						recursive_rev_text(data[0],res,0)
				if len(result)==0:
					print 'Please check Resource ID'
				else:
					print 'Success'
			else:
				print 'Wrong Mode'


if __name__ == '__main__':
	# spaces=''
	# tab='    '
	validation()