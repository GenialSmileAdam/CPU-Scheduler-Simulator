import pandas as pd
import matplotlib.pyplot as plt

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
        procs = sorted(self.processes, key=lambda p: p.arrival_time) # type: ignore
        
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
        if not self.gantt:
            print("No Gantt chart data available")
            return

        segments_per_row = 40
        total_segments = len(self.gantt)
        num_rows = (total_segments + segments_per_row - 1) // segments_per_row

        fig, axes = plt.subplots(num_rows, 1, figsize=(16, max(3, 2.2 * num_rows)), squeeze=False)

        unique_processes = list(set([pid for pid, _, _ in self.gantt]))
        try:
            colormap = plt.get_cmap('tab20')
            colors = [colormap(i) for i in range(len(unique_processes))]
        except:
            colormap = plt.get_cmap('Set3')
            colors = [colormap(i % 12) for i in range(len(unique_processes))]

        color_map = {pid: colors[i] for i, pid in enumerate(sorted(unique_processes))}

        for row_idx in range(num_rows):
            ax = axes[row_idx][0]
            start_idx = row_idx * segments_per_row
            end_idx = min((row_idx + 1) * segments_per_row, total_segments)
            row_segments = self.gantt[start_idx:end_idx]

            if not row_segments:
                continue

            row_start_time = row_segments[0][1]
            time_offset = row_start_time

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

            ax.set_xlabel('Time', fontsize=10, fontweight='bold')
            ax.set_ylabel('CPU', fontsize=10, fontweight='bold')
            ax.set_ylim(-0.5, 0.5)
            ax.set_yticks([])
            ax.grid(axis='x', alpha=0.3, linestyle=':', linewidth=0.5)

            max_time_in_row = max([end - time_offset for _, _, end in row_segments])
            ax.set_xlim(-0.5, max_time_in_row + 1)

            xticks = range(0, int(max_time_in_row) + 1, max(1, int(max_time_in_row / 10)))
            ax.set_xticks(xticks)
            ax.set_xticklabels([str(int(row_start_time + tick)) for tick in xticks])

            if row_idx == 0:
                ax.set_title('SRTF Scheduling - Gantt Chart',
                             fontsize=12, fontweight='bold')

        plt.tight_layout()
        plt.savefig('./results/srtf_gantt_chart.png', dpi=300, bbox_inches='tight')
        print("✓ Saved: ./results/srtf_gantt_chart.png")