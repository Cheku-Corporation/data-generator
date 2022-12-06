# Isto é mais um teste para verificar se o código está a funcionar

import pika, sys, os

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel2 = connection.channel()

    channel.queue_declare(queue='velocities') # if queue does not exist, create it
    channel2.queue_declare(queue='fluids') # if queue does not exist, create it

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)

    channel.basic_consume(queue='velocities', on_message_callback=callback, auto_ack=True)   #Hardcoded para testar o carro 0
    channel2.basic_consume(queue='fluids', on_message_callback=callback, auto_ack=True)   #Hardcoded para testar o carro 0

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
    channel2.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

