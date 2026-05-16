import pandas as pd 
from collections import deque
from process import Process

data = pd.read_csv("./static/data", index_col="process_id")
print(type(data))
# print(data.head())

# print(data[data.arrival_time == 24])
ready_queue = deque()

for row in data.itertuples():
    # print(row)
    # print(type(row.arrival_time))
    process = Process(row.Index, row.arrival_time, row.burst_time)
    ready_queue.append(process)

print(len(list(ready_queue)))
print(ready_queue.pop())

# ready_queue.append(1)
# ready_queue.append(2)

# print(ready_queue.pop())