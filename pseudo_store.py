import simpy

BATCHING_RULES = ['SPT', 'LPT']

class pseudo_store(object):
    def __init__(self, env, kind, name=None, capacity=float('inf')) -> None:
        self.env = env
        self.kind = kind
        self.store = simpy.PriorityStore(env, capacity=capacity)
        self.name = name

    def put(self, job) -> None:
        priority_job = None
        if self.kind == 'SPT': # Shortest Processing Time
            priority_job = simpy.PriorityItem(priority=job.OT_table[self.name], item=job)
        elif self.kind == 'LPT': # Longest Processing Time
            priority_job = simpy.PriorityItem(priority=-job.OT_table[self.name], item=job)
        else: # TODO add dispatching rules
            priority_job = simpy.PriorityItem(priority=None, item=job)
        return self.store.put(priority_job)

    def get(self) -> None:
        return self.store.get()
    
    def print_items(self) -> None:
        items = self.store.items
        for item in items:
            print(item.item.name, end=', ')
        print()
