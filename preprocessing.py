import numpy as np

def standard_specification(filename='./JobShop/input/example.txt'):
    num_jobs = None
    num_machines = None

    data = None

    with open(filename, 'r') as file:
        line = file.readline().strip().split()
        num_jobs = int(line[0])
        num_machines = int(line[1])
        data = np.empty((num_jobs, num_machines, 2))

        for i in range(num_jobs):
            line = file.readline().strip().split()
            for j in range(num_machines):
                data[i][j] = (float(line[2*j]), float(line[2*j+1]))
    return num_jobs, num_machines, data
