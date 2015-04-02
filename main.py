#!/usr/bin/env python

import time
import uuid
from multiprocessing import Process

import pika

EXCHANGE = 'issue349'
ROUTING_KEY = 'test.issue349'


class Consumer(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.consumer_channel = self.connection.channel()
        self.publisher_channel = self.connection.channel()
        self.consumer_channel.exchange_declare(exchange=EXCHANGE,
                                               type='topic',
                                               durable=True)
        result = self.consumer_channel.queue_declare(exclusive=True)
        queue = result.method.queue
        self.consumer_channel.basic_consume(self.callback, queue=queue)
        self.consumer_channel.queue_bind(exchange=EXCHANGE,
                                         queue=queue,
                                         routing_key=ROUTING_KEY)

    def publish(self, routing_key, message, properties={}):
        message_id = properties.pop('message_id', str(uuid.uuid4()))
        content_type = properties.pop('content_type', 'text/plain')
        timestamp = properties.pop('timestamp', int(time.time()))

        props = pika.BasicProperties(content_type=content_type,
                                     timestamp=timestamp,
                                     message_id=message_id,
                                     **properties)
        self.publisher_channel.basic_publish(EXCHANGE,
                                             routing_key,
                                             message,
                                             props)
        print 'PUBLISH:', message

    def callback(self, ch, meth, props, body):
        print 'CONSUME:', body
        ch.basic_ack(delivery_tag=meth.delivery_tag)
        self.publish(ROUTING_KEY, 'test')
        self.publish(ROUTING_KEY, 'test2')

    def run(self):
        self.consumer_channel.start_consuming()

if __name__ == '__main__':
    consumer = Consumer()
    process = Process(target=consumer.run)
    process.start()

    consumer.publish(ROUTING_KEY, 'blah')
