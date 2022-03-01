import networkx as nx

import sys

from os import listdir


def add_date_model(file,lines):
    model = nx.drawing.nx_agraph.read_dot(file)
    splitted = file.split("-")
    v1 = splitted[0].split("/")[2].split("T")[0]
    v2 = splitted[1].split("T")[0]
    v1 = v1.replace(".","_",3)
    v2 = v2.replace(".","_",3)


    
    v1_date = None
    v2_date = None
    for line in lines:
        if v1 in line:
            v1_date = line.split(" ")[0]
        if v2 in line:
            v2_date = line.split(" ")[0]

   

    model.graph["Date reference model"] = v1_date
    model.graph["Date updated model"] = v2_date
    nx.drawing.nx_agraph.write_dot(model,file)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file1 = open('release-dates.txt', 'r')
        lines = file1.readlines()
        for file in listdir(sys.argv[1]):
            add_date_model(sys.argv[1] + file,lines)
        file1.close()
