from collections import deque

from process_loader import arrange_processes, get_processes
from scheduler_report import (
    display_results,
    log_event,
    save_gantt_chart,
    save_log,
    save_results,
    update_completed_process,
)


TIME_QUANTUM = 5


def add_arrived_processes(process_list, ready_queue, current_time, logs):
    """Move every process that has arrived into the ready queue."""
    while process_list and process_list[0].arrival_time <= current_time:
        process = process_list.pop(0)
        ready_queue.append(process)
        log_event(logs, current_time, f"P{process.id} arrived and entered the ready queue")


def roundrobin(time_quantum=TIME_QUANTUM):
    """Run Round Robin scheduling using the generated CSV process data."""
    processes = arrange_processes(get_processes())
    process_list = processes.copy()
    ready_queue = deque()
    logs = []
    gantt_chart = []
    current_time = 0
    completed_processes = 0

    log_event(logs, current_time, "Round Robin simulation started")
    log_event(logs, current_time, f"Time quantum = {time_quantum}")

    while completed_processes < len(processes):
        add_arrived_processes(process_list, ready_queue, current_time, logs)

        if not ready_queue:
            current_time = process_list[0].arrival_time
            log_event(logs, current_time, "CPU was idle until the next process arrived")
            continue

        current_process = ready_queue.popleft()

        if current_process.response_time == -1:
            current_process.response_time = current_time - current_process.arrival_time

        run_time = min(time_quantum, current_process.remaining_time)
        start_time = current_time
        current_time += run_time
        current_process.remaining_time -= run_time
        gantt_chart.append((current_process.id, start_time, current_time))

        log_event(
            logs,
            current_time,
            f"P{current_process.id} ran from {start_time} to {current_time} "
            f"(remaining time: {current_process.remaining_time})",
        )

        add_arrived_processes(process_list, ready_queue, current_time, logs)

        if current_process.remaining_time == 0:
            update_completed_process(current_process, current_time)
            completed_processes += 1
            log_event(logs, current_time, f"P{current_process.id} completed")
        else:
            ready_queue.append(current_process)
            log_event(logs, current_time, f"P{current_process.id} returned to the ready queue")

    log_event(logs, current_time, "Round Robin simulation completed")
    save_log(processes, logs, gantt_chart, current_time, time_quantum)
    save_results(processes)
    save_gantt_chart(gantt_chart)
    display_results(processes, gantt_chart, current_time)


if __name__ == "__main__":
    roundrobin()
