#!/usr/bin/python
import memcache,json,sys,os,ConfigParser,time,subprocess
from pprint import pprint
#----------------------------------
# Fireant working environment setup
#----------------------------------
config = ConfigParser.ConfigParser()
home_directory = os.path.expanduser('~')
config.read(home_directory + '/.fireantenv')
folder_path = config.get('directory','path')
sys.path.insert(0, folder_path+'Common')
from ReadConfig import ReadConfig

DEBUG_MODULE = '[ResourceManagement]'
DEBUG_SCRIPT = '[OpenStackResourceAssignment]'
DEBUG_HEADER = DEBUG_MODULE + DEBUG_SCRIPT

def OpenStackResourceAssignment(message_content_json):
    config = ConfigParser.ConfigParser()
    config.read('/etc/nova/fireant.conf')

    req_data = {}
    req_data['request'] = message_content_json['request']['resources'][0]['properties']
    print DEBUG_HEADER, "Assigning resources for the request..."
    #Save the mac and ip into localfile
    smi=open(folder_path+"maciptable","w")
    entry= ""
    table =  message_content_json['netinfo']
    for tab in table:
        tab = int(tab)
        local_ip=config.get('Local','ip')
        if table.values()[tab]['cluster'] != local_ip: #Dont add local flows into tables
           entry = entry+ req_data['request']['host_ip']+"_"+table.values()[tab]['ip']+"_"+table.values()[tab]['mac']+'_'+table.values()[tab]['vlan']+"\n"
    smi.write(entry)
    smi.close()
    print DEBUG_HEADER, "Setting vlan/vxlan tags..."
    shared = memcache.Client(['127.0.0.1:11211'], debug=0)
    shared.set('vlantag', req_data['request']['ID'])
    shared.set('vnitag', req_data['request']['vnitag'])
    shared.set('ipaddr', req_data['request']['vm_ip'])
    shared.set('host',req_data['request']['host_ip']) # New line added by Khayam   
    print DEBUG_HEADER, "Launching vms..."
    ipcmd = "#!/bin/bash\n ifconfig eth1 "+req_data['request']['vm_ip'] +"/24 up"
    vmdata_file_path = folder_path+'SharedData/vmdata.txt'
    f = open(vmdata_file_path,'w')
    f.write(ipcmd)
    f.close() 

    user=config.get('creds', 'user')
    passwd=config.get('creds', 'pass')
    keystone=config.get('Local', 'ip')
    keystone= "http://"+keystone+":5000/v2.0/"
    tenant=config.get('creds', 'tenant')
    # Limits works with tenant ID, so need to get tenant id from keystone API.
    #Creating admin creds file
    import subprocess
    fo = open(folder_path+"keystone_tester", "w")
    contents = "export OS_USERNAME="+user+"\n" +"export OS_TENANT_NAME=tester\n"+"export OS_PASSWORD="+passwd+"\nexport OS_AUTH_URL="+keystone
    fo.write(contents)
    fo.close()
    cmd = "source "+folder_path+"keystone_tester && nova boot " + req_data['request']['vm_alias'] + \
            " --flavor " + req_data['request']['flavor'] + \
            " --image "+ req_data['request']['image'] + \
            " --user-data " + vmdata_file_path
    subprocess.Popen(cmd,shell=True)
    print DEBUG_HEADER, (req_data['request']['vm_alias'])
    time.sleep(2)

    return
