file = input("Enter the file name: ")


f = open(file, "r")
w = open("csv_trips/" + file.split("/")[1], "w")


for i, line in enumerate(f.readlines()):

    if i == 0:
        continue

    if i != 1:
        w.write("\n")
        
    w.write(line.split(",")[2] + "," + line.split(",")[3])