class Process:
    def __init__(self, id:int, arrival_time:int,burst_time:int ):
        self.id = id
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0
        self.response_time = -1  # -1 means not yet responded
        self.first_run_time = 0

    def __str__(self):
        return f"Process {self.id}"