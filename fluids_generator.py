#Fluids generators
import random


def generate_fuel(fuel, gear, rpm):

    if gear != 0 and gear != -1:
        fuel -= (rpm / gear  /10000)

    else:
        fuel -= (rpm / 10000)


    if fuel <= 0:
        fuel = 0
    
    
    return fuel

def generate_water(water):

    water -= random.uniform(0, 0.01)

    if water <= 0:
        water = 0
    

    return water


def generate_oil(oil):

    oil -= random.uniform(0, 0.001)

    if oil <= 0:
        oil = 0
    

    return oil