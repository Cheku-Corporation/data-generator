import json
import os
import random
import sys
import time
import numpy
import pika
from velocities_generator import *
from fluids_generator import *



class velocity_sensor:
    def __init__(self, id=0, current_velocity=0.0, current_gear = 0,max_acceleration = 3.3, current_rpm = 0, current_fuel = 100, current_water = 100, current_oil = 100):
        self.id = id    #Vehicle ID
        self.current_velocity = current_velocity    #Initial Current velocity
        self.current_gear = current_gear
        self.max_acceleration = max_acceleration    #Maximum acceleration in km/0.1s^2
        self.velocity = {'inside_locality': ([0, 20, 40, 60],[0.05, 0.15, 0.33, 0.47]), 'outside_locality': ([0, 20, 40, 60, 80, 100],[0.03, 0.07, 0.12, 0.18, 0.38, 0.22]), 'highway': ([0, 20, 40, 60, 80, 100, 120, 140],[0.01, 0.05, 0.07, 0.10, 0.12, 0.20, 0.35, 0.10])}    #Max velocity for each type of road
        self.current_rpm = current_rpm
        self.current_fuel = current_fuel
        self.current_water = current_water
        self.current_oil = current_oil



    def run(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        # connection = pika.BlockingConnection(pika.ConnectionParameters(host='172.19.0.3'))
        
        
        channel = connection.channel()
        channel.queue_declare(queue='car_queue') # if queue does not exist, create it

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
                
                #Gerar a mudança
                self.current_gear = generate_gear(self, max_velocity, previous)

                #Gerar velocidade máxima aleatória e utiliza-la por 10 segundos
                max_velocity = numpy.random.choice(self.velocity[road_type][0], p=self.velocity[road_type][1]) #Probability of each type of road
                for i in range(100):
                    time.sleep(0.1)

                    #Generate current velocity, and current gear
                    self.current_velocity = generate_velocity(self, max_velocity)
                    self.current_rpm = generate_rpm(self, self.current_gear)
                    if i%10 == 0:
                        self.current_fuel = generate_fuel(self, self.current_fuel, self.current_gear, self.current_rpm)
                        self.current_water = generate_water(self, self.current_water)
                        self.current_oil = generate_oil(self, self.current_oil)
                        message = {'id': self.id, 'timestamp': time.time(), 'current_fuel': round(self.current_fuel/100, 2), 'current_water': round(self.current_water/100,2), 'current_oil': round(self.current_oil/100,2)}
                        channel.basic_publish(exchange='', routing_key='fluids', body=json.dumps(message))
                
                    
                    message = {'id': self.id, 'timestamp': time.time(), 'velocity': round(self.current_velocity,2), 'gear': round(self.current_gear,2), 'rpm': round(self.current_rpm,2)}
                    channel.basic_publish(exchange='', routing_key='velocities', body=json.dumps(message))
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
