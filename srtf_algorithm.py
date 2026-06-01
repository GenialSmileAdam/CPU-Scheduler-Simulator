import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

class SRTFScheduler:
    def __init__(self, processes):
        self.processes = processes
        self.gantt = []
        self.log = []
    
    def log_event(self, msg):
        print(msg)
        self.log.append(msg)
    
    def log_ready_queue(self, ready):
        if ready:
            queue_str = ', '.join([f"P{p.id}({p.remaining_time})" for p in sorted(ready, key=lambda x: x.remaining_time)])
            self.log_event(f"  Ready Queue: [{queue_str}]")
    
    def run(self):
        time, done, idx, ready = 0, 0, 0, []
        procs = sorted(self.processes, key=lambda p: p.arrival_time)
        
        self.log_event("="*60)
        self.log_event("SRTF SIMULATION STARTED")
        self.log_event("="*60)
        
        while done < len(procs):
            # Add arrived processes
            while idx < len(procs) and procs[idx].arrival_time <= time:
                p = procs[idx]
                p.remaining_time = p.burst_time
                p.response_time = -1
                ready.append(p)
                self.log_event(f"[T{time}] P{p.id} arrived")
                idx += 1
            
            if not ready:
                time = procs[idx].arrival_time
                continue
            
            # Sort by remaining time and log queue
            ready.sort(key=lambda x: x.remaining_time)
            self.log_ready_queue(ready)
            
            # Run shortest process
            p = ready.pop(0)
            
            if p.response_time == -1:
                p.response_time = time - p.arrival_time
                self.log_event(f"[T{time}] P{p.id} FIRST RUN (RT={p.response_time})")
            
            # Find next event
            next_arrival = procs[idx].arrival_time if idx < len(procs) else float('inf')
            run_time = min(p.remaining_time, next_arrival - time)
            start = time
            time += run_time
            p.remaining_time -= run_time
            self.gantt.append((p.id, start, time))
            self.log_event(f"[T{start}->{time}] P{p.id} runs (rem={p.remaining_time})")
            
            if p.remaining_time == 0:
                p.completion_time = time
                p.turnaround_time = time - p.arrival_time
                p.waiting_time = p.turnaround_time - p.burst_time
                done += 1
                self.log_event(f"[DONE] P{p.id} (TAT={p.turnaround_time}, WT={p.waiting_time}) [{done}/{len(procs)}]")
            else:
                ready.append(p)
                self.log_event(f"[PREEMPTED] P{p.id} added back to queue")
        
        self.log_event("="*60)
        self.log_event("SRTF SIMULATION COMPLETED")
        self.log_event("="*60)
    
    def save_results(self):
        # Save log
        with open('./results/srtf_simulation_log.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.log))
            f.write(f"\n\n{'='*60}\n")
            f.write(f"SUMMARY STATISTICS\n")
            f.write(f"{'='*60}\n")
            f.write(f"ATT: {sum(p.turnaround_time for p in self.processes)/len(self.processes):.2f}\n")
            f.write(f"AWT: {sum(p.waiting_time for p in self.processes)/len(self.processes):.2f}\n")
            f.write(f"ART: {sum(p.response_time for p in self.processes)/len(self.processes):.2f}\n")
            f.write(f"Context Switches: {len(self.gantt)-1}\n")
            f.write(f"Total Time: {max(p.completion_time for p in self.processes)}\n")
        
        # Save CSV
        pd.DataFrame([{
            'id': p.id, 'arrival_time': p.arrival_time, 'burst_time': p.burst_time,
            'completion_time': p.completion_time, 'turnaround_time': p.turnaround_time, 
            'waiting_time': p.waiting_time, 'response_time': p.response_time
        } for p in self.processes]).to_csv('./results/srtf_simulation_results.csv', index=False)
        
        print("\n✓ Saved: ./results/srtf_simulation_log.txt, ./results/srtf_simulation_results.csv")
    
    def plot_gantt(self):
        # Merge consecutive same process segments
        merged = []
        for pid, s, e in self.gantt:
            if merged and merged[-1][0] == pid and merged[-1][2] == s:
                merged[-1] = (pid, merged[-1][1], e)
            else:
                merged.append((pid, s, e))
        
        # Calculate total time
        total_time = max(e for _, _, e in merged)
        
        # Define maximum time span per row (in time units)
        max_time_per_row = 15  # Each row will show max 15 time units
        
        # Calculate how many rows we need
        num_rows = max(1, int(np.ceil(total_time / max_time_per_row)))
        num_rows = min(num_rows, 4)  # Limit to 4 rows maximum
        
        # Split the timeline into chunks
        time_chunks = []
        chunk_size = total_time / num_rows
        
        for i in range(num_rows):
            chunk_start = i * chunk_size
            chunk_end = (i + 1) * chunk_size if i < num_rows - 1 else total_time
            time_chunks.append((chunk_start, chunk_end))
        
        # Create figure with multiple subplots (one per row)
        fig, axes = plt.subplots(num_rows, 1, figsize=(16, num_rows * 3.0))
        if num_rows == 1:
            axes = [axes]
        
        # Beautiful color palette
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
                  '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2']
        
        for row_idx, (ax, (chunk_start, chunk_end)) in enumerate(zip(axes, time_chunks)):
            # Filter segments that belong to this time chunk
            segments_in_chunk = []
            for pid, s, e in merged:
                if e > chunk_start and s < chunk_end:
                    # Clip segment to chunk boundaries
                    start_in_chunk = max(s, chunk_start)
                    end_in_chunk = min(e, chunk_end)
                    if end_in_chunk > start_in_chunk:
                        segments_in_chunk.append((pid, start_in_chunk, end_in_chunk, s, e))
            
            if not segments_in_chunk:
                ax.text(0.5, 0.5, f'No processes in time range {chunk_start:.1f}-{chunk_end:.1f}', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=12)
                ax.set_xlim(chunk_start, chunk_end)
                continue
            
            # Bar height
            bar_height = 1.2
            y_position = 0.5
            
            for pid, start, end, original_s, original_e in segments_in_chunk:
                duration = end - start
                
                # Draw rectangle with BLACK borders instead of white
                rect = Rectangle((start, y_position - bar_height/2), duration, bar_height,
                               facecolor=colors[pid % len(colors)],
                               edgecolor='black',  # Changed from white to black
                               linewidth=2.5,
                               alpha=0.85)
                ax.add_patch(rect)
                
                # Add process label with larger font and black outline for better readability
                if duration > 0.5:
                    ax.text(start + duration/2, y_position, f'P{pid}',
                           ha='center', va='center',
                           fontsize=12, fontweight='bold',
                           color='white',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7))
                elif duration > 0.2:
                    ax.text(start + duration/2, y_position, f'{pid}',
                           ha='center', va='center',
                           fontsize=10, fontweight='bold',
                           color='white',
                           bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.7))
                
                # Add small markers for continuation with BLACK borders
                if original_s < chunk_start:
                    ax.plot(chunk_start, y_position, 'k<', markersize=12, 
                           markeredgecolor='black', markerfacecolor='gray', markeredgewidth=1.5)
                if original_e > chunk_end:
                    ax.plot(chunk_end, y_position, 'k>', markersize=12,
                           markeredgecolor='black', markerfacecolor='gray', markeredgewidth=1.5)
            
            # Configure the subplot
            ax.set_xlim(chunk_start, chunk_end)
            ax.set_ylim(-0.8, 1.3)
            ax.set_yticks([])
            ax.set_ylabel('CPU Core', fontsize=11, fontweight='bold')
            ax.set_xlabel('Time', fontsize=11, fontweight='bold')
            ax.set_title(f'Time Slice {row_idx + 1}: {chunk_start:.1f} → {chunk_end:.1f}', 
                        fontsize=13, fontweight='bold', pad=15)
            
            # Add grid with better visibility
            ax.grid(True, axis='x', alpha=0.3, linestyle='--', linewidth=0.8)
            ax.set_axisbelow(True)
            
            # Format x-axis ticks
            num_ticks = min(10, int(chunk_end - chunk_start))
            if num_ticks > 0:
                tick_step = (chunk_end - chunk_start) / num_ticks
                ax.xaxis.set_major_locator(plt.MultipleLocator(tick_step))
            
            # Add background shading for better readability
            ax.axhspan(-0.8, 1.3, alpha=0.03, color='gray')
        
        # Overall title
        fig.suptitle(f'SRTF Gantt Chart - Distributed across {num_rows} Time Slices\n(Total Time: {total_time:.1f} units)', 
                    fontsize=16, fontweight='bold', y=1.02)
        
        # Adjust layout with more spacing
        plt.tight_layout()
        plt.subplots_adjust(hspace=0.4)
        plt.savefig('./results/srtf_simulation_gantt.png', dpi=150, bbox_inches='tight')
        plt.show()
        print(f"✓ Saved: ./results/srtf_simulation_gantt.png (Split into {num_rows} time slices with black borders)")
    
    def plot_gantt_alternative(self):
        """Alternative approach: Show each process on its own row with thicker bars and black borders"""
        # Merge consecutive same process segments
        merged = []
        for pid, s, e in self.gantt:
            if merged and merged[-1][0] == pid and merged[-1][2] == s:
                merged[-1] = (pid, merged[-1][1], e)
            else:
                merged.append((pid, s, e))
        
        # Get unique processes
        unique_pids = sorted(set(pid for pid, _, _ in merged))
        num_processes = len(unique_pids)
        
        # Create figure with one row per process
        fig, ax = plt.subplots(figsize=(16, max(6, num_processes * 1.2)))
        
        # Beautiful color palette
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
                  '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2']
        
        # Map each process to a y-position
        pid_to_y = {pid: i for i, pid in enumerate(unique_pids)}
        
        # Bar height
        bar_height = 0.8
        y_offset = bar_height / 2
        
        # Plot segments for each process
        for pid, start, end in merged:
            y_pos = pid_to_y[pid]
            duration = end - start
            
            # Draw rectangle with BLACK borders instead of white
            rect = Rectangle((start, y_pos - bar_height/2), duration, bar_height,
                           facecolor=colors[pid % len(colors)],
                           edgecolor='black',  # Changed from white to black
                           linewidth=2.5,
                           alpha=0.85)
            ax.add_patch(rect)
            
            # Add label with black background for better readability
            if duration > 0.5:
                ax.text(start + duration/2, y_pos, f'Process {pid}',
                       ha='center', va='center',
                       fontsize=10, fontweight='bold',
                       color='white',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7))
            else:
                ax.text(start + duration/2, y_pos, f'P{pid}',
                       ha='center', va='center',
                       fontsize=9, fontweight='bold',
                       color='white',
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='black', alpha=0.7))
        
        # Configure the plot
        total_time = max(e for _, _, e in merged)
        ax.set_xlim(0, total_time)
        ax.set_ylim(-0.8, num_processes - 0.2)
        ax.set_yticks(range(num_processes))
        ax.set_yticklabels([f'Process {pid}' for pid in unique_pids], fontsize=11)
        ax.set_xlabel('Time', fontsize=13, fontweight='bold')
        ax.set_ylabel('Processes', fontsize=13, fontweight='bold')
        ax.set_title('SRTF Gantt Chart - Per Process View (Black Borders)', 
                    fontsize=15, fontweight='bold', pad=20)
        
        # Add grid
        ax.grid(True, axis='x', alpha=0.3, linestyle='--', linewidth=0.8)
        ax.set_axisbelow(True)
        
        # Add horizontal lines to separate processes
        for i in range(num_processes - 1):
            ax.axhline(y=i + 0.5, color='black', linestyle='-', alpha=0.15, linewidth=1)
        
        # Format x-axis
        num_ticks = min(15, int(total_time))
        if num_ticks > 0:
            tick_step = max(1, total_time / num_ticks)
            ax.xaxis.set_major_locator(plt.MultipleLocator(tick_step))
        
        plt.tight_layout()
        plt.savefig('./results/srtf_simulation_gantt_per_process.png', dpi=150, bbox_inches='tight')
        plt.show()
        print("✓ Saved: ./results/srtf_simulation_gantt_per_process.png (Black borders for better visibility)")