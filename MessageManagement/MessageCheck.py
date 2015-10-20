#/usr/bin/env python
import pika,sys,os,ConfigParser,json
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
from PushToQueue import PushToQueue
sys.path.insert(0, folder_path+'AnalyticsEngine')
from AnalyticsEngine import *

DEBUG_MODULE = '[MessageManagement]'
DEBUG_SCRIPT = '[MessageCheck]'
DEBUG_HEADER = DEBUG_MODULE + DEBUG_SCRIPT

#------------------------
# Read configuration file
#------------------------
config = ReadConfig()
#print DEBUG_HEADER, config
listen_port = int(config.get('MessageManagement', 'listen_port'))
#print DEBUG_HEADER, listen_port
message_cache_name = config.get('MessageManagement', 'message_cache_name')
#print DEBUG_HEADER, message_cache_name
resource_management_queue_name = config.get('ResourceManagement', 'message_queue_name')
#print DEBUG_HEADER, resource_management_queue_name
communication_queue_name = config.get('Communication', 'message_queue_name')
local_ip = config.get('Local', 'ip')
#print DEBUG_HEADER, local_ip

#------------------------
# Message check functions
#------------------------
def MessageTypeCheck(message_content):
    print DEBUG_HEADER, "Checking message type..."
    #print DEBUG_HEADER, type(message_content)
    message_content_json = json.loads(message_content)
    pprint(message_content_json)
    if message_content_json.get('request') is not None:
        #print DEBUG_HEADER, "The message is a REQUEST."
        if message_content_json['request']['resources'][0]['properties']['host_ip'] == local_ip:
            message_type = 'request_from_local'
        else:
            message_type = 'request_from_others'
        print DEBUG_HEADER, "The message is a '%s'" % (message_type)
        return message_type
    if message_content_json.get('reply') is not None:
        print DEBUG_HEADER, "The message is a REPLY."
        if message_content_json['reply']['requester_ip'] == local_ip:
            message_type = 'reply_to_local'
        else:
            message_type = 'reply_to_others'
        print DEBUG_HEADER, "The message is a '%s'" % (message_type)
        return message_type

