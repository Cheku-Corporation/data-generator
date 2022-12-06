#Fluids generators
import random


def generate_fuel(self, fuel, gear, rpm):
    if gear != 0:
        fuel -= (rpm / gear  /10000)
    if fuel <= 0:
        fuel = 0
    
    return fuel

def generate_water(self, water):
    water -= random.uniform(0, 0.01)
    if water <= 0:
        water = 0
    
    return water


def generate_oil(self, oil):
    oil -= random.uniform(0, 0.001)
    if oil <= 0:
        oil = 0
    
    return oil