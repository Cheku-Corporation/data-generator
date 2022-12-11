#O que falta gerar?

#Temperatura do motor   - 85-90, começa a ser preocupante apartir dos 105 -Done
#Estado do motor    -   Ligado ou desligado -Done

#Estado das luzes   - Done

#Temperatura dos pneus - Done
#Pressão dos pneus - Done

import random


#Temperatura dos pneus  -  50-70, começa a ser preocupante apartir dos 90
def tires_temperature(tires_temperature, speed):
    if speed <= 50:
        if tires_temperature < 55:
            tires_temperature += 1
        else:
            tires_temperature -= 1
    elif speed <= 75:
        if tires_temperature < 60:
            tires_temperature += 1
        else:
            tires_temperature -= 1
    elif speed <= 100:
        if tires_temperature < 65:
            tires_temperature += 1
        else:
            tires_temperature -= 1
    elif speed <= 130:
        if tires_temperature < 70:
            tires_temperature += 1
        else:
            tires_temperature -= 1
    elif speed >= 130:
        if tires_temperature < 75:
            tires_temperature += 1
        else:
            tires_temperature -= 1

    return tires_temperature


def engine_temperature(engine_temperature, current_rpm, problem = False):
    if problem:
        engine_temperature += 2
        return engine_temperature, problem
    
    if current_rpm > 2500:
        if random.uniform(0, 1) > 0.95:
            problem = True
        if engine_temperature < 95:
            engine_temperature += 1
    else:
        engine_temperature += 1

    return engine_temperature, problem




#2.5 bars
def tires_pressure(tires_pressure, speed):
    if speed <= 50:
        tires_pressure -= 0.003
    elif speed <= 75:
        tires_pressure -= 0.005
    elif speed <= 100:
        tires_pressure -= 0.007
    elif speed <= 130:
        tires_pressure -= 0.009
    else:
        tires_pressure -= 0.01

    return tires_pressure