#!/usr/bin/python
import pika

def DeleteQueue(queue_name):
    queue_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    queue_channel = queue_connection.channel()
    try:
        queue_channel.queue_delete(queue = queue_name)
        queue_channel.close()
        queue_connection.close()
    except:
        queue_connection.close()
    return
