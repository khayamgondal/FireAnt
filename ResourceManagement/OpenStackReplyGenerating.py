#!/usr/bin/python
import sys,os,ConfigParser,json
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
DEBUG_SCRIPT = '[OpenStackReplyGenerating]'
DEBUG_HEADER = DEBUG_MODULE + DEBUG_SCRIPT

#------------------------
# Read configuration file
#------------------------
config = ReadConfig()
#print DEBUG_HEADER, config
local_ip = config.get('Local', 'ip')
#print DEBUG_HEADER, local_ip

def OpenStackReplyGenerating(message_content_json):
    print DEBUG_HEADER, "Generating a reply message..."

    reply_content_json = {}
    reply_content_json['action'] = 'reply'
    reply_content_json['last_hop_ip'] = message_content_json['last_hop_ip']
    reply_content_json['message_type'] = 'reply_to_others'

    reply_content_json['reply'] = {}
    reply_content_json['reply']['host_ip'] = local_ip
    reply_content_json['reply']['request_uuid'] = message_content_json['request']['uuid']
    reply_content_json['reply']['requester_ip'] = message_content_json['request']['resources'][0]['properties']['host_ip']
    
    reply_content_json['reply']['resources'] = {}
    reply_content_json['reply']['resources']['vm_name'] = message_content_json['request']['connections'][0][0]
    reply_content_json['reply']['resources']['vxlan'] = message_content_json['request']['resources'][0]['properties']['ID']

    print DEBUG_HEADER, "The reply message content is:"
    pprint(reply_content_json)

    return reply_content_json
