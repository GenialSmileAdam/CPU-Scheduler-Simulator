import pandas as pd
import matplotlib.pyplot as plt
from typing import List
from process import Process
from datetime import datetime
import numpy as np


class SJFScheduler:
    def __init__(self, processes: List[Process]):
        # Sort by process ID for initial order
        self.processes = sorted(processes, key=lambda p: p.id)
        # Remove all arrival time dependencies
        for p in self.processes:
            p.arrival_time = 0  # Set all to 0 to avoid errors, but won't be used
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

    def run(self):
        """Main SJF Non-Preemptive Simulation - No arrival times, all processes available at time 0"""
        total_processes = len(self.processes)
        
        # All processes are available at time 0
        available_processes = [p for p in self.processes if p.remaining_time > 0]
        
        self.log_event("=== SJF NON-PREEMPTIVE SIMULATION STARTED (No Arrival Times) ===")
        self.log_event(f"All {total_processes} processes available at time 0")

        while self.completed < total_processes:
            # Get all remaining processes (all are always available since no arrival times)
            remaining_processes = [p for p in self.processes if p.remaining_time > 0]
            
            if not remaining_processes:
                break

            # Log ready queue (all remaining processes)
            ready_list = [f"P{p.id}(BT={p.burst_time})" for p in sorted(remaining_processes, key=lambda x: x.burst_time)]
            self.log_event(f"Ready Queue: [{', '.join(ready_list)}]")

            # Select process with shortest burst time (SJF - Non-Preemptive)
            # Tie-breaker: smaller process ID
            current_process = min(remaining_processes, key=lambda p: (p.burst_time, p.id))

            # Record response time (first time on CPU)
            if current_process.response_time == -1:
                current_process.response_time = self.current_time  # No arrival time to subtract
                current_process.first_run_time = self.current_time
                self.log_event(
                    f"Process P{current_process.id} gets CPU for the FIRST TIME "
                    f"(response time = {current_process.response_time:.2f})"
                )

            # Run to completion (Non-Preemptive)
            start_time = self.current_time
            self.current_time += current_process.burst_time
            current_process.remaining_time = 0
            current_process.completion_time = self.current_time

            # Calculate metrics (no arrival time, so TAT = completion time)
            current_process.turnaround_time = current_process.completion_time
            current_process.waiting_time = current_process.turnaround_time - current_process.burst_time

            self.gantt_chart.append((current_process.id, start_time, self.current_time))
            
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
            f.write("SJF NON-PREEMPTIVE SIMULATION LOG (No Arrival Times)\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Processes: {len(self.processes)}\n")
            f.write("All processes available at time 0\n")
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
        """Display a professional visual Gantt chart with multiple rows for better visibility"""
        if not self.gantt_chart:
            print("No Gantt chart data available")
            return

        # Calculate total time and number of segments
        total_time = max(end for _, _, end in self.gantt_chart)
        total_segments = len(self.gantt_chart)
        
        # Determine number of rows based on time or segment count
        # Each row will show approximately 15 time units or 8 segments
        max_time_per_row = 15
        max_segments_per_row = 8
        
        num_rows_by_time = max(1, int(np.ceil(total_time / max_time_per_row)))
        num_rows_by_segments = max(1, int(np.ceil(total_segments / max_segments_per_row)))
        num_rows = min(4, max(num_rows_by_time, num_rows_by_segments))  # Max 4 rows
        
        # Split the timeline into chunks
        time_chunks = []
        chunk_size = total_time / num_rows
        
        for i in range(num_rows):
            chunk_start = i * chunk_size
            chunk_end = (i + 1) * chunk_size if i < num_rows - 1 else total_time
            time_chunks.append((chunk_start, chunk_end))
        
        # Create figure with multiple subplots
        if num_rows > 1:
            fig, axes = plt.subplots(num_rows, 1, figsize=(20, 3.5 * num_rows))
            if num_rows == 1:
                axes = [axes]
        else:
            fig, axes = plt.subplots(1, 1, figsize=(20, 4))
            axes = [axes]
        
        # Get unique processes and assign colors
        unique_processes = list(set([pid for pid, _, _ in self.gantt_chart]))
        
        # Modern color palette
        modern_colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
            '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2',
            '#F8B739', '#5DADE2', '#58D68D', '#EC7063', '#AF7AC5'
        ]
        
        color_map = {pid: modern_colors[i % len(modern_colors)] 
                    for i, pid in enumerate(sorted(unique_processes))}
        
        # Process each time chunk
        for row_idx, (ax, (chunk_start, chunk_end)) in enumerate(zip(axes, time_chunks)):
            # Filter segments that belong to this time chunk
            segments_in_chunk = []
            for pid, start, end in self.gantt_chart:
                if end > chunk_start and start < chunk_end:
                    # Clip segment to chunk boundaries
                    start_in_chunk = max(start, chunk_start)
                    end_in_chunk = min(end, chunk_end)
                    if end_in_chunk > start_in_chunk:
                        segments_in_chunk.append((pid, start_in_chunk, end_in_chunk, start, end))
            
            if not segments_in_chunk:
                ax.text(0.5, 0.5, f'No processes in time range {chunk_start:.1f}-{chunk_end:.1f}', 
                    ha='center', va='center', transform=ax.transAxes, fontsize=10)
                ax.set_xlim(chunk_start, chunk_end)
                ax.set_ylim(-0.5, 0.5)
                ax.set_yticks([])
                if row_idx == num_rows - 1:
                    ax.set_xlabel('Time', fontsize=11, fontweight='bold')
                continue
            
            # Plot each segment in this row
            y_position = 0
            
            for pid, start, end, original_start, original_end in segments_in_chunk:
                duration = end - start
                
                # Draw bar with black edges
                ax.barh(y=y_position, width=duration, left=start,
                        color=color_map[pid], edgecolor='black', linewidth=2, alpha=0.85)
                
                # Add process label with background for better readability
                if duration > 0.8:
                    mid_x = start + duration / 2
                    ax.text(mid_x, y_position, f"P{pid}", ha='center', va='center',
                            fontsize=10, fontweight='bold',
                            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                                    edgecolor='black', alpha=0.9))
                elif duration > 0.3:
                    mid_x = start + duration / 2
                    ax.text(mid_x, y_position, f"{pid}", ha='center', va='center',
                            fontsize=8, fontweight='bold',
                            bbox=dict(boxstyle='round,pad=0.15', facecolor='white', 
                                    edgecolor='black', alpha=0.9))
                
                # Add markers for continuation
                if original_start < chunk_start:
                    ax.plot(chunk_start, y_position, '<', color='black', 
                        markersize=10, markeredgecolor='black', 
                        markerfacecolor='gray', markeredgewidth=1.5)
                if original_end > chunk_end:
                    ax.plot(chunk_end, y_position, '>', color='black', 
                        markersize=10, markeredgecolor='black', 
                        markerfacecolor='gray', markeredgewidth=1.5)
            
            # Configure the subplot
            ax.set_xlim(chunk_start, chunk_end)
            ax.set_ylim(-0.5, 0.5)
            ax.set_yticks([])
            
            # Set x-axis labels with proper time values
            ax.set_xlabel('Time', fontsize=11, fontweight='bold')
            
            # Format x-axis ticks to show proper time labels
            # Calculate appropriate tick intervals
            time_range = chunk_end - chunk_start
            if time_range <= 10:
                # For small ranges, show ticks every 1 unit
                tick_interval = 1
            elif time_range <= 20:
                # For medium ranges, show ticks every 2 units
                tick_interval = 2
            elif time_range <= 50:
                # For larger ranges, show ticks every 5 units
                tick_interval = 5
            else:
                # For very large ranges, show ticks every 10 units
                tick_interval = 10
            
            # Generate tick positions and labels
            tick_positions = np.arange(chunk_start, chunk_end + tick_interval, tick_interval)
            # Filter to only show ticks within the range
            tick_positions = tick_positions[tick_positions <= chunk_end]
            
            # Format tick labels to show 1 decimal place if needed
            if tick_interval < 1:
                tick_labels = [f'{tick:.1f}' for tick in tick_positions]
            else:
                tick_labels = [f'{int(tick)}' if tick == int(tick) else f'{tick:.1f}' 
                            for tick in tick_positions]
            
            ax.set_xticks(tick_positions)
            ax.set_xticklabels(tick_labels, fontsize=9, rotation=0)
            
            # Add minor ticks for better granularity
            if tick_interval > 1:
                minor_tick_interval = tick_interval / 2
                minor_ticks = np.arange(chunk_start, chunk_end + minor_tick_interval, minor_tick_interval)
                minor_ticks = minor_ticks[minor_ticks <= chunk_end]
                ax.set_xticks(minor_ticks, minor=True)
            
            # Add vertical grid lines at major tick positions
            ax.grid(True, axis='x', alpha=0.3, linestyle='--', linewidth=0.5)
            ax.set_axisbelow(True)
            
            # Add vertical lines at chunk boundaries
            ax.axvline(x=chunk_start, color='blue', linestyle='-', alpha=0.3, linewidth=1)
            ax.axvline(x=chunk_end, color='red', linestyle='-', alpha=0.3, linewidth=1)
            
            # Add title with time range and duration
            duration_str = f"{chunk_end - chunk_start:.1f}"
            ax.set_title(f'Time Slice {row_idx + 1}: {chunk_start:.1f} → {chunk_end:.1f} (Duration: {duration_str} units)', 
                        fontsize=11, fontweight='bold', pad=10)
            
            # Add background shading for alternate rows
            if row_idx % 2 == 1:
                ax.axhspan(-0.5, 0.5, alpha=0.05, color='gray')
        
        # Add overall title
        fig.suptitle(f'SJF Non-Preemptive Scheduling - Gantt Chart (Multiple Rows)\n'
                    f'Total Time: {total_time:.1f} units | {total_segments} segments | Distributed across {num_rows} rows',
                    fontsize=14, fontweight='bold', y=1.02)
        
        # Adjust layout
        plt.tight_layout()
        plt.subplots_adjust(hspace=0.4)  # Add space between rows
        plt.savefig('./results/sjf_gantt_chart.png', dpi=300, bbox_inches='tight')
        print(f"\n[SUCCESS] Visual Gantt chart saved as 'sjf_gantt_chart.png' (Split into {num_rows} rows with proper time labels)")
        plt.show()

    def display_results(self):
        """Display process table and metrics"""
        print("\n" + "=" * 80)
        print("SJF NON-PREEMPTIVE - PROCESS EXECUTION TABLE (No Arrival Times)")
        print("=" * 80)

        data = []
        for p in self.processes:
            data.append({
                'Process ID': p.id,
                'Burst Time (BT)': p.burst_time,
                'Completion Time (CT)': p.completion_time,
                'Turnaround Time (TAT)': p.turnaround_time,
                'Waiting Time (WT)': p.waiting_time,
                'Response Time (RT)': p.response_time
            })

        df = pd.DataFrame(data)
        print(df.to_string(index=False))

        avg_tat = sum(p.turnaround_time for p in self.processes) / len(self.processes)
        avg_wt = sum(p.waiting_time for p in self.processes) / len(self.processes)
        avg_rt = sum(p.response_time for p in self.processes) / len(self.processes)

        print("\n" + "=" * 80)
        print("PERFORMANCE METRICS")
        print("=" * 80)
        print(f"Total Processes Completed:        {len(self.processes)}")
        print(f"Execution Order:                  {', '.join([f'P{p.id}' for p in self.processes if hasattr(p, 'completion_time')])}")
        print(f"Average Turnaround Time (ATT):    {avg_tat:.2f}")
        print(f"Average Waiting Time (AWT):       {avg_wt:.2f}")
        print(f"Average Response Time (ART):      {avg_rt:.2f}")
        print(f"Total Context Switches:           {len(self.gantt_chart) - 1}")
        print(f"Total Completion Time:            {self.current_time:.2f}")
        print("=" * 80)

    def export_results(self, filename: str = "./results/sjf_simulation_results.csv"):
        """Export results to CSV file"""
        # Create a list of completion times to determine execution order
        processes_with_completion = [(p.id, p.completion_time) for p in self.processes if hasattr(p, 'completion_time')]
        # Sort by completion time to get execution order
        processes_with_completion.sort(key=lambda x: x[1])
        
        # Create a mapping from process ID to execution order
        execution_order_map = {pid: idx + 1 for idx, (pid, _) in enumerate(processes_with_completion)}
        
        data = []
        for p in self.processes:
            data.append({
                'process_id': p.id,
                'burst_time': p.burst_time,
                'completion_time': p.completion_time,
                'turnaround_time': p.turnaround_time,
                'waiting_time': p.waiting_time,
                'response_time': p.response_time,
                'execution_order': execution_order_map.get(p.id, None)  # Get execution order if completed
            })

        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"\n[SUCCESS] Results exported to {filename}")