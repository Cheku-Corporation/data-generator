import json
import os
import random
import sys
import time
import numpy
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='car_end') # if queue does not exist, create it



message = "MEKIE MANO"
channel.basic_publish(exchange='', routing_key='car_end', body=json.dumps(message))

connection.close()
