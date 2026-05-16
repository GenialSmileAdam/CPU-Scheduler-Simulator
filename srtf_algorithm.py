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
        fig, ax = plt.subplots(figsize=(12, 2))
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        merged = []
        for pid, s, e in self.gantt:
            if merged and merged[-1][0] == pid and merged[-1][2] == s:
                merged[-1] = (pid, merged[-1][1], e)
            else:
                merged.append((pid, s, e))
        
        for pid, s, e in merged:
            ax.barh(0, e-s, left=s, color=colors[pid%5], edgecolor='black')
            if e-s > 0.5:
                ax.text(s+(e-s)/2, 0, f"P{pid}", ha='center', va='center', fontsize=8)
        
        ax.set_yticks([])
        ax.set_xlabel('Time')
        ax.set_title('SRTF Gantt Chart')
        plt.tight_layout()
        plt.savefig('./results/srtf_simulation_gantt.png', dpi=150)
        plt.show()
        print("✓ Saved: ./results/srtf_simulation_gantt.png")