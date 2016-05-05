#!/usr/bin/env python
import sys

import time
import uuid
import json
import pika

if "../public/" not in sys.path:
    sys.path.append("../public/")

import constants

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()

channel.queue_declare(queue=constants.QUEUE_WORKER, durable=True)
channel.basic_qos(prefetch_count=1)

class FibonacciRpcClient(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='localhost'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, struuid):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key=constants.QUEUE_RPC,
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         ),
                                   body=str(struuid))

        while self.response is None:
            self.connection.process_data_events()
        return str(self.response)


def callback(ch, method, properties, body):
    """
    Process the main business.After the action, send out the message to rpc_server.
    """
    print(" [x] Received %r" % body)

    # send the result to rpc_server.
    strtask = str(body)
    one_task = dict(json.loads(strtask))
    onekey = one_task.keys()[0]

    task_detail = one_task[onekey]

    # kernel of process.
    time.sleep(len(onekey))

    # update the task state.
    task_detail[constants.TASK_STATE] = constants.TASK_STATE_DONE
    task_detail[constants.TASK_COMMENT] = "Just finished one task [%s]." % onekey
    one_task[onekey] = task_detail

    taskinfo = json.dumps(one_task)

    print ("New Task: %s\n"% onekey)

    fibonacci_rpc = FibonacciRpcClient()

    print(" [x] Reporting uuid(%s)" % onekey)
    response = fibonacci_rpc.call(taskinfo)
    #
    print(" [x] Done")
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_consume(callback,
                      queue=constants.QUEUE_WORKER)
                      #queue='task_queue',
                      # no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

