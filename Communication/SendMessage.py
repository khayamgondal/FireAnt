#!/usr/bin/python
import sys,os,ConfigParser,socket

#----------------------------------
# Fireant working environment setup
#----------------------------------
config = ConfigParser.ConfigParser()
home_directory = os.path.expanduser('~')
config.read(home_directory + '/.fireantenv')
folder_path = config.get('directory','path')
sys.path.insert(0, folder_path+'Common')
from ReadConfig import ReadConfig

DEBUG_MODULE = '[Communication]'
DEBUG_SCRIPT = '[SendMessage]'
DEBUG_HEADER = DEBUG_MODULE + DEBUG_SCRIPT

#------------------------
# Read configuration file
#------------------------
config = ReadConfig()
listen_port = int(config.get('MessageManagement', 'listen_port'))

#-----------------------
# Function: send message
#-----------------------
def SendMessage(destinations, message_content):
    send_success_set = []
    for direction_ip in destinations:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((direction_ip,listen_port))
            client_socket.send(message_content)
            print DEBUG_HEADER, 'Sent a message to %s.' % (direction_ip)
            client_socket.close()
            send_success_set.append(direction_ip)
        except Exception,e:
            print DEBUG_HEADER, "====== SOMETHING IS WRONG WITH %s. EXCEPTION TYPE IS %s. ======" \
                     % (direction_ip, e)
    print DEBUG_HEADER, "The send_success_set is ", send_success_set
    return send_success_set
