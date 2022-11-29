import json
import os
import random
import sys
import time
import numpy
import pika


def generate_velocity(self, max_velocity, previous):
    #Calcular a mudança em que me encontro
    if self.current_velocity < 10:
        if max_velocity == 0:
            if self.current_velocity == 0:
                gear = 0
            else:
                if previous:
                    probabilidade = random.uniform(0, 1)    #Probabilidade de acelerar ou reduzir
                    if probabilidade < 0.7:
                        gear = 1
                    else:
                        gear = -1
                else:
                    gear = 1
        else:
            gear = 1
    elif self.current_velocity < 20:
        gear = 2
    elif self.current_velocity < 35:
        gear = 3
    elif self.current_velocity < 50:
        gear = 4
    elif self.current_velocity < 60:
        gear = 5
    else:
        gear = 6


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
                    self.current_velocity = 0
                else:
                    self.current_velocity -= aceleracao
        else:
            if self.current_velocity - aceleracao < 0:
                self.current_velocity = 0
                gear = 0
            else:
                self.current_velocity -= aceleracao
    
    return self.current_velocity, gear





class velocity_sensor:
    def __init__(self, id=0, current_velocity=0.0, current_gear = 0,max_acceleration = 3.3):
        self.id = id    #Vehicle ID
        self.current_velocity = current_velocity    #Initial Current velocity
        self.current_gear = current_gear
        self.max_acceleration = max_acceleration    #Maximum acceleration in km/0.1s^2
        self.velocity = {'inside_locality': ([0, 20, 40, 60],[0.05, 0.15, 0.33, 0.47]), 'outside_locality': ([0, 20, 40, 60, 80, 100],[0.03, 0.07, 0.12, 0.18, 0.38, 0.22]), 'highway': ([0, 20, 40, 60, 80, 100, 120, 140],[0.01, 0.05, 0.07, 0.10, 0.12, 0.20, 0.35, 0.10])}    #Max velocity for each type of road



    def run(self):
        # connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='172.19.0.3'))
        
        
        channel = connection.channel()
        channel.queue_declare(queue='car_' + str(self.id)) # if queue does not exist, create it

        while True:
            road_type = numpy.random.choice(list(self.velocity.keys()), p=[0.5, 0.3, 0.2]) #Probability of each type of road
            #Com o tipo de rua, gerar dados aleatórios durante 5 minutos
            max_velocity = None
            for i in range(30):
                
                #Check if car was stopped
                if max_velocity == 0:
                    previous = True
                else:
                    previous = False

                #Gerar velocidade máxima aleatória e utiliza-la por 10 segundos
                max_velocity = numpy.random.choice(self.velocity[road_type][0], p=self.velocity[road_type][1]) #Probability of each type of road
                for i in range(100):
                    time.sleep(0.1)

                    #Generate current velocity, and current gear
                    self.current_velocity, self.current_gear = generate_velocity(self, max_velocity, previous)
                
                    
                    message = {'tag': 'velocity', 'timestamp': time.time(), 'velocity': self.current_velocity, 'gear': self.current_gear}
                    channel.basic_publish(exchange='', routing_key='car_' + str(self.id), body=json.dumps(message))
                    # print("Current velocity: ", current_velocity)
        connection.close()


if __name__ == '__main__':
    try:
        v0 = velocity_sensor(0, current_velocity=50, current_gear=0, max_acceleration=3.3)
        v0.run()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
