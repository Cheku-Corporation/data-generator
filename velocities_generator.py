#Velocities Generators
import math


def distance(lon1, lat1, lon2, lat2):
    R = 6371e3

    φ1 = lat1 * math.pi/180
    φ2 = lat2 * math.pi/180

    Δφ = (lat2-lat1) * math.pi/180
    Δλ = (lon2-lon1) * math.pi/180

    a = math.sin(Δφ/2) * math.sin(Δφ/2) + math.cos(φ1) * math.cos(φ2) * math.sin(Δλ/2) * math.sin(Δλ/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    d = R * c
    
    return d


def gear(current_velocity, aceleracao, gear):
    if aceleracao > 0:

        if current_velocity >= 85:
            return 6
        elif current_velocity >= 60:
            return 5
        elif current_velocity >= 40:
            return 4
        elif current_velocity >= 20:
            return 3
        elif current_velocity >= 10:
            return 2 
        else:
            return 1
    
    elif aceleracao < 0:

        if current_velocity <= 15:
            return 1
        elif current_velocity <= 20:
            return 2
        elif current_velocity <= 40:
            return 3
        elif current_velocity <= 60:
            return 4
        elif current_velocity <= 85:
            return 5
        else:
            return 6
    
    elif current_velocity == 0:

        return 0
        
    
    return gear


def generate_rpm(current_velocity, gear):

    if gear == 0:
        rpm = 900

    else:
        rpm = 900 + current_velocity / gear * 100
        
    
    return rpm