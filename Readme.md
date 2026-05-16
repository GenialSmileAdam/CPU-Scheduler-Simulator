# CPU Scheduler Simulator

This project generates process data and runs CPU scheduling simulations for an Operating Systems assignment. It currently includes:

- Round Robin scheduling
- SRTF (Shortest Remaining Time First) scheduling
- CSV data generation for at least 20 processes
- Simulation logs, result tables, and Gantt chart outputs

## Project Structure

| File/Folder | Purpose |
| --- | --- |
| `data_generator.py` | Generates random process data and saves it to `static/data.csv`. |
| `process.py` | Defines the shared `Process` class used by the schedulers. |
| `process_loader.py` | Loads and sorts process data from the CSV file. |
| `round_robin_algorithm.py` | Runs the Round Robin scheduler. |
| `scheduler_report.py` | Saves logs, results, Gantt charts, and calculates metrics. |
| `srtf_algorithm.py` | Contains the SRTF scheduler implementation. |
| `main.py` | Runs the SRTF simulation. |
| `static/` | Stores generated input data. |
| `results/` | Stores simulation outputs. |

## Setup

Round Robin and the data generator use only Python's standard library.

SRTF uses extra packages:

```bash
pip install pandas matplotlib
```

If you are using Pipenv:

```bash
pipenv install
pipenv shell
```

## 1. Generate Process Data

Run:

```bash
python data_generator.py
```

This creates:

- `static/data.csv`

The generated data follows the assignment requirement:

- `20` processes by default
- arrival time range: `0-30`
- burst time range: `1-50`

CSV format:

| process_id | arrival_time | burst_time |
| --- | --- | --- |
| 1 | 13 | 9 |
| 2 | 17 | 5 |

## 2. Run Round Robin

Run:

```bash
python round_robin_algorithm.py
```

The time quantum is set inside `round_robin_algorithm.py`:

```python
TIME_QUANTUM = 5
```

Round Robin output files:

- `results/round_robin_simulation_log.txt`
- `results/round_robin_simulation_results.csv`
- `results/round_robin_gantt_chart.txt`
- `results/round_robin_gantt_chart.csv`

The results CSV contains:

- process ID
- arrival time
- burst time
- completion time
- turnaround time
- waiting time
- response time

The log also includes:

- Average Waiting Time (AWT)
- Average Turnaround Time (ATT)
- Average Response Time
- Context Switches
- CPU Utilization
- Throughput

## 3. Run SRTF

Install the required packages first:

```bash
pip install pandas matplotlib
```

Then run:

```bash
python main.py
```

SRTF output files:

- `results/srtf_simulation_log.txt`
- `results/srtf_simulation_results.csv`
- `results/srtf_gantt_chart.png`

## Metrics Used

For every process:

```text
Turnaround Time = Completion Time - Arrival Time
Waiting Time = Turnaround Time - Burst Time
Response Time = First CPU Start Time - Arrival Time
```

Project averages:

```text
Average Turnaround Time = Total Turnaround Time / Number of Processes
Average Waiting Time = Total Waiting Time / Number of Processes
```

Extra metrics:

```text
CPU Utilization = CPU Busy Time / Total Simulation Time * 100
Throughput = Number of Completed Processes / Total Simulation Time
```

## Recommended Workflow

1. Generate fresh process data:

```bash
python data_generator.py
```

2. Run the assigned scheduler:

```bash
python round_robin_algorithm.py
```

or:

```bash
python main.py
```

3. Open the files in `results/`.

4. Use the result CSV and Gantt chart in your report or presentation.

## Notes

- Regenerating data will overwrite `static/data.csv`.
- Rerunning a scheduler will overwrite that scheduler's files in `results/`.
- Round Robin is intentionally split into smaller modules so the code stays readable and cohesive.
