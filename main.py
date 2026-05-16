import os
from pathlib import Path
import pandas as pd
import sys
from process import Process
from srtf_algorithm import SRTFScheduler
from sjf_algorithm import SJFScheduler
from round_robin_algorithm import roundrobin

def load_processes_from_csv(filename):
    processes = []
    df = pd.read_csv(filename, encoding="utf-8")
    for _, row in df.iterrows():
        process = Process(
            id=int(row["process_id"]),
            arrival_time=int(row["arrival_time"]),
            burst_time=int(row["burst_time"])
        )
        processes.append(process)
    return processes

def run_sjf():
    Path("./results").mkdir(exist_ok=True)
    print("SJF SIMULATION")
    processes = load_processes_from_csv("./static/data.csv")
    scheduler = SJFScheduler(processes)
    scheduler.run()
    scheduler.save_log_to_file("./results/sjf_simulation_log.txt")
    scheduler.display_gantt_chart_visual()
    scheduler.export_results("./results/sjf_simulation_results.csv")
    print("[SUCCESS] SJF COMPLETE")

def run_srtf():
    Path("./results").mkdir(exist_ok=True)
    print("SRTF SIMULATION")
    processes = load_processes_from_csv("./static/data.csv")
    scheduler = SRTFScheduler(processes)
    scheduler.run()
    scheduler.save_results()
    scheduler.plot_gantt()
    print("[SUCCESS] SRTF COMPLETE")

def run_round_robin():
    Path("./results").mkdir(exist_ok=True)
    print("ROUND ROBIN SIMULATION")
    roundrobin()
    print("[SUCCESS] ROUND ROBIN COMPLETE")

def main():
    print("1. SJF\n2. SRTF\n3. Round Robin\n4. All Three")
    choice = input("Enter choice (1/2/3/4): ").strip()
    if choice == "1":
        run_sjf()
    elif choice == "2":
        run_srtf()
    elif choice == "3":
        run_round_robin()
    elif choice == "4":
        run_sjf()
        run_srtf()
        run_round_robin()
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
