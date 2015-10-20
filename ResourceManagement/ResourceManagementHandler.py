#!/usr/bin/python
import pika,json,sys,os,ConfigParser
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
sys.path.insert(0, folder_path+'ResourceManagement')
from ResourceAvailabilityCheck import ResourceAvailabilityCheck
from OpenStackResourceAssignment import OpenStackResourceAssignment
from OpenStackResourceStitching import OpenStackResourceStitching
from OpenStackReplyGenerating import OpenStackReplyGenerating

DEBUG_MODULE = '[ResourceManagement]'
DEBUG_SCRIPT = '[ResourceManagementHandler]'
DEBUG_HEADER = DEBUG_MODULE + DEBUG_SCRIPT

#------------------------
# Read configuration file
#------------------------
config = ReadConfig()
resource_management_queue_name = config.get('ResourceManagement', 'message_queue_name')
communication_queue_name = config.get('Communication', 'message_queue_name')

#-----------------------------------------
# Resource Management FIFO queue listening
#-----------------------------------------
queue_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
queue_channel = queue_connection.channel()
queue_channel.queue_declare(queue = resource_management_queue_name)

print DEBUG_HEADER, "Waiting for messages from the %s..." % (resource_management_queue_name)

def callback(channel, method, properties, body):
    print DEBUG_HEADER, "Received one message from the %s." % (resource_management_queue_name)
    print DEBUG_HEADER, "Received message content: "
    message_content_json = json.loads(body)
    pprint(message_content_json)
    
    message_type = message_content_json['message_type']
    if (message_type == 'request_from_local') or (message_type == 'request_from_others'):
        print DEBUG_HEADER, "This is a %s message." % (message_type)
        is_available = ResourceAvailabilityCheck(message_content_json)
        if is_available == 'yes':
            print DEBUG_HEADER, "The local resource is available."
            OpenStackResourceAssignment(message_content_json)
            OpenStackResourceStitching(message_content_json)
            reply_content_json = OpenStackReplyGenerating(message_content_json)
            reply_content = json.dumps(reply_content_json)
            print DEBUG_HEADER, "Pushing the message into the %s..." % (communication_queue_name)
            PushToQueue(communication_queue_name, reply_content)

        elif is_available == 'no':
            print DEBUG_HEADER, "The local resource is NOT available."
            message_content_json['action'] = 'forward'
            message_content = json.dumps(message_content_json)
            print DEBUG_HEADER, "Add the header 'action' into the message."
            pprint(message_content_json)
            print DEBUG_HEADER, "Pushing the message into the %s..." % (communication_queue_name)
            PushToQueue(communication_queue_name, message_content)

    elif message_type == 'reply_to_local':
        print DEBUG_HEADER, "This is a %s message." % (message_type)
        OpenStackResourceStitching(message_content_json)     

queue_channel.basic_consume(callback, queue=resource_management_queue_name, no_ack=True)
queue_channel.start_consuming()
