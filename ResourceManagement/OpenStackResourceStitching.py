#!/usr/bin/python
import os

DEBUG_MODULE = '[ResourceManagement]'
DEBUG_SCRIPT = '[OpenStackResourceStitching]'
DEBUG_HEADER = DEBUG_MODULE + DEBUG_SCRIPT

def OpenStackResourceStitching(message_content_json):
    print DEBUG_HEADER, "Stitching the resource..."
    
    if message_content_json.get('request') is not None:
        remote_ip = message_content_json['request']['resources'][0]['properties']['host_ip']
    elif message_content_json.get('reply') is not None:
        remote_ip = message_content_json['reply']['host_ip']

    print DEBUG_HEADER, "Configuring vxlan tunnel..."
    cmd = "echo dell | sudo -S ovs-vsctl add-port br-ant vx" + remote_ip \
            +"  -- set interface vx" + remote_ip \
            +" type=vxlan options:remote_ip=" + remote_ip \
            + " option:key=flow "
    
    os.system(cmd)
