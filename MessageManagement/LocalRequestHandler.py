#!/usr/bin/env python
import sys,socket,os,ConfigParser
#----------------------------------
# Fireant working environment setup
#----------------------------------
config = ConfigParser.ConfigParser()
home_directory = os.path.expanduser('~')
config.read(home_directory + '/.fireantenv')
folder_path = config.get('directory','path')
sys.path.insert(0, folder_path+'/Common')
from ReadConfig import ReadConfig

DEBUG_MODULE = '[MessageManagement]'
DEBUG_SCRIPT = '[LocalRequestHandler]'
DEBUG_HEADER = DEBUG_MODULE + DEBUG_SCRIPT

#------------------------
# Read configuration file
#------------------------
config = ReadConfig()
#print DEBUG_HEADER, config
listen_port = int(config.get('MessageManagement', 'listen_port'))
#print DEBUG_HEADER, listen_port

#--------------------------------
# Resource Description API caller
#--------------------------------
# Leave the space for future extension

#---------------------------------------------
# Send the message to Message Listening Daemon
#---------------------------------------------
message_path = sys.argv[1]
send_file = open(message_path,"rb")
send_data = send_file.read(2048)
#print DEBUG_HEADER, message_path
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1',listen_port))
client_socket.send(send_data)
print DEBUG_HEADER, 'Sent a local request to message listen daemon.'
client_socket.close()
