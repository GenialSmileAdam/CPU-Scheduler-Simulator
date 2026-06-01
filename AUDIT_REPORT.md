# CPU Scheduler Algorithms - Audit Report

## Overview
This audit verifies that all three scheduling algorithms correctly handle **arrival time** (when processes actually arrive) vs **arrival order** (the order they appear when sorted by arrival time).

---

## Algorithm Analysis

### 1. SJF (Shortest Job First) - Non-Preemptive

**File:** `sjf_algorithm.py`

#### What it Should Do:
- Select processes that have arrived (arrival_time ≤ current_time)
- Among arrived processes, select the one with **shortest burst time**
- When burst times are equal, use **arrival time** as tiebreaker
- When arrival times are equal, use **arrival order** (index in original sorted list)
- Run selected process to completion (non-preemptive)

#### Current Implementation:

**Line 10:** Sorts by arrival_time ✓
```python
self.processes = sorted(processes, key=lambda p: p.arrival_time)
```

**Lines 40-43:** Gets all arrived processes correctly ✓
```python
arrived = [p for p in self.processes if p.arrival_time <= self.current_time ...]
```

**Line 59:** Uses correct tiebreaker logic ✓
```python
current_process = min(arrived, key=lambda p: (p.burst_time, p.arrival_time, self.processes.index(p)))
```
- Primary: burst_time (shortest)
- Secondary: arrival_time (earliest arrival)
- Tertiary: arrival_order (first in sorted list)

**Status: ✅ CORRECT** - After recent fix (commit 5e9aaa8)

---

### 2. SRTF (Shortest Remaining Time First) - Preemptive

**File:** `srtf_algorithm.py`

#### What it Should Do:
- Preemptive version of SJF
- At each time step, add newly arrived processes
- Among ready processes, select the one with **shortest remaining time**
- Can preempt (interrupt) the running process if a shorter one arrives
- When remaining times are equal, use **arrival time** as tiebreaker

#### Current Implementation:

**Line 21:** Sorts by arrival_time ✓
```python
procs = sorted(self.processes, key=lambda p: p.arrival_time)
```

**Lines 29-35:** Adds arrived processes correctly ✓
```python
while idx < len(procs) and procs[idx].arrival_time <= time:
    p = procs[idx]
    p.remaining_time = p.burst_time
    ready.append(p)
```

**Lines 42-46:** Selects by remaining time and handles preemption ⚠️
```python
ready.sort(key=lambda x: x.remaining_time)  # Line 42
p = ready.pop(0)  # Line 46
```

**Issue Identified:** When remaining times are equal, `sort()` doesn't have a tiebreaker. This could cause non-deterministic behavior or use arrival order instead of arrival time.

**Status: ⚠️ NEEDS FIX** - Missing tiebreaker for equal remaining times

---

### 3. Round Robin

**File:** `round_robin_algorithm.py`

#### What it Should Do:
- Each process gets a fixed time quantum
- When a process's time quantum expires, it goes to the back of the queue
- Processes enter queue when they arrive (arrival_time ≤ current_time)
- FIFO within the ready queue (no priority, just FIFO order)

#### Current Implementation:

**Lines 27-30:** Gets processes and creates queue ✓
```python
processes = arrange_processes(get_processes())  # Sorts by arrival_time, then id
process_list = processes.copy()
ready_queue = deque()
```

**Lines 19-22:** Adds arrived processes to queue correctly ✓
```python
while process_list and process_list[0].arrival_time <= current_time:
    process = process_list.pop(0)
    ready_queue.append(process)
```

**Lines 46-72:** Manages queue with time quantum correctly ✓
```python
current_process = ready_queue.popleft()
run_time = min(time_quantum, current_process.remaining_time)
# ... run process
if current_process.remaining_time == 0:
    completed_processes += 1
else:
    ready_queue.append(current_process)  # Back to queue
```

**Status: ✅ CORRECT**

---

## Data Generator Analysis

**File:** `data_generator.py`

#### Parameters:
- **NUMBER_OF_PROCESSES:** 40 (default)
- **ARRIVAL_TIME_MIN:** 1
- **ARRIVAL_TIME_MAX:** 50
- **BURST_TIME_MIN:** 1
- **BURST_TIME_MAX:** 50

#### Issue: Arrival time starts at 1, not 0
Modern OS scheduling assignments typically expect arrival times to include 0 (some processes arrive immediately). Current range 1-50 means all processes arrive after time 0.

**Status: ⚠️ PARAMETER ISSUE** - Should allow arrival time of 0

---

## Summary of Findings

| Algorithm | Status | Issues |
|-----------|--------|--------|
| **SJF** | ✅ CORRECT | None - recent fix is correct |
| **SRTF** | ⚠️ NEEDS FIX | Missing tiebreaker for equal remaining times |
| **Round Robin** | ✅ CORRECT | None |
| **Data Generator** | ⚠️ PARAMETER ISSUE | Arrival time should start from 0, not 1 |

---

## Recommended Fixes

### 1. Fix SRTF Tiebreaker (HIGH PRIORITY)
In `srtf_algorithm.py` line 42, add explicit sorting key with tiebreaker:

**Current:**
```python
ready.sort(key=lambda x: x.remaining_time)
```

**Should be:**
```python
ready.sort(key=lambda x: (x.remaining_time, x.arrival_time))
```

### 2. Fix Data Generator (MEDIUM PRIORITY)
In `data_generator.py` line 9-10, change arrival time range:

**Current:**
```python
ARRIVAL_TIME_MIN = 1
ARRIVAL_TIME_MAX = 50
```

**Should be:**
```python
ARRIVAL_TIME_MIN = 0
ARRIVAL_TIME_MAX = 50
```

---

## Test Case Verification

### Example Test Data:
| Process | Arrival Time | Burst Time |
|---------|--------------|-----------|
| P1      | 0            | 8         |
| P2      | 1            | 4         |
| P3      | 2            | 2         |
| P4      | 3            | 4         |

### Expected Execution Order:

**SJF (Non-Preemptive):**
1. Time 0: P1 arrives (only one), runs P1 (0-8)
2. Time 8: P2,P3,P4 arrived, P3 has shortest (2), run P3 (8-10)
3. Time 10: P2,P4 in queue, both have 4, use arrival time: P2 (10-14)
4. Time 14: P4 runs (14-18)

**SRTF (Preemptive):**
1. Time 0: P1 arrives, runs P1
2. Time 1: P2 arrives (burst 4 > remaining 7), continue P1
3. Time 2: P3 arrives (burst 2 < remaining 6), **preempt P1**, run P3
4. Time 4: P4 arrives (burst 4), P1 remaining 6 > 4, **preempt P3**, run P4
5. Time 8: P1 arrives as ready, runs P1 (remaining 6)
6. Time 14: P2 runs (remaining 4)
...etc

**Round Robin (TQ=5):**
1. Time 0: P1 arrives, runs 5 units (0-5)
2. Time 1: P2 arrives, added to queue
3. Time 2: P3 arrives, added to queue
4. Time 3: P4 arrives, added to queue
5. Time 5: P1 goes back (remaining 3), P2 runs 4 units (5-9, completes)
6. Time 9: P3 runs 2 units (9-11, completes)
7. Time 11: P4 runs 4 units (11-15, completes)
8. Time 15: P1 runs 3 units (15-18, completes)