def MessageRecordCheck(message_type, message_content):
    print DEBUG_HEADER, "Checking message record..."
    message_content_json = json.loads(message_content)

    if (message_type == 'request_from_local') or (message_type == 'request_from_others'):
        message_uuid = message_content_json['request']['uuid']
        is_existed = isExistingRecord(message_uuid)
 
        if is_existed == 'yes':
            print DEBUG_HEADER, "Found one existing request record."
            # Check if the message timeout or not
            is_timeout = isTimeout(message_uuid)
            if is_timeout == 'yes':
                #print DEBUG_HEADER, "Deleting the request record..."
                DeleteRecord(message_uuid)
                print DEBUG_HEADER, "Discard the received message."
                return
            elif is_timeout == 'no':
                #print DEBUG_HEADER, "Checking if the request was replied..."
                is_replied = isReplied(message_uuid)
                if is_replied == 'yes':
                    #print DEBUG_HEADER, "The request was already replied."
                    print DEBUG_HEADER, "Discard the received message."
                    return
                elif is_replied == 'no':
                    #print DEBUG_HEADER, "The request is pending."
                    print DEBUG_HEADER, "Checking if the in_direction is contained in the table..."
                    message_in_direction = message_content_json['last_hop_ip']
                    contain_in_direction = containInDirection(message_uuid, message_in_direction)
                    if contain_in_direction == 'yes':
                        print DEBUG_HEADER, "Discard the received message."
                        return
                    elif contain_in_direction == 'no':
                        print DEBUG_HEADER, "Updating the in_direction for this record..."
                        UpdateInDirection(message_uuid, message_in_direction)
                        print DEBUG_HEADER, "Discard the received message."
                        return

        elif is_existed == 'no':
            print DEBUG_HEADER, "No request record was found."
            #print DEBUG_HEADER, "Inserting a record into the request_status table..."
            message_status = 'pending'
            message_forwarded_direction = None
            message_in_direction = message_content_json['last_hop_ip']
            InsertRecord(message_uuid, message_status, message_forwarded_direction, \
                            message_in_direction, message_content)
            
            print DEBUG_HEADER, "Pushing the message into the resource_management_message_queue..."
            message_content_json['message_type'] = message_type
            message_content = json.dumps(message_content_json)
            PushToQueue(resource_management_queue_name, message_content)
            #print DEBUG_HEADER, "Sent on message to the ResourceManagementMessageQueue."
            return
        
    elif (message_type == 'reply_to_others'):
        message_content_json['action'] = 'forward'
        print DEBUG_HEADER, "Added the header 'action' into the message."
        
        request_uuid = message_content_json['reply']['request_uuid']
        is_existed = isExistingRecord(request_uuid)

        if is_existed == 'yes':
            print DEBUG_HEADER, "Found one existing request record."
            # Check if the request timeout or not
            is_timeout = isTimeout(request_uuid)
            if is_timeout == 'yes':
                #print DEBUG_HEADER, "Deleting the request record..."
                DeleteRecord(request_uuid)
                print DEBUG_HEADER, "Discard the received reply."
                return
            elif is_timeout == 'no':
                print DEBUG_HEADER, "Checking if the request was replied..."
                is_replied = isReplied(request_uuid)
                if is_replied == 'yes':
                    print DEBUG_HEADER, "The request was already replied."
                    print DEBUG_HEADER, "Discard the received reply."
                    return
                elif is_replied == 'no':
                    print DEBUG_HEADER, "The request is still pending."
                    UpdateStatus(request_uuid, 'replied')
                    IncreaseRepliesCountByOne(message_content_json['last_hop_ip'])

                    print DEBUG_HEADER, "Pushing the message into the %s..." % (communication_queue_name)
                    message_content_json['message_type'] = message_type
                    message_content = json.dumps(message_content_json)
                    PushToQueue(communication_queue_name, message_content)
                    #print DEBUG_HEADER, "Sent on message to the ResourceManagementMessageQueue."
                    return

        elif is_existed == 'no':
            print DEBUG_HEADER, "No request record was found."
                   
            request_status = 'replied'
            request_forwarded_direction = None
            request_in_direction = None
            request_content = None
            InsertRecord(request_uuid, request_status, request_forwarded_direction, \
                            request_in_direction, request_content)

            print DEBUG_HEADER, "Pushing the message into the %s..." % (communication_queue_name)
            message_content_json['message_type'] = message_type
            message_content = json.dumps(message_content_json)
            PushToQueue(communication_queue_name, message_content)
            return

    elif (message_type == 'reply_to_local'):
        request_uuid = message_content_json['reply']['request_uuid']
        is_existed = isExistingRecord(request_uuid)

        if is_existed == 'yes':
            print DEBUG_HEADER, "Found one existing request record."
            # Check if the request timeout or not
            is_timeout = isTimeout(request_uuid)
            if is_timeout == 'yes':
                #print DEBUG_HEADER, "Deleting the request record..."
                DeleteRecord(request_uuid)
                print DEBUG_HEADER, "Discard the received reply."
                return
            elif is_timeout == 'no':
                print DEBUG_HEADER, "Checking if the request was replied..."
                is_replied = isReplied(request_uuid)
                if is_replied == 'yes':
                    print DEBUG_HEADER, "The request was already replied."
                    print DEBUG_HEADER, "Discard the received reply."
                    return
                elif is_replied == 'no':
                    print DEBUG_HEADER, "The request is still pending."
                    UpdateStatus(request_uuid, 'replied')
                    IncreaseRepliesCountByOne(message_content_json['last_hop_ip'])
                    reply_content_json = {}
                    reply_content_json['reply'] = message_content_json['reply']
                    reply_content = json.dumps(reply_content_json)
                    UpdateReplyContent(request_uuid, reply_content)

                    print DEBUG_HEADER, "Pushing the message into the %s..." % (resource_management_queue_name)
                    message_content_json['message_type'] = message_type
                    message_content = json.dumps(message_content_json)
                    PushToQueue(resource_management_queue_name, message_content)
                    #print DEBUG_HEADER, "Sent on message to the ResourceManagementMessageQueue."
                    return

        elif is_existed == 'no':
            print DEBUG_HEADER, "No request record was found."
            print DEBUG_HEADER, "Discard the received reply."
            return

#-------------------------
# Message Cache connection
#-------------------------
message_cache_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
message_cache_channel = message_cache_connection.channel()
message_cache_channel.queue_declare(queue = message_cache_name)

print DEBUG_HEADER, "Waiting for messages from the Message Cache..."

def callback(channel, method, properties, body):
    print DEBUG_HEADER, "Received one message from the Message Cache."
    print DEBUG_HEADER, "Received message content: \n", body
    message_type = MessageTypeCheck(body)
    message_record_status = MessageRecordCheck(message_type, body)
    

message_cache_channel.basic_consume(callback, queue=message_cache_name, no_ack=True)
message_cache_channel.start_consuming()
