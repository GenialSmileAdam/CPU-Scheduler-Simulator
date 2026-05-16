import pandas as pd 
from random import randint
import numpy as np 
import os 
from pathlib import Path

folder = Path("./static")

# Check if it exists and is a directory
if folder.is_dir():
    print("The folder exists.")
else:
    print("Static folder has been created .")
    os.mkdir("static")


# num_processes = randint(1, 10)
num_processes = 30
print(f"Number of processes created : {num_processes}")
data_list = []
# Creates a dataframe that contains Burst time, Process id, Arrival time . There should be a minimum of 30 processes 
for process in range(0, num_processes ):
    arrival_time = randint(0, 50)
    burst_time = randint(0, 50)
    # print(f"Process {process}: arrival time: {arrival_time},Burst time: {burst_time} ")
    data_list.append([arrival_time, burst_time])

data = pd.DataFrame(np.array(data_list), columns=["arrival_time", "burst_time"])



# Saves the dataframe in a csv format in the directory 

data = data.rename_axis("process_id")

data.to_csv("./static/data.csv")