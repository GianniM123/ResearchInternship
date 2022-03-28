import networkx as nx

import sys
import csv
import ast
from os import listdir

def extract_info_from_model(file):
    
    model = nx.drawing.nx_agraph.read_dot(file)
    return_dict = {}
    splitted = file.split("-")
    v3 = splitted[3].split(".")[0]
    return_dict["reference version"] = splitted[0].split("/")[3]
    return_dict["updated version"] = splitted[1]
    return_dict["SMT solver"] =  model.graph["Solver"]
    return_dict["iteration"] =  v3
    return_dict["incoming time"] =  model.graph["Incoming time"]
    return_dict["outgoing time"] =  model.graph["Outgoing time"] 
    return_dict["f-measure"] =  model.graph["f-measure"]
    return_dict["precision"] =  model.graph["precision"]
    return_dict["recall"] =  model.graph["recall"]
    return_dict["reference model: number of states"] = ast.literal_eval(model.graph["Reference"])["States"]
    return_dict["reference model: number of transitions"] = ast.literal_eval(model.graph["Reference"])["Transitions"]
    return_dict["updated model: number of states"] = ast.literal_eval(model.graph["Updated"])["States"]
    return_dict["updated model: number of transitions"] = ast.literal_eval(model.graph["Updated"])["Transitions"]
    return_dict["output model: number of states"] = ast.literal_eval(model.graph["Output"])["States"]
    return_dict["output model: number of transitions"] = ast.literal_eval(model.graph["Output"])["Transitions"]

    return return_dict

if __name__ == "__main__":
    if len(sys.argv) > 1:
        dict_list = []
        for file in listdir(sys.argv[1]):
            dict_list.append(extract_info_from_model(sys.argv[1] + file))
        res = sys.argv[1].split("/")[2]
        with open('results_' + res + '.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = dict_list[0].keys())
            writer.writeheader()
            writer.writerows(dict_list)
