#!/usr/bin/env python
import socket,pika,sys,os,ConfigParser,json
#----------------------------------
# Fireant working environment setup
#----------------------------------
config = ConfigParser.ConfigParser()
home_directory = os.path.expanduser('~')
config.read(home_directory + '/.fireantenv')
folder_path = config.get('directory','path')
sys.path.insert(0, folder_path+'/Common')
from ReadConfig import ReadConfig

DEBUG_MODULE = "[MessageManagement]"
DEBUG_SCRIPT = "[MessageListenDaemon]"
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

#-----------------------
# Server socket creation
#-----------------------
# Create an INET, STREAM socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Receice messages from any address
server_socket.bind(("0.0.0.0", listen_port))
# The max connect requests
server_socket.listen(10)

#-----------------------
# Message cache creation
#-----------------------
message_cache_connection = pika.BlockingConnection(pika.ConnectionParameters(host = 'localhost'))
message_cache_channel = message_cache_connection.channel()
message_cache_channel.queue_declare(queue = message_cache_name) # create a rabbitmq FIFO queue

#---------------
# Listening loop
#---------------
while True:
    # Accept any incoming socket request
    print DEBUG_HEADER, "Waiting for incoming message..."
    (client_socket, client_address) = server_socket.accept()
    #print DEBUG_HEADER, client_socket, client_address
    print DEBUG_HEADER, "Got one connection from", client_address
    
    # Receive data from the socket
    client_data = client_socket.recv(2048)
    print DEBUG_HEADER, "Got one message from", client_address
    #print DEBUG_HEADER, client_data

    #--------------------
    # Message Formatting
    #--------------------
    # Insert last_hop to the json file
    last_hop_ip = client_address[0]
    print DEBUG_HEADER, last_hop_ip
    client_data_json = json.loads(client_data)
    client_data_json['last_hop_ip'] = last_hop_ip
    client_data = json.dumps(client_data_json)

    #---------------------------------------
    # Send the message to the message cache
    #---------------------------------------
    # Test: in case the connection is closed
    message_cache_connection = pika.BlockingConnection(pika.ConnectionParameters(host = 'localhost'))
    message_cache_channel = message_cache_connection.channel()
    message_cache_channel.queue_declare(queue = message_cache_name) # create a rabbitmq FIFO queue

    message_cache_channel.basic_publish(exchange='',
                                        routing_key=message_cache_name,
                                        body=client_data)
    print DEBUG_HEADER, "Sent one message to the Message Cache."

    client_socket.close()

server_socket.close()
message_cache_connection.close()
