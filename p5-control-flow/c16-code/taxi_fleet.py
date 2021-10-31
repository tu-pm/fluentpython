from collections import namedtuple

Event = namedtuple('Event', 'time proc action')

def taxi_process(id, trips, start_time=0):
    """Yield to simulator issuing event at each stage change"""
    time = yield Event(start_time, id, 'leave garage')
    for i in range(trips):
        time = yield Event(time, id, 'pick up passager')
        time = yield Event(time, id, 'drop off passanger')

    yield Event(time, id, 'going home')


from random import randint
from queue import PriorityQueue

class Simulator:

    def __init__(self, procs_map):
        self.events = PriorityQueue()
        self.procs = dict(procs_map)

    def run(self, end_time):
        """Schedule and display events until time is up"""

        # schedule the first event for each taxi
        for _, proc in sorted(self.procs.items()):
            first_event = next(proc)
            self.events.put(first_event)

        # main loop of the simulation
        sim_time = 0
        while sim_time < end_time:
            if self.events.empty():
                print('*** end of events ***')
                break

            # get the event with the smallest time in the queue...
            current_event = self.events.get()
            sim_time, proc_id, previous_action = current_event

            # ...and print it out
            print('taxi: ', proc_id, proc_id * '\t', current_event)

            # evaluate the next time an event occurs in current process...
            next_time = sim_time + randint(1, 5)

            # ... and generate the next event from current process
            try:
                next_event = self.procs[proc_id].send(next_time)
            except StopIteration:
                # if there's no more events, remove reference to the process
                del self.procs[proc_id]
            else:
                # put the new event on the queue
                self.events.put(next_event)
        else:
            msg = '*** end of simulation time: {} events pending ***'
            print(msg.format(self.events.qsize()))

taxis = {0: taxi_process(id=0, trips=2, start_time=0),
         1: taxi_process(id=1, trips=4, start_time=5),
         2: taxi_process(id=2, trips=6, start_time=10)}

sim = Simulator(taxis)

sim.run(50)