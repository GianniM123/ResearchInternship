import random
import math
from os import listdir

def read_pairs(file):
    '''Function for reading pairs from a file'''
    pairs = []
    with open(file, 'r') as f:
        lines = f.read().splitlines()
        for line in lines:
            if line[0] == "#":
                continue
            splitted = line.split(":")
            pairs.append((splitted[0],splitted[1]))
    return pairs

def write_pairs_to_file(pairs, file):
    with open(file, 'w') as f:
        for p in pairs:
            f.write(p[0] + ":" + p[1] + "\n")

if __name__ == "__main__":
    for file in listdir("."):
        split = file.split(".")
        if split[1] == ".txt":
            pairs = read_pairs(file)
            nr_picks = math.floor(len(pairs)/2)
            picks = random.sample(pairs,nr_picks)
            write_pairs_to_file(picks, split[0] + "-50.txt")


