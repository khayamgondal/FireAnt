#!/usr/bin/env python
 # -*- coding: utf-8 -*-
import memcache,json,subprocess,time,uuid,os
import ConfigParser,MySQLdb

#----------------------------------
# Fireant working environment setup
#----------------------------------
config = ConfigParser.ConfigParser()
home_directory = os.path.expanduser('~')
config.read(home_directory + '/.fireantenv')
folder_path = config.get('directory','path')

config = ConfigParser.ConfigParser()
config.read('/etc/nova/fireant.conf')
local_ip = config.get('Local','ip')
shared = memcache.Client(['127.0.0.1:11211'], debug=0)
data = {}
data['vm_alias'] = shared.get('name')
data['flavor'] = shared.get('flavor')
if shared.get('vlantag') == -1 :
  data['ID'] = 'empty'
else :
  data['ID'] =  shared.get('vlantag')
data['image'] = shared.get('image')
data['vnitag']= shared.get('vnitag')
if shared.get('ipaddr') is not None:
   data['vm_ip'] = shared.get('ipaddr')
data['host_ip'] = local_ip #'172.16.10.83'
data['service'] = 'dbserver'
data['bin_name'] = 'dbserver.bin'
data['hop_count'] = shared.get('hopcount')
data2 = {}
data2['request'] = data
json_data = json.dumps(data2)

capabilities = {}
cap = {}

cap['virtulization'] = 'full'
cap['image_protocol'] = 'ccnx'
cap['network'] = 'ethernet'
capabilities = cap

firstreq = {}
firstreq['id']= shared.get('name')
firstreq['capabilites'] = capabilities
firstreq['properties'] = data

resource ={}
resource['resources'] = [firstreq]
connections = {}
connections = [[shared.get('name'),'vx1']]
resource['connections'] = connections
request = {}
request['request'] = resource
# Khayam: adding IP & MAC into request
dip=config.get('Local', 'ip')
dbase=config.get('sql', 'db')
duser=config.get('sql', 'user')
dpass=config.get('sql', 'pass')
db = MySQLdb.connect(host=dip,
                user=duser, # your username
                passwd=dpass, # your password
                db=dbase) # name of the data base

cur = db.cursor()
netinfo = {}
cur.execute("select mac,ip,vlan from vms where cluster='CB_"+dip+"'")
for idx, row in enumerate(cur.fetchall()):
     current = {}    
     current['mac']=row[0]
     current['ip']=row[1]
     current['vlan']=row[2]
     netinfo[idx]=current
request['netinfo']=netinfo
# Ke: add uuid into the request json 09/14/2015
request_uuid = str(uuid.uuid4())
request['request']['uuid'] = request_uuid

common = memcache.Client([local_ip+':11211'], debug=0)
common.set('vm', 'noone')
demotype = shared.get('demotype')
if int(demotype) == 1:
	request['request']['forward_type'] = 'broadcast'
else:
	request['request']['forward_type'] = 'unicast'


new_data = json.dumps(request)

#file = open('/home/dell/Documents/fireant/sockreq.json','w')
file = open(folder_path+'SharedData/sockreq.json','w')
file.write(new_data)
file.close()

'''
if int(demotype) == 1:
  cmd = "python /home/dell/Documents/fireant/socket_request.py > /home/dell/request_log"
else:
  cmd = "python /home/dell/Documents/fireant/unicast_request.py > /home/dell/request_log"
#cmd = "python /home/dell/Documents/fireant/fireant_request_temp.py > /home/dell/output_log"
'''
# New fireant code tested by Ke 09082015
cmd = "echo 'recepter.py here...' >> "+folder_path+"Log/fireant.log"
subprocess.Popen(cmd,shell=True)
cmd = folder_path+"MessageManagement/LocalRequestHandler.py "+folder_path+"/SharedData/sockreq.json >> "+folder_path+"Log/fireant.log"
#cmd = "./kenew/Code/MessageManagement/LocalRequestHandler.py ./kenew/Code/SharedData/sockreq.json"
subprocess.call(cmd,shell=True)
#time.sleep(5)
