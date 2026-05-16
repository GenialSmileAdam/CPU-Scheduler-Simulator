Here's a brief and simple README:


# Process Data Generator

Generates random process scheduling data (arrival time & burst time) for 30-60 processes.

## Setup

```bash
pip install pandas numpy
```

## Generate Data

Run the script:
```bash
python generator.py
```

This creates:
- `static/` folder
- `static/data.csv` CSV file with process data

## Load the Data

```python
import pandas as pd

data = pd.read_csv("./static/data")
print(data.head())
```

## Output Format

| process_id | arrival_time | burst_time |
|------------|--------------|------------|
| 0 | 12 | 35 |
| 1 | 5 | 42 |

- **arrival_time**: 0-50 time units
- **burst_time**: 0-50 time units



That's it! Just run the script and load the CSV with pandas.

# SRFT Algorithm

This uses the Shortest Remaining Time First Algorithm to arrange all the processes.

## SRTF Setup

```bash
pip install pandas numpy matplotlib
```

## Run The Algorithm

Run the script:
```bash
main.py
```

## SRTF Output

After running the algorithm through the main.py file, it creates three files in the results folder

- `results/` folder
- `results/srtf_gantt_chart.png` Gantt Chart showing the scheduling
- `results/srtf_simulation_log.txt` TXT file containing the logs of each process' arrival, preempive removal (if any), completion and the processes in the ready queue as well as the remaining time for their completion at each time stamp.
- `results/srtf_simulation_result.csv` CSV file containing the processes, their response time, turnaround time, completion time and waiting time