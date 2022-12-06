#Velocities Generators
import random


def generate_velocity(self, max_velocity):
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
    
    return self.current_velocity
    

def generate_gear(self, max_velocity, previous):
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
    elif self.current_velocity < 15:
        gear = 2
    elif self.current_velocity < 30:
        gear = 3
    elif self.current_velocity < 50:
        gear = 4
    elif self.current_velocity < 80:
        gear = 5
    else:
        gear = 6
    
    
    return gear


def generate_rpm(self, gear):
    if gear == 0:
        rpm = 0
    else:
        rpm = 500 + self.current_velocity / gear * 100
    
    return rpm