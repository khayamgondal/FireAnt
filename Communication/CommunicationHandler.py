#!/usr/bin/python
import pika,json,sys,os,ConfigParser,socket
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
sys.path.insert(0, folder_path+'AnalyticsEngine')
from AnalyticsEngine import *
sys.path.insert(0, folder_path+'Communication')
from SendMessage import SendMessage

DEBUG_MODULE = '[Communication]'
DEBUG_SCRIPT = '[CommunicationHandler]'
DEBUG_HEADER = DEBUG_MODULE + DEBUG_SCRIPT

#------------------------
# Read configuration file
#------------------------
config = ReadConfig()
communication_queue_name = config.get('Communication', 'message_queue_name')
listen_port = int(config.get('MessageManagement', 'listen_port'))

#-----------------------------------------
# Resource Management FIFO queue listening
#-----------------------------------------
queue_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
queue_channel = queue_connection.channel()
queue_channel.queue_declare(queue = communication_queue_name)

print DEBUG_HEADER, "Waiting for messages from the %s..." % (communication_queue_name)

def callback(channel, method, properties, body):
    print DEBUG_HEADER, "Received one message from the %s." % (communication_queue_name)
    print DEBUG_HEADER, "Received message content: "
    message_content = body
    message_content_json = json.loads(message_content)
    pprint(message_content_json)

    message_type = message_content_json['message_type']
    message_action = message_content_json['action']
    if (message_type == 'request_from_local') or (message_type == 'request_from_others'):
        message_uuid = message_content_json['request']['uuid']
        print DEBUG_HEADER, "This is a %s." % (message_type)

        if message_action == 'forward':
            hop_count = message_content_json['request']['resources'][0]['properties']['hop_count']
            print DEBUG_HEADER, "The current hop count is : ", hop_count
            if message_type == 'request_from_others':
                hop_count = hop_count - 1
                message_content_json['request']['resources'][0]['properties']['hop_count'] = hop_count

            if hop_count == 0:
                print DEBUG_HEADER, "The hop count is ZERO. Discard the received request."
            elif hop_count > 0:
                print DEBUG_HEADER, "Removing the headers..."
                del message_content_json['last_hop_ip']
                print DEBUG_HEADER, "'last_hop_ip' section was removed."
                #pprint(message_content_json)
                del message_content_json['message_type']
                print DEBUG_HEADER, "'message_type' section was removed."
                del message_content_json['action']
                print DEBUG_HEADER, "'action' section was removed."
                message_content = json.dumps(message_content_json)

                decision_forwarded_direction = ForwardDirectionCalculation(message_uuid)
                message_forward_type = message_content_json['request']['forward_type']
                print DEBUG_HEADER, "This is a %s message. " % (message_forward_type)
                if message_forward_type == 'unicast':
                    decision_forwarded_direction = \
                        SelectOpportunisticUnicastDirection(decision_forwarded_direction)
                elif message_forward_type == 'broadcast':
                    print DEBUG_HEADER, "Will broadcast to all neighbors except the incoming one."

                print DEBUG_HEADER, "Forwarding the message..."
                if decision_forwarded_direction is None:
                    print DEBUG_HEADER, "There is no direction to forward the message!"
                else:
                    send_success_set = SendMessage(decision_forwarded_direction, message_content)
                    if send_success_set != []:
                        #print DEBUG_HEADER, send_success_set
                        UpdateForwardedDirection(message_uuid, send_success_set)
                    else:
                        print DEBUG_HEADER, "No message was sent successfully to the next hop."
            

    elif message_type == 'reply_to_others':
        print DEBUG_HEADER, "This is a %s." % (message_type)
        
        request_uuid = message_content_json['reply']['request_uuid']
        decision_forwarded_direction = ReplyDirectionCalculation(request_uuid, message_content)
        
        print DEBUG_HEADER, "Removing the headers..."
        del message_content_json['last_hop_ip']
        print DEBUG_HEADER, "'last_hop_ip' section was removed."
        del message_content_json['message_type']
        print DEBUG_HEADER, "'message_type' section was removed."
        del message_content_json['action']
        print DEBUG_HEADER, "'action' section was removed."
        message_content = json.dumps(message_content_json)
        
        print DEBUG_HEADER, "Forwarding the message..."
        if decision_forwarded_direction is None:
            print DEBUG_HEADER, "There is no direction to forward the message!"
        else:
            send_success_set = SendMessage(decision_forwarded_direction, message_content)
            if send_success_set != []:
                print DEBUG_HEADER, send_success_set
                UpdateStatus(request_uuid, 'replied')
                UpdateForwardedDirection(request_uuid, send_success_set)
                if message_action == 'reply':
                    UpdateReplyContent(request_uuid, message_content)
            else:
                print DEBUG_HEADER, "No message was sent successfully to the next hop."
        
            

queue_channel.basic_consume(callback, queue=communication_queue_name, no_ack=True)
queue_channel.start_consuming()
