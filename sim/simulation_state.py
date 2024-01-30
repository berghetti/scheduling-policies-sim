#!/usr/bin/env python
"""Object to maintain simulation state."""

import math
from math import sqrt, log
import datetime
import random
import os

from timer import Timer
from work_search_state import WorkSearchState
from tasks import EnqueuePenaltyTask, Task
from sim_thread import Thread
from sim_queue import Queue
import progress_bar as progress

class SimulationState:
    """Object to maintain simulation state as time passes."""

    def __init__(self, config):
        # Simulation Global Variables
        self.timer = Timer()
        self.threads = []
        self.queues = []
        self.tasks = []
        self.parked_threads = []
        self.available_queues = []
        self.allocating_threads = []
        self.main_queue = None

        # Global stats
        self.overall_steal_count = 0
        self.flag_steal_count = 0
        self.flag_raise_count = 0
        self.complete_task_count = 0
        self.park_count = 0
        self.last_realloc_choice = 0
        self.global_check_count = 0
        self.work_steal_tasks = 0
        self.empty_flags = 0
        self.alloc_to_task_time = 0 # Make this per-task if need anything other than the average
        self.allocations = 0

        # Stats only known at complete time
        self.tasks_scheduled = 0
        self.end_time = None
        self.sim_end_time = None

        # Optional stats
        self.reallocation_schedule = []
        self.reallocations = 0
        self.ws_checks = []
        self.queue_lens = []

        self.attempted_flag_steals = 0

        self.config = config

        # persephone core dispather
        self.persephone_dispatcher = None

        # afp related
        self.afp_timer = None
        self.wait_queue = None


    def any_queue_past_delay_threshold(self):
        """Returns true if any queue has a queueing delay longer than the reallocation interval."""
        return any([x.current_delay() > self.config.ALLOCATION_THRESHOLD for x in self.queues])

    def currently_working_cores(self):
        """Returns the cores currently working on something productive."""
        return [thread.id for thread in self.threads if thread.is_productive()]

    def num_currently_working_cores(self):
        """Returns the number of cores currently working on something productive."""
        return sum(thread.is_productive() for thread in self.threads)

    def num_currently_distracted_cores(self):
        """Returns the number of cores currently (in this timestep) distracted by overhead from a local task."""
        return sum(thread.is_distracted(evaluate=False) for thread in self.threads)

    def currently_non_productive_cores(self):
        """Returns cores not currently working on a productive task or parked."""
        return [thread.id for thread in self.threads if not thread.is_productive() and
                not (thread.id in self.parked_threads)]

    def num_paired_cores(self):
        """Returns the number of cores that could be spending their time on a productive, non-local task."""
        # TODO: Figure out how allocation time and parked time fits into this
        total_queue = self.total_queue_occupancy()
        distracted = self.num_currently_distracted_cores()
        non_productive = len(self.currently_non_productive_cores())
        tasks = total_queue - distracted
        cores = non_productive - distracted
        paired = min(tasks, cores)
        return paired

    def current_buffer_cores(self, check_work_available=False):
        """Returns the number of cores currently matching the definition of a buffer core.
        Buffer cores are ones that are not working on anything productive, are active, do not have a work steal flag,
        are not currently placing tasks,
        and optionally do not have any work available in their local queue.
        :param check_work_available: If true, confirm that there is no work available in the local queue.
        Otherwise, ignore this factor.
        """
        buffer_cores = []
        for thread in self.threads:
            if not thread.is_productive() and not thread.work_search_state == WorkSearchState.PARKED and \
                    not(thread.current_task is not None and type(thread.current_task) == EnqueuePenaltyTask) and \
                    not(self.config.delay_flagging_enabled and thread.work_steal_flag is not None) and \
                    not(check_work_available and thread.queue.length() > 0) and \
                    not(self.config.enqueue_choice and thread.queue.awaiting_enqueue):
                buffer_cores.append(thread.id)
        return buffer_cores

    def allowed_buffer_cores(self):
        """Calculate the current number of allowed buffer cores."""
        # Min changes to achieve better efficiency at low loads - need fewer cores than constant offers
        currently_working = self.num_currently_working_cores()

        # Get the max number
        max_count = self.config.BUFFER_CORE_COUNT_MAX if self.config.BUFFER_CORE_COUNT_MAX is not None \
            else math.ceil(currently_working * (self.config.BUFFER_CORE_PCT_MAX/100))
        if max_count == 0:
            max_count = 1

        # If both types of mins defined, take higher one
        if self.config.BUFFER_CORE_PCT_MIN is not None and self.config.BUFFER_CORE_COUNT_MIN is not None:
            min_count = max(self.config.BUFFER_CORE_COUNT_MIN,
                            math.ceil(currently_working * (self.config.BUFFER_CORE_PCT_MIN/100)))
        elif self.config.BUFFER_CORE_COUNT_MIN is not None:
            min_count = self.config.BUFFER_CORE_COUNT_MIN
        else:
            min_count = math.ceil(currently_working * (self.config.BUFFER_CORE_PCT_MIN/100))
        return min_count, max_count

    def current_utilization(self, reset=True):
        """Calculate the current average utilization."""
        busy_time = 0
        task_time = 0
        for thread in self.threads:
            busy_time += thread.last_interval_busy_time
            task_time += thread.last_interval_task_time
            if reset:
                thread.last_interval_busy_time = 0
                thread.last_interval_task_time = 0

        return (task_time / busy_time) * 100 if busy_time > 0 else 100

    def can_remove_buffer_core(self):
        """Determine if a buffer core can be parked while still meeting minimum requirements."""
        if not self.config.buffer_cores_enabled:
            return True
        current_buffer_cores = len(self.current_buffer_cores())
        allowed_buffer_cores = self.allowed_buffer_cores()
        return current_buffer_cores > allowed_buffer_cores[0]

    def current_average_queueing_delay(self):
        """Return the current average queueing delay across all queues."""
        # Consider non-available queues since cores can be forced to park with tasks
        total_queue_time = 0
        for queue in self.queues:
            total_queue_time += queue.current_delay()
        return total_queue_time / len(self.available_queues)

    def current_average_service_time_sum(self):
        """Return the current average queueing delay across all queues."""
        # Consider non-available queues since cores can be forced to park with tasks
        total_service_time_left = 0
        for queue in self.queues:
            total_service_time_left += queue.length_by_service_time()
        for thread in self.threads:
            if thread.is_productive():
                total_service_time_left += thread.current_task.time_left
        return total_service_time_left / (self.config.num_threads - len(self.parked_threads))

    def can_increase_delay(self):
        """Determine if the average queueing delay is currently below the acceptable threshold."""
        if not self.config.delay_range_enabled:
            return True
        if self.config.delay_range_by_service_time:
            return self.current_average_service_time_sum() < self.config.REALLOCATION_THRESHOLD_MAX
        return self.current_average_queueing_delay() < self.config.REALLOCATION_THRESHOLD_MAX

    def threads_available_for_allocation(self):
        """Return true if there are currently any parked threads."""
        return len(self.parked_threads) > 0

    def threads_available_for_deallocation(self):
        """Return true if there are non-parked cores."""
        return len(self.parked_threads) < self.config.num_threads

    def any_incomplete(self):
        """Return true if there are any incomplete tasks for the entire simulation."""
        #print('{} {}'.format(self.complete_task_count, self.tasks_scheduled))
        return self.complete_task_count < self.tasks_scheduled

    def record_ws_check(self, local_id, remote, check_count, successful=False):
        """Record a work steal check on a queue to see if it can be stolen from."""
        if self.config.record_steals:
            if not successful:
                self.ws_checks.append((local_id, remote.id, self.state.timer.get_time() - remote.last_ws_check,
                                       remote.length(), check_count, False))
            else:
                self.ws_checks[-1] = (local_id, remote.id, self.state.timer.get_time() - remote.last_ws_check,
                                      remote.length(), check_count, True)

    def record_queue_lengths(self):
        """Record the lengths of all queues."""
        if self.config.record_queue_lens:
            # self.queue_lens.append([x.length() for x in self.queues])
            self.queue_lens.append([x.current_delay() for x in self.queues])

    def add_reallocation(self, is_park, attempted=False):
        """Record a reallocation.
        :param is_park: True if the reallocation was a park, otherwise false.
        """
        if self.config.record_allocations:
            if self.config.buffer_cores_enabled:
                self.reallocation_schedule.append(
                    (self.timer.get_time(), is_park, int(attempted), self.total_queue_occupancy(),
                     self.total_work_in_system(), len(self.current_buffer_cores())))
            else:
                self.reallocation_schedule.append((self.timer.get_time(), is_park, int(attempted),
                                                   self.total_queue_occupancy(), self.total_work_in_system()))

    def add_realloc_time_check_in(self):
        """Record time, cores working, and core occupancy."""
        self.reallocation_schedule.append((self.timer.get_time(), self.num_currently_working_cores(),
                                           self.total_queue_occupancy(), self.total_work_in_system()))

    def add_final_stats(self):
        """Add final global stats to to the simulation state."""
        self.end_time = self.timer.get_time()
        self.tasks_scheduled = len(self.tasks)
        self.sim_end_time = datetime.datetime.now().strftime("%y-%m-%d_%H:%M:%S")

    def results(self):
        """Create a dictionary of important statistics for saving."""
        stats = {"Global Number of Steals": self.overall_steal_count, "Completed Tasks": self.complete_task_count,
                 "Global Park Count": self.park_count, "Tasks Scheduled": self.tasks_scheduled,
                 "Simulation End Time": self.sim_end_time, "End Time": self.end_time,
                 "Flag Steals": self.flag_steal_count, "Empty Queues Flagged": self.empty_flags,
                 "Flags Raised": self.flag_raise_count, "Total Alloc to Task Time": self.alloc_to_task_time,
                 "Number Allocations": self.allocations}
        return stats

    def allocate_thread(self):
        """Allocate a parked thread."""
        if not self.threads_available_for_allocation():
            self.add_reallocation(False, attempted=True)
            return None

        # If all cores are parked, allocate the most recently parked one so that it is mapped to the active queue
        if len(self.parked_threads) == self.config.num_threads:
            chosen_thread = self.queues[self.available_queues[0]].get_core()
        else:
            chosen_thread = max(self.parked_threads)
        self.threads[chosen_thread].scheduled_dealloc = False
        self.add_reallocation(False)
        self.parked_threads.remove(chosen_thread)

        if not self.config.allocation_delay:
            self.threads[chosen_thread].work_search_state.reset()
            if self.config.num_queues > 1 and not(self.threads[chosen_thread].queue.id in self.available_queues):
                self.available_queues.append(self.threads[chosen_thread].queue.id)
        else:
            self.threads[chosen_thread].work_search_state.allocate()
            self.allocating_threads.append(chosen_thread)

        self.allocations += 1
        self.last_realloc_choice = self.timer.get_time()
        return chosen_thread

    def deallocate_thread(self, thread_id):
        """Park the specified thread."""
        if not self.threads_available_for_deallocation():
            self.add_reallocation(True, attempted=True)
            return

        self.park_count += 1
        self.add_reallocation(True)
        self.last_realloc_choice = self.timer.get_time()

        self.parked_threads.append(thread_id)

        # Make the queue unavailable if there's more than one queue, the queue is available, and
        # all of its threads are parked
        # Queue may not be available if thread was on allocation delay
        if self.config.num_queues > 1 and self.threads[thread_id].queue.id in self.available_queues and \
                all(x in self.parked_threads for x in self.threads[thread_id].queue.thread_ids) and \
                len(self.available_queues) > 1:
            self.available_queues.remove(self.threads[thread_id].queue.id)

        # If in replay mode, allow the thread to finish its current task
        if self.config.reallocation_replay and self.threads[thread_id].is_productive():
            self.threads[thread_id].scheduled_dealloc = True
        else:
            if self.threads[thread_id].current_task and self.threads[thread_id].current_task.remote:
                self.threads[thread_id].current_task.remote.unlock(thread_id)
            if thread_id in self.allocating_threads:
                self.allocating_threads.remove(thread_id)
            self.threads[thread_id].current_task = None
            self.threads[thread_id].queue.unlock(thread_id)
            self.threads[thread_id].work_search_state.park()

    def total_queue_occupancy(self):
        """Return the total queue occupancy across all queues."""
        total = 0
        for q in self.queues:
            total += q.length()
        return total

    def total_work_in_system(self):
        """Return the total work in the system."""
        total = 0
        for q in self.queues:
            total += q.length_by_service_time()
        for thread in self.threads:
            if thread.is_productive():
                total += thread.current_task.time_left
        return total

    def initialize_state(self, config):
        """Initialize the simulation state based on the configuration."""
        if config.progress_bar:
            print("\nInitializing...")

        # Input validation
        if not config.validate():
            print("Invalid configuration")
            return

        # Set random seed based on run name
        if config.reallocation_replay:
            random.seed(config.reallocation_record)
        else:
            #print('Seed: {}'.format(config.seed))
            #random.seed(config.name)
            random.seed(config.seed)

        # Set reallocation schedule if replaying one
        if config.reallocation_replay:
            record_file = open("./results/sim_{}/realloc_schedule".format(config.reallocation_record), "r")
            self.reallocation_schedule = eval(record_file.read())
            self.reallocations = len(self.reallocation_schedule)
            record_file.close()

        # Initialize queues
        for i in range(len(set(config.mapping))):
            self.queues.append(Queue(i, config, self))
        self.available_queues = list(set(config.mapping))

        if config.join_bounded_shortest_queue:
            self.main_queue = Queue(-1, config, self)

        # Initialize threads
        for i in range(config.num_threads):
            queue = self.queues[config.mapping[i]]
            self.threads.append(Thread(queue, i, config, self))
            queue.set_thread(i)


        if config.afp_enable:
            self.afp_timer = self.threads[-1] # last core is timer
            self.afp_timer.is_afp_timer = True
            self.wait_queue = Queue(-1, config, self)
            self.available_queues.remove(self.afp_timer.id) # remove queue from 'NIC dispatching'
            #print(self.available_queues, self.afp_timer)

        if config.persephone_enable:
            # thread 0 is persephone dispatcher
            self.persephone_dispatcher = self.threads[0]
            self.threads[0].is_persephone_dispatcher = True

            # set two queues, one to short other to long requests
            self.threads[0].persephone_queues.append(Queue(100, config, self))
            self.threads[0].persephone_queues[0].set_thread(0)
            self.threads[0].persephone_queues.append(Queue(200, config, self))
            self.threads[0].persephone_queues[1].set_thread(0)

            # set reserved cores to short request
            for i in range(config.persephone_total_reserved_cores):
                self.threads[i+1].persephone_reserved = True

        # Set siblings
        for i in range(config.num_threads):
            if config.num_threads % 2 == 1 and config.num_threads-1 == i:
                self.threads[i].sibling = None
            elif i % 2 == 0:
                self.threads[i].sibling = self.threads[i + 1]
            else:
                self.threads[i].sibling = self.threads[i - 1]

        total_requests = 0
        total_requests_short = 0
        total_requests_long = 0

        service_time_avg = \
            config.SHORT_REQUEST_SERVICE_TIME * config.SHORT_REQUEST_RATE / 1000 + \
            config.LONG_REQUEST_SERVICE_TIME * (1 - config.SHORT_REQUEST_RATE / 1000)

        taxa_rps = 10**9 / service_time_avg * config.worker_cores_count * config.avg_system_load
        print('rps {} load {}'.format(taxa_rps, config.avg_system_load))

        #mean = 1/config.rps * 10**9
        mean = 1/taxa_rps * 10**9 # in ns

        # pareto parameters
        alpha = 1.0 + mean / (mean - 1.0)
        xm = mean * (alpha - 1) / (alpha)

        # lognormal parameters
        sigma = sqrt(2*(log(mean) - log(mean/2)))
        mu = log(mean) - (sigma * sigma) / 2

        # Set tasks and arrival times
        request_rate = mean
        #request_rate = config.avg_system_load * config.worker_cores_count / config.AVERAGE_SERVICE_TIME
        #request_rate =  0.1 * 14 / config.AVERAGE_SERVICE_TIME
        #request_rate = config.avg_system_load * config.rps / 10 ** 9

        print('arrival_dist: {}'.format(config.regular_arrivals))
        match config.regular_arrivals:
            case 'uniform':
                next_task_time = int(request_rate)
            case 'exp':
                next_task_time = int(random.expovariate(1/request_rate))
            case 'pareto':
                next_task_time = int(random.paretovariate(alpha) * xm)
            case 'lognorm':
                next_task_time = int(random.lognormvariate(mu, sigma))
            case _:
                exit('error regular_arrivals config')

        i = 0
        while (config.sim_duration is None or next_task_time < config.sim_duration) and \
                (config.num_tasks is None or i < config.num_tasks):
            service_time = None
            while service_time is None or service_time == 0:
                total_requests += 1
                if config.constant_service_time:
                    service_time = config.AVERAGE_SERVICE_TIME
                elif config.bimodal_service_time:
                    if random.randint(0, 999) < config.SHORT_REQUEST_RATE:
                        total_requests_short += 1
                        service_time = config.SHORT_REQUEST_SERVICE_TIME
                    else:
                        total_requests_long += 1
                        service_time = config.LONG_REQUEST_SERVICE_TIME
                else:
                    service_time = int(random.expovariate(1 / config.AVERAGE_SERVICE_TIME))

            #print('SV {}'.format(service_time))
            self.tasks.append(Task(service_time, next_task_time, config, self))

            match config.regular_arrivals:
                case 'uniform':
                    next_task_time += int(request_rate)
                case 'exp':
                    next_task_time += int(random.expovariate(1/request_rate))
                case 'pareto':
                    next_task_time += int(random.paretovariate(alpha) * xm)
                case 'lognorm':
                    next_task_time += int(random.lognormvariate(mu, sigma))

            if config.progress_bar and i % 100 == 0:
                progress.print_progress(next_task_time, config.sim_duration, decimals=3, length=50)
            i += 1

        print("\ntotal:{}\n  shorts:{}\n  longs:{}\n".format(total_requests, total_requests_short, total_requests_long))
