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


#Channels:
#car_queue
#fluids
#velocities
#coordinates
#lights_status
#motor_status
#tires_status





class velocity_sensor:
    def __init__(self, id=0, current_velocity=0.0, current_fuel = 100, current_water = 100, current_oil = 100, current_tires_temperature = 40, current_engine_temperature = 70):
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
                time.sleep(5*60)

                randfuel = random.choice([i for i in range(20)], p=[i for i in range(20)])
                self.current_fuel += randfuel
                time.sleep(30)  #Abastecendo

            elif self.current_fuel < 100:

                #Probabilidade de colocar combustivel
                randnumber = random.choice([i for i in reversed(range(100))], p=[i for i in range(100)])

                if randnumber > self.current_fuel: #Vou abastecer
                    
                    randfuel = random.choice([i for i in range(100-int(self.current_fuel))], p=[i for i in range(100-int(self.current_fuel))])
                    self.current_fuel += randfuel
                    time.sleep(30)  #Abastecendo

            
            if self.engine_problem:
                #Tenho de esperar o carro esfriar e que alguém o arranje
                time.sleep(10*60)
                self.engine_problem = False
                self.current_engine_temperature = 70

            if self.current_lights == "DEAD":
                #Tenho de esperar o carro esfriar e que alguém o arranje
                time.sleep(1*60)
                self.current_lights = "OFF"
                # print("Enviar mensagem de que as luzes estão a funcionar")
                message = {'id': self.id, 'timestamp': time.time(), 'lights': self.current_lights}
                channel4.basic_publish(exchange='', routing_key='lights_status', body=json.dumps(message))


            #Preciso de ligar o carro
            message = {'id': self.id, 'timestamp': time.time(), 'motor_status': "ON", 'motor_temperature': self.current_engine_temperature}
            channel5.basic_publish(exchange='', routing_key='motor_status', body=json.dumps(message))
            

            for i, cam in enumerate(self.current_trip):

                if i == 0:
                    self.current_coordinates = self.current_trip[i]
                    continue

                #Posso é acrescentar aqui uma probabilidade de o carro parar para fazer abastecimentos
                #Uma probabilidade de trocar o estado em que as luzes estão

                #De 20 em 20 segundos, gerar um estado de luzes novo
                if i % 30 == 0:
                    if self.current_lights != "DEAD":
                        if random.uniform(0, 1) > 0.90: #Gerar novo estado
                            self.current_lights = numpy.random.choice(["OFF", "AVG", "MAX", "MIN", "DEAD"], p=[0.53, 0.37, 0.05, 0.03, 0.02])
                    #Enviar a mensagem
                    # print("Luzes: ", self.current_lights)
                    message = {'id': self.id, 'timestamp': time.time(), 'lights': self.current_lights}
                    channel4.basic_publish(exchange='', routing_key='lights_status', body=json.dumps(message))
                    


                #Enviar a temperatura dos pneus a cada 30 segundos
                if i % 30 == 0:
                    #Enviar a temperatura dos pneus
                    self.current_tires_pressure = tires_pressure(self.current_tires_pressure, self.current_velocity)
                    self.current_tires_temperature = tires_temperature(self.current_tires_temperature, self.current_velocity)

                    #Enviar a temperatura do motor
                    self.current_engine_temperature, self.engine_problem = engine_temperature(self.current_engine_temperature, self.current_rpm, self.engine_problem)

                    # print("Pressao: ", self.current_tires_pressure, "Pneus: ", self.current_tires_temperature, "Motor: ", self.current_engine_temperature)
                    message = {'id': self.id, 'timestamp': time.time(), 'tires_pressure': self.current_tires_pressure, 'tires_temperature': self.current_tires_temperature}
                    channel6.basic_publish(exchange='', routing_key='tires_status', body=json.dumps(message))
                    
                    
                    if self.engine_problem and self.current_engine_temperature > 105:
                        message = {'id': self.id, 'timestamp': time.time(), 'motor_status': "OFF", 'motor_temperature': self.current_engine_temperature}
                        channel5.basic_publish(exchange='', routing_key='motor_status', body=json.dumps(message)) 
                        break


                if self.current_fuel <= 0:
                    message = {'id': self.id, 'timestamp': time.time(), 'motor_status': "OFF", 'motor_temperature': self.current_engine_temperature}
                    channel5.basic_publish(exchange='', routing_key='motor_status', body=json.dumps(message))
                    break
                    #Espero um tempo random e volto a gerar dados, abastecendo

                

                distancia = distance(self.current_coordinates[0], self.current_coordinates[1], cam[0], cam[1])  #m/s = #distancia/1000km*3600 = km/h
                velocidade_media = distancia/1000*3600  #Velocidade média naquele segundo
                aceleracao = (velocidade_media-self.current_velocity)/5  #5 pois é metade de 1 segundo que seriam 10 iterações, ou seja, 5 segundos para igualar e 5 segundos para afastar de forma a que a velocidade média seja coerente
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
                        # if current_oil <= 0.7:  #Aos 0.8 devia ser gerado um aviso no spring boot
                        #Aqui é como a current_water, a qualquer altura pode ser abastecido

                        # print({'timestamp': time.time(), 'current_fuel': round(self.current_fuel/100, 2), 'current_water': round(self.current_water/100,2), 'current_oil': round(self.current_oil/100,2)})
                        message = {'id': self.id, 'timestamp': time.time(), 'current_fuel': round(self.current_fuel/100, 2), 'current_water': round(self.current_water/100,2), 'current_oil': round(self.current_oil/100,2)}
                        channel.basic_publish(exchange='', routing_key='fluids', body=json.dumps(message))
                        

                    
                    message = {'id': self.id, 'timestamp': time.time(), 'velocity': round(self.current_velocity,2), 'gear': round(self.current_gear,2), 'rpm': round(self.current_rpm,2)}
                    channel2.basic_publish(exchange='', routing_key='velocities', body=json.dumps(message))
                    time.sleep(0.1)
                    
                

                    
                self.current_coordinates = self.current_trip[i]
                message = {'id': self.id, 'timestamp': time.time(), 'coordinates': self.current_coordinates}
                channel3.basic_publish(exchange='', routing_key='coordinates', body=json.dumps(message))

            

            #Acabei a minha viagem, vou esperar um coto antes de voltar a fazer outra
            self.current_trip = []
            message = {'id': self.id, 'timestamp': time.time(), 'motor_status': "OFF", 'motor_temperature': self.current_engine_temperature}
            channel5.basic_publish(exchange='', routing_key='motor_status', body=json.dumps(message))
            time.sleep(5*60)    #Aguardar 5 minutos antes de voltar a fazer uma viagem



