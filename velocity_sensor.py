import json
import os
import random
import sys
import time
import numpy
import pika

class velocity_sensor:
    def __init__(self, id=0, current_velocity=0.0, max_acceleration = 3.3):
        self.id = id    #Vehicle ID
        self.current_velocity = current_velocity    #Initial Current velocity
        self.max_acceleration = max_acceleration    #Maximum acceleration in km/0.1s^2
        self.velocity = {'inside_locality': ([0, 20, 40, 60],[0.05, 0.15, 0.33, 0.47]), 'outside_locality': ([0, 20, 40, 60, 80, 100],[0.03, 0.07, 0.12, 0.18, 0.38, 0.22]), 'highway': ([0, 20, 40, 60, 80, 100, 120, 140],[0.01, 0.05, 0.07, 0.10, 0.12, 0.20, 0.35, 0.10])}    #Max velocity for each type of road



    def run(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='car_' + str(self.id)) # if queue does not exist, create it

        while True:
            road_type = numpy.random.choice(list(self.velocity.keys()), p=[0.5, 0.3, 0.2]) #Probability of each type of road
            #Com o tipo de rua, gerar dados aleatórios durante 5 minutos
            for i in range(30):
                #Gerar velocidade máxima aleatória e utiliza-la por 10 segundos
                max_velocity = numpy.random.choice(self.velocity[road_type][0], p=self.velocity[road_type][1]) #Probability of each type of road
                print("Max velocity " + str(max_velocity))
                for i in range(100):
                    time.sleep(0.1)
                    if self.current_velocity > max_velocity:
                        self.current_velocity -= random.uniform(0, self.max_acceleration)
                    else:
                        aceleracao = random.uniform(0, self.max_acceleration)
                        probabilidade = random.uniform(0, 1)    #Probabilidade de acelerar ou reduzir
                        if probabilidade < 0.7:
                            if max_velocity != 0:
                                self.current_velocity += aceleracao
                            else:
                                if self.current_velocity - aceleracao < 0:
                                    max_velocity = 0
                                else:
                                    max_velocity -= aceleracao
                        else:
                            if self.current_velocity - aceleracao < 0:
                                self.current_velocity = 0
                            else:
                                self.current_velocity -= aceleracao
                    message = {'tag': 'velocity', 'timestamp': time.time(), 'velocity': self.current_velocity}
                    channel.basic_publish(exchange='', routing_key='car_' + str(self.id), body=json.dumps(message))
                    # print("Current velocity: ", current_velocity)
        connection.close()


if __name__ == '__main__':
    try:
        v0 = velocity_sensor(0, current_velocity=50, max_acceleration=3.3)
        v0.run()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)