import numpy as np
import sys
from pseudo_store import BATCHING_RULES
from os.path import realpath, dirname

def standard_specification(filename=dirname(realpath(__file__))+'/input/example.txt'):
    num_jobs = None
    num_machines = None

    data = None

    with open(filename, 'r') as file:
        line = file.readline().strip().split()
        num_jobs = int(line[0])
        num_machines = int(line[1])
        parallel_machines = 1
        if len(line) > 2:
            parallel_machines = int(line[2])
        data = np.empty((num_jobs, num_machines, 2))

        for i in range(num_jobs):
            line = file.readline().strip().split()
            for j in range(num_machines):
                data[i][j] = (float(line[2*j]), float(line[2*j+1]))
    return num_jobs, num_machines, data, parallel_machines

class ModeException(Exception):
    pass

def set_path(name='example.txt'):
    if len(sys.argv) > 3:
        inputpath = sys.argv[1]
        outputpath = sys.argv[2]
        mode = sys.argv[3]
    elif len(sys.argv) > 2:
        inputpath = sys.argv[1]
        outputpath = './output'
        mode = sys.argv[2]
    elif len(sys.argv) > 1:
        inputpath = sys.argv[1]
        outputpath = './output'
        mode = 'SPT'
    else:
        inputpath = dirname(realpath(__file__))+'/input/'+name
        outputpath = dirname(realpath(__file__))+'/output'
        mode = 'SPT'
    if mode not in BATCHING_RULES:
        raise ModeException(f'{mode} not supported!')
    return inputpath, outputpath, mode