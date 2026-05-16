import pandas as pd 
from collections import deque
from process import Process



ready_queue = deque()
current_time = 0 
TIME_QUANTUM =  5


def roundrobin():
    
    processes = get_processes()
    sorted_processes = arrange_processes(processes)
    check_for_process_arrival(sorted_processes)
    # First check if there is items in the ready queue and the process list, if not, the program is done 
    while sorted_processes or ready_queue:
        pass
    # # to actually run the program, check if there is any process in the ready queue

    # # if yes then run the process for the time quantum
    # #       if the process burst time < time quantum , run the program and terminate it
    # #       if not, run the program and then add it back to the ready queue 


    # # if no , then increase time by 1 second, and rerun the program
    #     if ready_queue:
    #         current_process= ready_queue.popleft()
    #         if current_process.burst_time <= TIME_QUANTUM:
    #             print(f"Time {current_time}-{current_process.burst_time} Process {current_process.process_id} finishes its last {current_process.burst_time}s")
              
    #             current_time += current_process.burst_time

    #         else:
    #             print(f"Time {current_time}-{current_time + TIME_QUANTUM} Process {current_process.process_id} runs for {TIME_QUANTUM}s (remaining {current_process.burst_time - TIME_QUANTUM}s)")

    #             current_process.burst_time -= TIME_QUANTUM
    #             current_time += TIME_QUANTUM
    #             add_to_ready_queue(current_process)
    #         check_for_process_arrival(sorted_processes)
    #     else: 
    #         check_for_process_arrival(sorted_processes)

    # then add that item to the ready queue
 

#TODO Arrange the processes based on arrival time into the ready queue 
def get_processes():
    """Gets processes from CSV"""
    data = pd.read_csv("./static/data.csv", index_col="process_id")
    process_list = []

    for row in data.itertuples():
        
        process = Process(row.Index, row.arrival_time, row.burst_time)
        process_list.append(process)

    return process_list

def arrange_processes(processes: list[Process]):
    """Arrange Processes in a list based on Arrival time"""

    sorted_processes = sorted(processes, key=lambda process: process.arrival_time)

    return sorted_processes    

# sorted_data = arrange_processes(data_list)

# for procs in sorted_data:
#     print(procs.arrival_time)

#TODO helper functions include Termination and addition to ready queue 
def add_to_ready_queue(process : Process):

    ready_queue.append(process)
    
def check_for_process_arrival(sorted_processes):
    # check if the arrival time of the first element in the process list is less than or equals to the current time
    print(f"Remaining processes in process list{len(sorted_processes)}")
    for item in sorted_processes:
        print("checking processes")
        if item.arrival_time <= current_time :
            add_to_ready_queue(item)
            print(f"Added Process {item.process_id} to the ready queue")
            try:
                sorted_processes.pop(sorted_processes.index(item))
            except IndexError:
                print(" Process is not in process list")
            
        else: 
            return 
        

roundrobin()