import pandas as pd
import matplotlib.pyplot as plt
from typing import List
from process import Process
from datetime import datetime


class SJFScheduler:
    def __init__(self, processes: List[Process]):
        self.processes = sorted(processes, key=lambda p: p.arrival_time)
        self.current_time = 0
        self.completed = 0
        self.gantt_chart = []
        self.event_log = []

    def log_event(self, message: str):
        """Add event to log and print to console"""
        timestamp = f"[Time {self.current_time:.2f}]"
        log_message = f"{timestamp:15} {message}"
        print(log_message)
        self.event_log.append(log_message)

    def find_next_arrival(self) -> float:
        """Find the next arrival time after current_time"""
        future_arrivals = [
            p.arrival_time for p in self.processes
            if p.arrival_time > self.current_time and p.remaining_time > 0
        ]
        return min(future_arrivals) if future_arrivals else float('inf')

    def run(self):
        """Main SJF Non-Preemptive Simulation"""
        total_processes = len(self.processes)
        done = set()

        self.log_event("=== SJF NON-PREEMPTIVE SIMULATION STARTED ===")

        while self.completed < total_processes:
            # Get all arrived processes not yet completed
            arrived = [
                p for p in self.processes
                if p.arrival_time <= self.current_time and p.remaining_time > 0 and p.id not in done
            ]

            if not arrived:
                # Jump to next arrival
                next_arrival = self.find_next_arrival()
                if next_arrival == float('inf'):
                    break
                self.log_event(f"CPU idle until time {next_arrival}")
                self.current_time = next_arrival
                continue

            # Log ready queue
            ready_list = [f"P{p.id}({p.burst_time})" for p in sorted(arrived, key=lambda x: x.burst_time)]
            self.log_event(f"Ready Queue: [{', '.join(ready_list)}]")

            # Select process with shortest burst time (Non-Preemptive)
            current_process = min(arrived, key=lambda p: (p.burst_time, p.arrival_time, self.processes.index(p)))

            # Record response time (first time on CPU)
            if current_process.response_time == -1:
                current_process.response_time = self.current_time - current_process.arrival_time
                current_process.first_run_time = self.current_time
                self.log_event(
                    f"Process P{current_process.id} gets CPU for the FIRST TIME "
                    f"(response time = {current_process.response_time:.2f})"
                )

            # Run to completion (Non-Preemptive — no interruption)
            start_time = self.current_time
            self.current_time += current_process.burst_time
            current_process.remaining_time = 0
            current_process.completion_time = self.current_time

            # Calculate metrics
            current_process.turnaround_time = current_process.completion_time - current_process.arrival_time
            current_process.waiting_time = current_process.turnaround_time - current_process.burst_time

            self.gantt_chart.append((current_process.id, start_time, self.current_time))
            done.add(current_process.id)

            self.log_event(
                f"P{current_process.id} runs from {start_time:.2f} to {self.current_time:.2f} "
                f"(duration: {current_process.burst_time})"
            )
            self.log_event(
                f"[COMPLETED] P{current_process.id} finished! "
                f"(TAT={current_process.turnaround_time:.2f}, WT={current_process.waiting_time:.2f})"
            )

            self.completed += 1
            self.log_event(f"Progress: {self.completed}/{total_processes} processes completed")

        self.log_event("=== SJF NON-PREEMPTIVE SIMULATION COMPLETED ===")

    def save_log_to_file(self, filename: str = "./results/sjf_simulation_log.txt"):
        """Save all event logs to a text file using UTF-8 encoding"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("SJF NON-PREEMPTIVE SIMULATION LOG\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Processes: {len(self.processes)}\n")
            f.write("=" * 80 + "\n\n")

            for event in self.event_log:
                f.write(event + "\n")

            # Summary statistics
            f.write("\n" + "=" * 80 + "\n")
            f.write("SUMMARY STATISTICS\n")
            f.write("=" * 80 + "\n")
            avg_tat = sum(p.turnaround_time for p in self.processes) / len(self.processes)
            avg_wt = sum(p.waiting_time for p in self.processes) / len(self.processes)
            avg_rt = sum(p.response_time for p in self.processes) / len(self.processes)
            f.write(f"Average Turnaround Time (ATT): {avg_tat:.2f}\n")
            f.write(f"Average Waiting Time (AWT):    {avg_wt:.2f}\n")
            f.write(f"Average Response Time (ART):   {avg_rt:.2f}\n")
            f.write(f"Total Context Switches:        {len(self.gantt_chart) - 1}\n")
            f.write(f"Total Completion Time:          {self.current_time}\n")

        print(f"\n[SUCCESS] Simulation log saved to '{filename}'")

    def display_gantt_chart_visual(self):
        """Display a professional visual Gantt chart with wrapping for long runs"""
        if not self.gantt_chart:
            print("No Gantt chart data available")
            return

        segments_per_row = 40
        total_segments = len(self.gantt_chart)
        num_rows = (total_segments + segments_per_row - 1) // segments_per_row

        if num_rows > 1:
            fig, axes = plt.subplots(num_rows, 1, figsize=(16, 3 * num_rows))
            if num_rows == 1:
                axes = [axes]
        else:
            fig, axes = plt.subplots(1, 1, figsize=(16, 6))
            axes = [axes]

        unique_processes = list(set([pid for pid, _, _ in self.gantt_chart]))
        try:
            colormap = plt.get_cmap('tab20')
            colors = [colormap(i) for i in range(len(unique_processes))]
        except:
            colormap = plt.get_cmap('Set3')
            colors = [colormap(i % 12) for i in range(len(unique_processes))]

        color_map = {pid: colors[i] for i, pid in enumerate(sorted(unique_processes))}

        for row_idx in range(num_rows):
            ax = axes[row_idx]
            start_idx = row_idx * segments_per_row
            end_idx = min((row_idx + 1) * segments_per_row, total_segments)
            row_segments = self.gantt_chart[start_idx:end_idx]

            if not row_segments:
                continue

            time_offset = row_segments[0][1] if start_idx > 0 else 0

            for pid, start, end in row_segments:
                adjusted_start = start - time_offset
                adjusted_end = end - time_offset
                duration = adjusted_end - adjusted_start

                ax.barh(y=0, width=duration, left=adjusted_start,
                        color=color_map[pid], edgecolor='black', linewidth=1)

                if duration > 0.5:
                    mid_x = adjusted_start + duration / 2
                    ax.text(mid_x, 0, f"P{pid}", ha='center', va='center',
                            fontsize=8, fontweight='bold')

            ax.set_xlabel('Time (relative to row start)', fontsize=10, fontweight='bold')
            ax.set_ylabel(f'Row {row_idx + 1}', fontsize=10, fontweight='bold')
            ax.set_ylim(-0.5, 0.5)
            ax.set_yticks([])
            ax.grid(axis='x', alpha=0.3, linestyle=':', linewidth=0.5)

            if row_idx == 0:
                ax.set_title('SJF Non-Preemptive Scheduling - Gantt Chart',
                             fontsize=12, fontweight='bold')

            max_time_in_row = max([end - time_offset for _, _, end in row_segments])
            ax.set_xlim(-0.5, max_time_in_row + 1)

        plt.tight_layout()
        plt.savefig('./results/sjf_gantt_chart.png', dpi=300, bbox_inches='tight')
        print("\n[SUCCESS] Visual Gantt chart saved as 'sjf_gantt_chart.png'")
        # plt.show()  # Uncomment if you want to view it immediately

    def display_results(self):
        """Display process table and metrics"""
        print("\n" + "=" * 90)
        print("SJF NON-PREEMPTIVE - PROCESS EXECUTION TABLE")
        print("=" * 90)

        data = []
        for p in self.processes:
            data.append({
                'ID': p.id,
                'AT': p.arrival_time,
                'BT': p.burst_time,
                'CT': p.completion_time,
                'TAT': p.turnaround_time,
                'WT': p.waiting_time,
                'RT': p.response_time
            })

        df = pd.DataFrame(data)
        print(df.to_string(index=False))

        avg_tat = sum(p.turnaround_time for p in self.processes) / len(self.processes)
        avg_wt = sum(p.waiting_time for p in self.processes) / len(self.processes)
        avg_rt = sum(p.response_time for p in self.processes) / len(self.processes)

        print("\n" + "=" * 90)
        print("PERFORMANCE METRICS")
        print("=" * 90)
        print(f"Total Processes Completed:     {len(self.processes)}")
        print(f"Average Turnaround Time (ATT): {avg_tat:.2f}")
        print(f"Average Waiting Time (AWT):    {avg_wt:.2f}")
        print(f"Average Response Time (ART):   {avg_rt:.2f}")
        print(f"Total Context Switches:        {len(self.gantt_chart) - 1}")
        print(f"Total Completion Time:          {max(p.completion_time for p in self.processes)}")

    def export_results(self, filename: str = "./results/sjf_simulation_results.csv"):
        """Export results to CSV file"""
        data = []
        for p in self.processes:
            data.append({
                'id': p.id,
                'arrival_time': p.arrival_time,
                'burst_time': p.burst_time,
                'completion_time': p.completion_time,
                'turnaround_time': p.turnaround_time,
                'waiting_time': p.waiting_time,
                'response_time': p.response_time
            })

        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"\n[SUCCESS] Results exported to {filename}")
