import random
import time
import numpy
import pika
import math

max_acceleration = 3.3  #Maximum acceleration in km/0.1s^2
current_velocity = 0.0  #Initial Current velocity

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='velocity') # if queue does not exist, create it

#channel.basic_publish(exchange='', routing_key='velocity', body='120')
velocity = {'inside_locality': ([0, 20, 40, 60],[0.05, 0.15, 0.33, 0.47]), 'outside_locality': ([0, 20, 40, 60, 80, 100],[0.03, 0.07, 0.12, 0.18, 0.38, 0.22]), 'highway': ([0, 20, 40, 60, 80, 100, 120, 140],[0.01, 0.05, 0.07, 0.10, 0.12, 0.20, 0.35, 0.10])}    #Max velocity for each type of road

while True:
    road_type = numpy.random.choice(list(velocity.keys()), p=[0.5, 0.3, 0.2]) #Probability of each type of road
    #Com o tipo de rua, gerar dados aleatórios durante 5 minutos
    for i in range(30):
        #Gerar velocidade máxima aleatória e utiliza-la por 10 segundos
        max_velocity = numpy.random.choice(velocity[road_type][0], p=velocity[road_type][1]) #Probability of each type of road
        print("Max velocity " + str(max_velocity))
        for i in range(100):
            time.sleep(0.1)
            if current_velocity > max_velocity:
                current_velocity -= random.uniform(0, max_acceleration)
            else:
                aceleracao = random.uniform(0, max_acceleration)
                probabilidade = random.uniform(0, 1)    #Probabilidade de acelerar ou reduzir
                if probabilidade < 0.7:
                    if max_velocity != 0:
                        current_velocity += aceleracao
                    else:
                        if current_velocity - aceleracao < 0:
                            max_velocity = 0
                        else:
                            max_velocity -= aceleracao
                else:
                    if current_velocity - aceleracao < 0:
                        current_velocity = 0
                    else:
                        current_velocity -= aceleracao
            # print("Current velocity: ", current_velocity)
            
            channel.basic_publish(exchange='', routing_key='velocity', body=str(current_velocity))

connection.close()




#Gerar dados:

# 1 - Escolher um tipo de local e utiliza-lo por 5 minutos
# 2 - Escolher um máximo de velocidade aleatório entre as possíveis
# 3 - Gerar uma aceleração aleatoria entre -max_acceleration e max_acceleration
# 4 - Alterar o valor, desde que não ultrapasse o máximo de velocidade, nem o mínimo de 0