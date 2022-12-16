from argparse import ArgumentParser
import json
import os
import random
import sys
import time
import numpy
import pika
from velocities_generator import *
from fluids_generator import *
import coordinates_generator
from termometer_generator import *

import logging
from datetime import date


class velocity_sensor:
    def __init__(self, id=0, current_velocity=0.0, current_fuel = 100, current_water = 100, current_oil = 100, current_tires_temperature = 40, current_engine_temperature = 70, time_between_trips = 30*60, time_speed = 1):#, message_speed = 1):
        self.id = id    #Vehicle ID
        self.current_velocity = current_velocity    #Initial Current velocity
        self.current_gear = 0   #Initial Current gear
        # self.velocity = {'inside_locality': ([0, 20, 40, 60],[0.05, 0.15, 0.33, 0.47]), 'outside_locality': ([0, 20, 40, 60, 80, 100],[0.03, 0.07, 0.12, 0.18, 0.38, 0.22]), 'highway': ([0, 20, 40, 60, 80, 100, 120, 140],[0.01, 0.05, 0.07, 0.10, 0.12, 0.20, 0.35, 0.10])}    #Max velocity for each type of road
        self.current_rpm = 0
        self.current_fuel = current_fuel
        self.current_water = current_water
        self.current_oil = current_oil
        self.current_coordinates = None
        self.current_trip = []

        self.engine_problem = False
        self.current_tires_pressure = 37
        self.current_tires_temperature = current_tires_temperature
        self.current_engine_temperature = current_engine_temperature

        self.current_lights = "OFF"

        self.time_between_trips = time_between_trips
        self.time_speed = time_speed
        # self.message_speed = message_speed



    def run(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        # connection = pika.BlockingConnection(pika.ConnectionParameters(host='172.19.0.3'))
        
        channel = connection.channel()
        channel2 = connection.channel()
        channel3 = connection.channel()
        channel4 = connection.channel()
        channel5 = connection.channel()
        channel6 = connection.channel()

        channel.queue_declare(queue='fluids') # if queue does not exist, create it
        channel2.queue_declare(queue='velocities') # if queue does not exist, create it
        channel3.queue_declare(queue='coordinates') # if queue does not exist, create it
        channel4.queue_declare(queue='lights_status') # if queue does not exist, create it
        channel5.queue_declare(queue='motor_status') # if queue does not exist, create it
        channel6.queue_declare(queue='tires_status') # if queue does not exist, create it

        while True:
            if self.current_trip == []:

                #Preciso de gerar uma nova viagem
                self.current_trip = coordinates_generator.generate_random_trip()


            if self.current_fuel == 0:

                #Tenho de abastecer e espero que alguem me traga o combustivel
                time.sleep(5*60/self.time_speed)

                randfuel = random.choice([i for i in range(20)], p=[i for i in range(20)])
                self.current_fuel += randfuel
                time.sleep(30/self.time_speed)  #Abastecendo

            elif self.current_fuel < 100:

                #Probabilidade de colocar combustivel
                somatorio = sum([i for i in range(100)])
                randnumber = numpy.random.choice([i for i in reversed(range(100))], p=[i/somatorio for i in range(100)])

                if randnumber > self.current_fuel: #Vou abastecer
                    
                    somatorio = sum([i for i in range(100-int(self.current_fuel))])
                    randfuel = numpy.random.choice([i for i in range(100-int(self.current_fuel))], p=[i/somatorio for i in range(100-int(self.current_fuel))])
                    self.current_fuel += randfuel
                    time.sleep(30/self.time_speed)  #Abastecendo

            
            if self.engine_problem:
                #Tenho de esperar o carro esfriar e que alguém o arranje
                time.sleep(10*60/self.time_speed)
                self.engine_problem = False
                self.current_engine_temperature = 70

            if self.current_lights == "DEAD":
                #Tenho de esperar o carro esfriar e que alguém o arranje
                time.sleep(1*60/self.time_speed)
                self.current_lights = "OFF"
                # print("Enviar mensagem de que as luzes estão a funcionar")
                message = {'id': self.id, 'timestamp': time.time(), 'lights': self.current_lights}
                channel4.basic_publish(exchange='', routing_key='lights_status', body=json.dumps(message))
                logger.debug(message)


            #Preciso de ligar o carro
            message = {'id': self.id, 'timestamp': time.time(), 'motor_status': "ON", 'motor_temperature': self.current_engine_temperature}
            channel5.basic_publish(exchange='', routing_key='motor_status', body=json.dumps(message))
            logger.debug(message)
            self.current_coordinates = self.current_trip.pop(0)
            #Preciso de mandar as coordenadas iniciais
            message = {'id': self.id, 'timestamp': time.time(), 'latitude': self.current_coordinates[0], 'longitude': self.current_coordinates[1]}
            channel3.basic_publish(exchange='', routing_key='coordinates', body=json.dumps(message))
            logger.debug(message)
            #Mandar também o estado dos pneus e das luzes
            message = {'id': self.id, 'timestamp': time.time(), 'tires_pressure': self.current_tires_pressure, 'tires_temperature': self.current_tires_temperature}
            channel6.basic_publish(exchange='', routing_key='tires_status', body=json.dumps(message))
            logger.debug(message)
            message = {'id': self.id, 'timestamp': time.time(), 'lights': self.current_lights}
            channel4.basic_publish(exchange='', routing_key='lights_status', body=json.dumps(message))
            logger.debug(message)
            

            i = 0
            while self.current_trip != []:
                i += 1


                #Enviar a temperatura dos pneus a cada 30 segundos
                if i % 30 == 0:

                    #Estado das luzes
                    if self.current_lights != "DEAD":
                        if random.uniform(0, 1) > 0.90: #Gerar novo estado
                            self.current_lights = numpy.random.choice(["OFF", "AVG", "MAX", "MIN", "DEAD"], p=[0.53, 0.37, 0.05, 0.03, 0.02])
                    #Enviar a mensagem
                    message = {'id': self.id, 'timestamp': time.time(), 'lights': self.current_lights}
                    channel4.basic_publish(exchange='', routing_key='lights_status', body=json.dumps(message))
                    logger.debug(message)



                    #Enviar a temperatura dos pneus
                    self.current_tires_pressure = tires_pressure(self.current_tires_pressure, self.current_velocity)
                    self.current_tires_temperature = tires_temperature(self.current_tires_temperature, self.current_velocity)

                    #Enviar a temperatura do motor
                    self.current_engine_temperature, self.engine_problem = engine_temperature(self.current_engine_temperature, self.current_rpm, self.engine_problem)

                    # print("Pressao: ", self.current_tires_pressure, "Pneus: ", self.current_tires_temperature, "Motor: ", self.current_engine_temperature)
                    message = {'id': self.id, 'timestamp': time.time(), 'tires_pressure': self.current_tires_pressure, 'tires_temperature': self.current_tires_temperature}
                    channel6.basic_publish(exchange='', routing_key='tires_status', body=json.dumps(message))
                    logger.debug(message)
                    
                    
                    if self.engine_problem and self.current_engine_temperature > 105:
                        break


                if self.current_fuel <= 0:
                    break
                    #Espero um tempo random e volto a gerar dados, abastecendo

                
                print("Coordenadas atuais:", self.current_coordinates)
                print("Proxima coordenada:", self.current_trip[0])
                distancia = distance(self.current_coordinates[0], self.current_coordinates[1], self.current_trip[0][0], self.current_trip[0][1])  #m/s = #distancia/1000km*3600 = km/h
                velocidade_media = distancia/1000*(3600)  #Velocidade média em km/h naquele segundo
                aceleracao = (velocidade_media-self.current_velocity)/5 #5 pois é metade de 1 segundo que seriam 10 iterações, ou seja, 5 segundos para igualar e 5 segundos para afastar de forma a que a velocidade média seja coerente
                if abs(aceleracao) > 4:  #Alguma coordenada acabou não sendo gerada
                    self.current_velocity = velocidade_media
                    aceleracao = 0

                self.current_gear = gear(self.current_velocity, aceleracao, self.current_gear)

                
                for j in range(10):
                    if self.current_velocity + aceleracao <= 0:
                        self.current_velocity = 0
                    else:
                        self.current_velocity += aceleracao
                    self.current_rpm = generate_rpm(self.current_velocity, self.current_gear)

                    if j == 0:

                        self.current_fuel = generate_fuel(self.current_fuel, self.current_gear, self.current_rpm)

                        
                        self.current_water = generate_water(self.current_water)
                        

                        self.current_oil = generate_oil(self.current_oil)

                        message = {'id': self.id, 'timestamp': time.time(), 'current_fuel': round(self.current_fuel/100, 2), 'current_water': round(self.current_water/100,2), 'current_oil': round(self.current_oil/100,2)}
                        channel.basic_publish(exchange='', routing_key='fluids', body=json.dumps(message))
                        logger.debug(message)
                        

                    
                    message = {'id': self.id, 'timestamp': time.time(), 'velocity': round(self.current_velocity,2), 'gear': round(self.current_gear,2), 'rpm': round(self.current_rpm,2)}
                    channel2.basic_publish(exchange='', routing_key='velocities', body=json.dumps(message))
                    logger.debug(message)
                    time.sleep(0.1)
                    
                

                    
                self.current_coordinates = self.current_trip.pop(0)
                #Não é preciso enviar a cada segundo, apenas quando o carro liga e desliga, de forma a não ter demasiadas coordenadas na base de dados e a ser mais fácil gerar o percurso no mapa do front-end
            

            #Acabei a minha viagem, vou esperar um coto antes de voltar a fazer outra
            self.current_trip = []
            message = {'id': self.id, 'timestamp': time.time(), 'latitude': self.current_coordinates[0], 'longitude': self.current_coordinates[1]}
            channel3.basic_publish(exchange='', routing_key='coordinates', body=json.dumps(message))
            logger.debug(message)
            message = {'id': self.id, 'timestamp': time.time(), 'motor_status': "OFF", 'motor_temperature': self.current_engine_temperature}
            channel5.basic_publish(exchange='', routing_key='motor_status', body=json.dumps(message))
            logger.debug(message)

            somatorio = sum([i for i in range(self.time_speed)])
            randnumber = numpy.random.choice([i for i in range(self.time_speed)], p=[i/somatorio for i in range(self.time_speed)])
            time.sleep(randnumber/ self.time_speed)    #Aguardar time_speed antes de voltar a fazer uma viagem



if __name__ == '__main__':
    parse = ArgumentParser()
    parse.add_argument('-id', '--id', default=0, type=int, help='id from running car')
    parse.add_argument('-f', '--fuel', default=100, type=float, help='Current fuel of the car')
    parse.add_argument('-w', '--water', default=100, type=float, help='Current water of the car')
    parse.add_argument('-o', '--oil', default=100, type=float, help='Current oil of the car')
    parse.add_argument('-tt', '--time_trips', default=30*60, type=float, help='Time between trips')
    parse.add_argument('-ts', '--time_speed', default=1, type=float, help='Time speed when stopped')
    # parse.add_argument('-tm', '--time_message', default=1, type=float, help='Time to send a new message')
    args = parse.parse_args()
    try:
        v0 = velocity_sensor(id=args.id, current_velocity=0, current_fuel=args.fuel, current_water=args.water, current_oil=args.oil, time_between_trips=args.time_trips, time_speed=args.time_speed)#, message_speed=args.time_message)

        # Create and configure logger
        today = date.today()
        logging.basicConfig(filename="logs/logfile_" + str(today) + ".log",
                            format='%(asctime)s %(message)s',
                            filemode='a')
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        v0.run()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)