if __name__ == '__main__':
    parse = ArgumentParser()
    parse.add_argument('-id', '--id', default=0, type=int, help='id from running car')
    parse.add_argument('-f', '--fuel', default=100, type=int, help='Current fuel of the car')
    parse.add_argument('-w', '--water', default=100, type=int, help='Current water of the car')
    parse.add_argument('-o', '--oil', default=100, type=int, help='Current oil of the car')
    args = parse.parse_args()
    try:
        v0 = velocity_sensor(id=args.id, current_velocity=0, current_fuel=args.fuel, current_water=args.water, current_oil=args.oil)
        v0.run()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


        # while True:
        #     road_type = numpy.random.choice(list(self.velocity.keys()), p=[0.5, 0.3, 0.2]) #Probability of each type of road
        #     #Com o tipo de rua, gerar dados aleatórios durante 5 minutos
        #     max_velocity = None
        #     for i in range(30):
                
        #         #Check if car was stopped
        #         if max_velocity == 0:
        #             previous = True
        #         else:
        #             previous = False
                
        #         #Gerar a mudança
        #         self.current_gear = generate_gear(self, max_velocity, previous)

        #         #Gerar velocidade máxima aleatória e utiliza-la por 10 segundos
        #         max_velocity = numpy.random.choice(self.velocity[road_type][0], p=self.velocity[road_type][1]) #Probability of each type of road
        #         for i in range(100):
        #             time.sleep(0.1)

        #             #Generate current velocity, and current gear
        #             self.current_velocity = generate_velocity(self, max_velocity)
        #             self.current_rpm = generate_rpm(self, self.current_gear)
        #             if i%10 == 0:
        #                 self.current_fuel = generate_fuel(self, self.current_fuel, self.current_gear, self.current_rpm)
        #                 self.current_water = generate_water(self, self.current_water)
        #                 self.current_oil = generate_oil(self, self.current_oil)
        #                 message = {'id': self.id, 'timestamp': time.time(), 'current_fuel': round(self.current_fuel/100, 2), 'current_water': round(self.current_water/100,2), 'current_oil': round(self.current_oil/100,2)}
        #                 channel.basic_publish(exchange='', routing_key='fluids', body=json.dumps(message))
                
                    
        #             message = {'id': self.id, 'timestamp': time.time(), 'velocity': round(self.current_velocity,2), 'gear': round(self.current_gear,2), 'rpm': round(self.current_rpm,2)}
        #             channel.basic_publish(exchange='', routing_key='velocities', body=json.dumps(message))
        #             # print("Current velocity: ", current_velocity)
        # connection.close()