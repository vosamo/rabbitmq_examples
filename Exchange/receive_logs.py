#!/usr/bin/env python
# coding=utf-8
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='logs', type='fanout')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='logs', queue=queue_name)

print "[*]Waiting for logs.To exit press CTRL+C"

def call_back(ch, method, properties, body):
    print "[x]%r" % body

channel.basic_consume(call_back, queue=queue_name, no_ack=True)
channel.start_consuming()
