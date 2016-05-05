#!/usr/bin/env python
# coding=utf-8
import pika
import sys

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='topic_logs', type='topic')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

binding_keys = sys.argv[1:]
if not binding_keys:
    sys.stderr.write("Usage:%s [info] [warning] [error]\n" % sys.argv[0])
    sys.exit(1)

for binding_key in binding_keys:
    channel.queue_bind(exchange='topic_logs', queue=queue_name, routing_key=binding_key)

print "[*]Waiting for logs.To exit press CTRL+C"

def call_back(ch, method, properties, body):
    print "[x] %r:%r" % (method.routing_key, body)

channel.basic_consume(call_back, queue=queue_name, no_ack=True)
channel.start_consuming()
