#!/usr/bin/env python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='hello')

for i in range(0,10):
    channel.basic_publish(exchange='',
                            routing_key='hello',
                            body='Hello World! ' + str(i))

    print " [x] Send one message!"

# Delete the queue
#channel.queue_delete(queue='hello')

connection.close()
