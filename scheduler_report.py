import csv
import os
from datetime import datetime


LOG_FILENAME = "./results/round_robin_simulation_log.txt"
RESULTS_FILENAME = "./results/round_robin_simulation_results.csv"
GANTT_CHART_FILENAME = "./results/round_robin_gantt_chart.txt"
GANTT_DATA_FILENAME = "./results/round_robin_gantt_chart.csv"


def log_event(logs, current_time, message):
    """Print an event and keep it for the result log file."""
    event = f"[Time {current_time:<6}] {message}"
    print(event)
    logs.append(event)


def update_completed_process(process, current_time):
    """Calculate completion, turnaround, and waiting time."""
    process.completion_time = current_time
    process.turnaround_time = process.completion_time - process.arrival_time
    process.waiting_time = process.turnaround_time - process.burst_time


def save_log(processes, logs, gantt_chart, current_time, time_quantum):
    """Save the simulation log to the results folder."""
    os.makedirs("./results", exist_ok=True)

    with open(LOG_FILENAME, "w", encoding="utf-8") as file:
        file.write("ROUND ROBIN SIMULATION LOG\n")
        file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        file.write(f"Time Quantum: {time_quantum}\n")
        file.write("=" * 60 + "\n\n")

        for event in logs:
            file.write(event + "\n")

        file.write("\n" + "=" * 60 + "\n")
        file.write("SUMMARY\n")
        file.write(f"Average Waiting Time: {average_waiting_time(processes):.2f}\n")
        file.write(f"Average Turnaround Time: {average_turnaround_time(processes):.2f}\n")
        file.write(f"Average Response Time: {average_response_time(processes):.2f}\n")
        file.write(f"Context Switches: {max(0, len(gantt_chart) - 1)}\n")
        file.write(f"Total Completion Time: {current_time}\n")
        file.write(f"CPU Utilization: {cpu_utilization(gantt_chart, current_time):.2f}%\n")
        file.write(f"Throughput: {throughput(processes, current_time):.4f} processes/unit time\n")

    print(f"\nLog saved to {LOG_FILENAME}")


def save_results(processes):
    """Save each process result to a CSV file."""
    os.makedirs("./results", exist_ok=True)

    with open(RESULTS_FILENAME, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "process_id",
                "arrival_time",
                "burst_time",
                "completion_time",
                "turnaround_time",
                "waiting_time",
                "response_time",
            ]
        )

        for process in processes:
            writer.writerow(
                [
                    process.id,
                    process.arrival_time,
                    process.burst_time,
                    process.completion_time,
                    process.turnaround_time,
                    process.waiting_time,
                    process.response_time,
                ]
            )

    print(f"Results saved to {RESULTS_FILENAME}")


def save_gantt_chart(gantt_chart):
    """Save the execution order as a simple Gantt chart."""
    os.makedirs("./results", exist_ok=True)

    with open(GANTT_CHART_FILENAME, "w", encoding="utf-8") as file:
        file.write("ROUND ROBIN GANTT CHART\n")
        file.write("=" * 60 + "\n\n")

        for row in split_gantt_chart(gantt_chart):
            labels = " | ".join(f"P{process_id}" for process_id, _, _ in row)
            times = " -> ".join(str(start_time) for _, start_time, _ in row)
            times = f"{times} -> {row[-1][2]}"

            file.write(f"| {labels} |\n")
            file.write(f"{times}\n\n")

    with open(GANTT_DATA_FILENAME, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["process_id", "start_time", "end_time", "duration"])

        for process_id, start_time, end_time in gantt_chart:
            writer.writerow([process_id, start_time, end_time, end_time - start_time])

    print(f"Gantt chart saved to {GANTT_CHART_FILENAME}")
    print(f"Gantt chart data saved to {GANTT_DATA_FILENAME}")


def split_gantt_chart(gantt_chart, row_size=12):
    """Break a long Gantt chart into readable rows."""
    return [
        gantt_chart[index : index + row_size]
        for index in range(0, len(gantt_chart), row_size)
    ]


def display_results(processes, gantt_chart, current_time):
    """Print the final process table and simple metrics."""
    print("\nProgram No.\tArrival Time\tBurst Time\tWait Time\tTurnaround Time")

    for process in processes:
        print(
            f"P{process.id}\t\t{process.arrival_time}\t\t"
            f"{process.burst_time}\t\t{process.waiting_time}\t\t"
            f"{process.turnaround_time}"
        )

    print(f"\nAverage wait time: {average_waiting_time(processes):.2f}")
    print(f"Average turnaround time: {average_turnaround_time(processes):.2f}")
    print(f"Average response time: {average_response_time(processes):.2f}")
    print(f"Context switches: {max(0, len(gantt_chart) - 1)}")
    print(f"Total completion time: {current_time}")
    print(f"CPU utilization: {cpu_utilization(gantt_chart, current_time):.2f}%")
    print(f"Throughput: {throughput(processes, current_time):.4f} processes/unit time")


def average_waiting_time(processes):
    return sum(process.waiting_time for process in processes) / len(processes)


def average_turnaround_time(processes):
    return sum(process.turnaround_time for process in processes) / len(processes)


def average_response_time(processes):
    return sum(process.response_time for process in processes) / len(processes)


def cpu_utilization(gantt_chart, total_time):
    if total_time == 0:
        return 0

    busy_time = sum(end_time - start_time for _, start_time, end_time in gantt_chart)
    return (busy_time / total_time) * 100


def throughput(processes, total_time):
    if total_time == 0:
        return 0

    return len(processes) / total_time
