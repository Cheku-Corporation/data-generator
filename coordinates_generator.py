from os import listdir
from os.path import isfile, join
import random

def generate_random_trip():

    path = "csv_trips/"
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]

    trip = random.choice(onlyfiles)
    f = open(path + trip, "r")

    caminho = []
    for line in f.readlines():
        caminho.append((float(line.split(",")[0].strip()), float(line.split(",")[1].strip())))
    
    return caminho