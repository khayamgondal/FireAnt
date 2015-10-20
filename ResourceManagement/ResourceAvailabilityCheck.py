#!/usr/bin/python
import ConfigParser,os,sys,memcache
from pprint import pprint
from novaclient import client

#----------------------------------
# Fireant working environment setup
#----------------------------------
config = ConfigParser.ConfigParser()
home_directory = os.path.expanduser('~')
config.read(home_directory + '/.fireantenv')
folder_path = config.get('directory','path')
sys.path.insert(0, folder_path+'ResourceManagement')
from OpenStackCheckResource import print_list


DEBUG_MODULE = '[ResourceManagement]'
DEBUG_SCRIPT = '[ResourceAvailabilityCheck]'
DEBUG_HEADER = DEBUG_MODULE + DEBUG_SCRIPT

def ResourceAvailabilityCheck(message_content_json):
    #print DEBUG_HEADER, "The received message content: "
    #pprint(message_content_json)
    print DEBUG_HEADER, "Checking resource availability..."

    config = ConfigParser.ConfigParser()
    config.read('/etc/nova/fireant.conf')
    #local = config.get('nova', 'local')
    admin_user=config.get('creds', 'admin_user')
    admin_pass=config.get('creds', 'admin_pass')
    keystone=config.get('Local', 'ip')
    keystone= "http://"+keystone+":5000/v2.0/"
    tenant=config.get('creds', 'tenant')
    # Limits works with tenant ID, so need to get tenant id from keystone API.
    #Creating admin creds file
    import subprocess
    fo = open(folder_path+"keystone_admin", "w")
    contents = "export OS_USERNAME="+admin_user+"\n" +"export OS_TENANT_NAME=admin\n"+"export OS_PASSWORD="+admin_pass+"\nexport OS_AUTH_URL="+keystone
    fo.write(contents)
    fo.close()
    #source the file and read from keystone
    cmd = "source "+folder_path+"keystone_admin && keystone tenant-list | grep " +tenant
    out =  os.popen(cmd).read()
    ten_id = out[2:34]
    print ten_id

    nova = client.Client(2,'admin',admin_user,admin_pass,keystone)
    limits = nova.limits.get(reserved=True, tenant_id=ten_id).absolute
    columns = ['Name', 'Value']
    res = print_list(limits, columns)

    freeRam = res['maxTotalRAMSize'] - res['totalRAMUsed']
    freeCores = res['maxTotalCores'] - res['totalCoresUsed']
    freeInstances = res['maxTotalInstances'] - res['totalInstancesUsed']
    
    req_data = {}
    req_data['request'] = message_content_json['request']['resources'][0]['properties']
    print DEBUG_HEADER, req_data

    if freeInstances > 0:
        reqRam = nova.flavors.get(req_data['request']['flavor']).ram
        reqvcpus = nova.flavors.get(req_data['request']['flavor']).vcpus
        if reqvcpus <= freeCores and reqRam <= freeRam:
            isAvailable = 'yes'
            print DEBUG_HEADER, "Resources are available!!!"
            common = memcache.Client([req_data['request']['host_ip']+':11211'], debug=0)
            cluster_name = config.get('Local', 'ip')
            common.set('vm', "CB_"+cluster_name)
        else:
            isAvailable = 'no'
            print DEBUG_HEADER, "No available resources found!!!"
    else:
        isAvailable = 'no'
        print DEBUG_HEADER, "No available resources found!!!" 
    
    return isAvailable
