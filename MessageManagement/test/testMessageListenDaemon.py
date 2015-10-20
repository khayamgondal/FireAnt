#!/usr/bin/env python
import socket

client_socket = []
for i in range(0,20):
    client_socket.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
    client_socket[i].connect(('127.0.0.1',9999))
    client_socket[i].send("hello from socket " + str(i+1))
    
for i in range(0,10):
    client_socket[i].close()
