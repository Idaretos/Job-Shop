import simpy
import pandas as pd
from pseudo_store import pseudo_store
from visualize import gantt

class Job(object):
    def __init__(self, id, data, num_machines) -> None:
        self.name = f'Job {id}'
        self.step = 0
        self.machine_order = data[:, 0]
        self.OT_table = {f'machine {int(self.machine_order[i])}': data[i][1] for i in range(len(self.machine_order))}
        self.process_list = [f'machine {int(self.machine_order[i])}' for i in range(num_machines)] + ['sink']

class Source(object):
    def __init__(self, env, monitor, model, name, num_jobs, num_machines, data, mode):
        env.process(Source.processing(env, monitor, model, name, num_jobs, num_machines, data, mode))

    @staticmethod
    def processing(env, monitor, model, name, num_jobs, num_machines, data, mode):
        jobs = [Job(i, data[i], num_machines) for i in range(num_jobs)]
        monitor.record(time=env.now, job=None, process=name, event='job created')
        for i in range(num_machines):
            model[f'machine {i}'] = Machine(env, monitor, model, i, mode, num_jobs)
        for job in jobs:
            yield model[job.process_list[job.step]].store.put(job)
        for i in range(num_machines):
            env.process(model[f'machine {i}'].processing())


class Machine(object):
    def __init__(self, env, monitor, model, id, mode, num_jobs) -> None:
        self.env = env
        self.monitor = monitor
        self.model = model
        self.id = id
        self.name = f'machine {id}'
        self.num_jobs = num_jobs
        self.done = 0
        self.resource = simpy.Resource(env, capacity=1)
        self.store = pseudo_store(env, mode, name=self.name)

    def processing(self):
        self.done = 0
        while self.done < self.num_jobs:
            with self.resource.request() as req:
                yield req
                job = yield self.store.get()
                job = job.item
                operation_time = job.OT_table[self.name]
                self.monitor.record(time=self.env.now, job=job.name, process=self.name, event='operation start', machine=self.id)
                yield self.env.timeout(operation_time)
                self.monitor.record(time=self.env.now, job=job.name, process=self.name, event='operation finish', machine=self.id)

                self.env.process(self.to_next_process(job))
                self.done += 1
    
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
        self.count = 0
        self.env.process(self.processing())

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
