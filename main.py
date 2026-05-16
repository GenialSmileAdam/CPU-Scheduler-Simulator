# main.py
import os
from pathlib import Path

import pandas as pd
import sys
from process import Process
from srtf_algorithm import SRTFScheduler

# Set UTF-8 encoding for console output on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def load_processes_from_csv(filename: str):
    """Load processes from CSV file"""
    processes = []
    
    try:
        df = pd.read_csv(filename, encoding='utf-8')
        
        # Check required columns
        required_columns = ['process_id', 'arrival_time', 'burst_time']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"CSV must contain '{col}' column")
        
        for _, row in df.iterrows():
            process = Process(
                id=int(row['process_id']),
                arrival_time=int(row['arrival_time']),
                burst_time=int(row['burst_time'])
            )
            processes.append(process)
        
        return processes
        
    except FileNotFoundError:
        print(f"Error: {filename} not found!")
        raise
    except Exception as e:
        print(f"Error reading CSV: {e}")
        raise

def run_strf():
    CSV_FILENAME = "./static/data.csv"

    folder = Path("./results")
    if folder.is_dir():
        print("Results folder exists.")
    else:
        print("Results folder has been created.")
        os.mkdir("results")
    
    print("="*80)
    print("SRTF (SHORTEST REMAINING TIME FIRST) SIMULATION")
    print("="*80)
    
    try:
        # Load processes from CSV
        print(f"\nLoading processes from {CSV_FILENAME}...")
        processes = load_processes_from_csv(CSV_FILENAME)
        
        # Display loaded processes
        print("\nLoaded Process Data (first 10):")
        print("-" * 50)
        print(f"{'ID':<6} {'Arrival':<10} {'Burst':<10}")
        print("-" * 50)
        for p in processes[:10]:
            print(f"{p.id:<6} {p.arrival_time:<10} {p.burst_time:<10}")
        if len(processes) > 10:
            print(f"... and {len(processes) - 10} more processes")
        
        print("\n" + "="*80)
        print("SIMULATION LOG (Real-time execution)")
        print("="*80 + "\n")
        
        # Run simulation
        scheduler = SRTFScheduler(processes)
        scheduler.run()
        
        # Save detailed log to file
        scheduler.save_log_to_file("./results/srtf_simulation_log.txt")
        
        # Display results
        scheduler.display_gantt_chart_visual()  # Visual multi-row Gantt chart
        scheduler.display_results()
        scheduler.export_results("./results/srtf_simulation_results.csv")
        
        print("\n" + "="*80)
        print("[SUCCESS] SIMULATION COMPLETE")
        print("="*80)
        print("Generated files:")
        print("  - srtf_simulation_log.txt (Detailed execution log)")
        print("  - srtf_gantt_chart.png (Visual Gantt chart)")
        print("  - srtf_simulation_results.csv (Process metrics)")
        
    except Exception as e:
        print(f"\n[ERROR] Simulation failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    run_strf()

if __name__ == "__main__":
    main()