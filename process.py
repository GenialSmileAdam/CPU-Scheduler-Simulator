class Process:
    def __init__(self, id:int, arrival_time:int,burst_time:int ):
        self.id = id
        self.arrival_time = arrival_time
        self.burst_time = burst_time

    def __str__(self):
        return f"Process {self.id}"