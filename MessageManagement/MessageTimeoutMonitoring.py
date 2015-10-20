#!/usr/bin/env python
import sys,os,ConfigParser,time
#----------------------------------
# Fireant working environment setup
#----------------------------------
config = ConfigParser.ConfigParser()
home_directory = os.path.expanduser('~')
config.read(home_directory + '/.fireantenv')
folder_path = config.get('directory','path')
sys.path.insert(0, folder_path+'Common')
from ReadConfig import ReadConfig
sys.path.insert(0, folder_path+'AnalyticsEngine')
from AnalyticsEngine import *

DEBUG_MODULE = '[MessageManagement]'
DEBUG_SCRIPT = '[MessageTimeoutMonitoring]'
DEBUG_HEADER = DEBUG_MODULE + DEBUG_SCRIPT

#------------------------
# Read configuration file
#------------------------
config = ReadConfig()
#print DEBUG_HEADER, config
request_timeout_seconds = int(config.get('AnalyticsEngine', 'request_timeout_seconds'))
print DEBUG_HEADER, request_timeout_seconds

while True:

    request_uuid_set = ReadRequestUUID()
    #print DEBUG_HEADER, request_uuid_set
    if request_uuid_set is not None:
        for request_entry in request_uuid_set:
            #print DEBUG_HEADER, request_entry
            request_uuid = request_entry[0]
            print DEBUG_HEADER, request_uuid
            is_timeout = isTimeout(request_uuid)
            print DEBUG_HEADER, "Is this request timeout? %s." % (is_timeout)

            if is_timeout == 'yes':
                DeleteRecord(request_uuid)
    else:
        print DEBUG_HEADER, "There is no existing record."   
    # Check every one hour
    print DEBUG_HEADER, "Will check timeout in the next hour."
    time.sleep(3600)
