import sys
import simpy
import numpy as np
import pandas as pd
import preprocessing
from pseudo_store import pseudo_store
from visualize import gantt

class Job(object):
    def __init__(self, id, data, num_machines) -> None:
        self.id = id
        self.name = f'Job {self.id}'
        self.step = 0
        self.machine_order = data[:, 0]
        self.OT_table = {str(int(self.machine_order[i])): data[i][1] for i in range(len(self.machine_order))}
        self.process_list = [f'machine {int(self.machine_order[i])}' for i in range(num_machines)] + ['sink']

class Source(object):
    def __init__(self, env, monitor, model, name, num_jobs, num_machines, data, kind, done):
        self.jobs = self.job_generator(num_jobs,num_machines, data)
        env.process(self.processing(env, monitor, model, name, num_jobs, num_machines, kind, done))

    def processing(self, env, monitor, model, name, num_jobs, num_machines, kind, done):
        monitor.record(time=env.now, job=None, process=name, event='job created')
        for i in range(num_machines):
            machine = Machine(env, monitor, model, i, kind, num_jobs, done)
            model[f'machine {i}'] = machine
        for job in self.jobs:
            yield model[job.process_list[job.step]].store.put(job)
        done.succeed()

    @staticmethod
    def job_generator(num_jobs, num_machines, data):
        '''Create `Jobs`'''
        jobs = []
        for i in range(num_jobs):
            jobs += [Job(i, data[i], num_machines)]
        return jobs
    
    def generate_machines(self, env, monitor, model, kind, num_jobs, num_machines, done) -> None:
        for i in range(num_machines):
            machine = Machine(env, monitor, model, i, kind, num_jobs, done)
            model[f'machine {i}'] = machine
            yield env.timeout(0)


class Machine(object):
    def __init__(self, env, monitor, model, id, kind, num_jobs, done) -> None:
        self.env = env
        self.monitor = monitor
        self.model = model
        self.name = f'machine {id}'
        self.id = id
        self.kind = kind
        self.num_jobs = num_jobs
        self.done = done
        self.resource = simpy.Resource(env, capacity=1)
        self.store = pseudo_store(env, kind, id=id)

        env.process(self.processing())

    def processing(self):
        yield self.done
        self.done = 0
        while self.done < self.num_jobs:
            with self.resource.request() as req:
                yield req
                job = yield self.store.get()
                job = job.item
                operation_time = job.OT_table[str(self.id)]
                self.monitor.record(time=self.env.now, job=job.name, process=self.name, event='operation start', machine=self.id)
                yield self.env.timeout(operation_time)
                self.monitor.record(time=self.env.now, job=job.name, process=self.name, event='operation finish', machine=self.id)

                self.env.process(self.to_next_process(job))
                self.done += 1

    def put(self, job) -> None:
        '''Push `Job` into `queue` using `simpy.PriorityStore`'''
        priority_job = None
        if self.kind == 'SPT': # Shortest Processing Time
            priority_job = simpy.PriorityItem(priority=job.OT_table[str(self.id)], item=job)
        else: # TODO add dispatching rules
            priority_job = simpy.PriorityItem(priority=None, item=job)
        yield self.store.put(priority_job)

    def to_next_process(self, job):
        job.step += 1
        yield self.model[job.process_list[job.step]].store.put(job)


class Sink(object):
    def __init__(self, env, monitor, model, name, num_jobs) -> None:
        self.env = env
        self.monitor = monitor
        self.model = model
        self.name = name
        self.num_jobs = num_jobs
        self.store = simpy.Store(env)
        self.env.process(self.processing())
        self.count = 0

    def processing(self) -> None:
        while self.count < self.num_jobs:
            job = yield self.store.get()
            self.count += 1
            self.monitor.record(time=self.env.now, job=job.name, process=self.name, event='job finish')


class Monitor(object):
    def __init__(self, filepath) -> None:
        self.filepath = filepath
        self.time = list()
        self.job = list()
        self.process = list()
        self.event = list()
        self.machine = list()

    def record(self, time, process=None, job=None, event=None, machine=None) -> None:
        self.time.append(time)
        self.job.append(job)
        self.process.append(process)
        self.event.append(event)
        self.machine.append(machine)

    def save_event_tracer(self) -> None:
        event_tracer = pd.DataFrame(columns=['Time', 'Job', 'Process', 'Event', 'Machine'])
        event_tracer['Time'] = self.time
        event_tracer['Job'] = self.job
        event_tracer['Process'] = self.process
        event_tracer['Event'] = self.event
        event_tracer['Machine'] = self.machine

        event_tracer.to_csv(self.filepath)

        return event_tracer
    
def setdata():
    if len(sys.argv) > 3:
        inputpath = sys.argv[1]
        outputpath = sys.argv[2]
        kind = sys.argv[3]
    elif len(sys.argv) > 2:
        inputpath = sys.argv[1]
        outputpath = './output'
        kind = sys.argv[2]
    elif len(sys.argv) > 1:
        inputpath = sys.argv[1]
        outputpath = './output'
        kind = 'SPT'
    else:
        inputpath = './JobShop/input/example.txt'
        outputpath = './JobShop/output'
        kind = 'SPT'
    return inputpath, outputpath, kind



if __name__ == '__main__':
    inputpath, outputpath, kind = setdata()
    num_jobs, num_machines, data = preprocessing.standard_specification(inputpath)

    env = simpy.Environment()
    monitor = Monitor(outputpath + '/eventlog.csv')
    done = env.event()
    model = {}
    model['source'] = Source(env, monitor, model, 'source', num_jobs,num_machines, data, kind, done)
    model['sink'] = Sink(env, monitor, model, 'sink', num_jobs)

    env.run(until=10000)

    monitor.save_event_tracer()
    gantt(num_jobs, outputpath, kind)
