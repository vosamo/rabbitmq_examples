#!/usr/bin/env python
# coding=utf-8
import pika
import sys

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='direct_logs', type='direct')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

serverities = sys.argv[1:]
if not serverities:
    sys.stderr.write("Usage:%s [info] [warning] [error]\n" % sys.argv[0])
    sys.exit(1)

for serverity in serverities:
    channel.queue_bind(exchange='direct_logs', queue=queue_name, routing_key=serverity)

print "[*]Waiting for logs.To exit press CTRL+C"

def call_back(ch, method, properties, body):
    print "[x] %r:%r" % (method.routing_key, body)

channel.basic_consume(call_back, queue=queue_name, no_ack=True)
channel.start_consuming()
