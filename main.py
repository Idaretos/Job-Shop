from preprocessing import *
from visualize import gantt
from simulation import *

if __name__ == '__main__':
    inputpath, outputpath, mode = set_path('pinedo.txt')
    num_jobs, num_machines, data, parallel_machines = standard_specification(inputpath)

    env = simpy.Environment()
    monitor = Monitor(outputpath + '/eventlog.csv')
    model = {}
    model['source'] = Source(env, monitor, model, 'source', num_jobs,num_machines, data, mode, parallel_machines)
    model['sink'] = Sink(env, monitor, model, 'sink', num_jobs)

    env.run(until=10000)

    monitor.save_event_tracer()
    gantt(num_jobs, outputpath, mode)
