# main.py
import pandas as pd
from process import Process
from srtf_algorithm import SRTFScheduler

# Load processes
df = pd.read_csv('./static/data.csv')
processes = [Process(row.process_id, row.arrival_time, row.burst_time) for _, row in df.iterrows()]

print(f"Loaded {len(processes)} processes\n")

def run_srtf():
    # Run simulation
    scheduler = SRTFScheduler(processes)
    scheduler.run()

    # Show results
    print("\n" + "="*60)
    print("RESULTS TABLE")
    print("="*60)
    for p in processes:
        print(f"P{p.id}: AT={p.arrival_time} BT={p.burst_time} CT={p.completion_time} TAT={p.turnaround_time} WT={p.waiting_time} RT={p.response_time}")

    print("\n" + "="*60)
    print("METRICS")
    print("="*60)
    print(f"ATT: {sum(p.turnaround_time for p in processes)/len(processes):.2f}")
    print(f"AWT: {sum(p.waiting_time for p in processes)/len(processes):.2f}")
    print(f"ART: {sum(p.response_time for p in processes)/len(processes):.2f}")
    print(f"Context Switches: {len(scheduler.gantt)-1}")

    # Save files
    scheduler.save_results()
    scheduler.plot_gantt()

if __name__ == "__main__":
    run_srtf()