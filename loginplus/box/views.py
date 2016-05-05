"""
The main module for processing the view-related tasks.
"""
import sys
import uuid
import json

import pika

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from public import constants

__author__ = 'shaomingwu@inspur.com'

class TaskNew(APIView):
    """
    Create a new task.
    ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']
    """
    def get(self, request, format=None):
        """
        Create one task.
        """
        connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
        channel = connection.channel()

        channel.queue_declare(queue=constants.QUEUE_WORKER, durable=True)
        channel.basic_qos(prefetch_count=1)

        # Prepare one task dict item.
        one_task = {}

        task_uuid = str(uuid.uuid4())
        task_detail = {}

        task_detail[constants.TASK_STATE] = constants.TASK_STATE_UNKNOWN
        task_detail[constants.TASK_COMMENT] = "Just created one task [%s]" % task_uuid

        one_task[task_uuid] = task_detail

        # convert the task item object into string format.
        message = json.dumps(one_task)

        channel.basic_publish(exchange='',
                              routing_key=constants.QUEUE_WORKER,
                              body=message,
                              properties=pika.BasicProperties(
                                 delivery_mode = 2, # make message persistent
                              ))
        print(" [x] Sent %r" % message)

        connection.close()

        return Response("Created task:[%s]." % message, status=status.HTTP_200_OK)


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

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key=constants.QUEUE_RPC,
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         ),
                                   body=str(n))
        while self.response is None:
            self.connection.process_data_events()
        return str(self.response)


class TaskState(APIView):
    """
    Create a new task.
    ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']
    """
    def get(self, request, taskid, format=None):
        """
        Create one task.
        """
        fibonacci_rpc = FibonacciRpcClient()

        # Prepare one task dict item.
        one_task = {}

        task_uuid = taskid
        task_detail = {}

        one_task[task_uuid] = task_detail

        # convert the task item object into string format.
        message = json.dumps(one_task)

        print(" [x] Requesting the status of task [%s]" % taskid)
        response = fibonacci_rpc.call(message)
        print(" [.] Got %s" % response)

        return Response(repr(response), status=status.HTTP_200_OK)