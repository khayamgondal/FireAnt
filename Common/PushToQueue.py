#!/usr/bin/python
import pika

def PushToQueue(queue_name, message_content):
    queue_connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    queue_channel = queue_connection.channel()
    queue_channel.queue_declare(queue = queue_name) #create a rabbitmq FIFO queue
    queue_channel.basic_publish(exchange='',
                                routing_key=queue_name,
                                body=message_content)
    queue_channel.close()
    queue_connection.close()
    return
