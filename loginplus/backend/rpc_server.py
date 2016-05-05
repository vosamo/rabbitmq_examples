#!/usr/bin/env python
import sys
import json
import pika

if "../public/" not in sys.path:
    sys.path.append("../public/")

import constants

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))

channel = connection.channel()

channel.queue_declare(queue=constants.QUEUE_RPC)

# define a global variable for storing the task items.
g_taskdict = {}

def on_request(ch, method, props, body):
    """
    Process the request.
    """
    rst_dict = {}

    strtask = str(body)
    one_task = dict(json.loads(strtask))
    onekey = one_task.keys()[0]
    task_detail = dict(one_task[onekey])

    cur_key_list = g_taskdict.keys()

    if onekey in cur_key_list:
        if task_detail:
            g_taskdict[onekey] = task_detail
        else:
            rst_dict[onekey] = g_taskdict[onekey]
    else:
        if task_detail:
            g_taskdict[onekey] = task_detail
        else:
            rst_dict[onekey] = {constants.TASK_STATE: constants.TASK_STATE_UNKNOWN,
                                constants.TASK_COMMENT:"Not found."}

    taskinfo = json.dumps(rst_dict)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(taskinfo))
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(on_request, queue=constants.QUEUE_RPC)

print(" [x] Awaiting RPC requests")
channel.start_consuming()
