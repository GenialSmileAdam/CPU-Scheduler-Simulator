import csv
import os
from datetime import datetime

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib.pyplot as plt


LOG_FILENAME = "./results/round_robin_simulation_log.txt"
RESULTS_FILENAME = "./results/round_robin_simulation_results.csv"
GANTT_CHART_FILENAME = "./results/round_robin_gantt_chart.txt"
GANTT_DATA_FILENAME = "./results/round_robin_gantt_chart.csv"
GANTT_IMAGE_FILENAME = "./results/round_robin_gantt_chart.png"


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

    if not gantt_chart:
        print("No Gantt chart data to save")
        return

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

    save_gantt_chart_image(gantt_chart)

    print(f"Gantt chart saved to {GANTT_CHART_FILENAME}")
    print(f"Gantt chart data saved to {GANTT_DATA_FILENAME}")
    print(f"Gantt chart image saved to {GANTT_IMAGE_FILENAME}")


def save_gantt_chart_image(gantt_chart):
    """Save the Gantt chart as a PNG image."""
    segments_per_row = 40
    rows = split_gantt_chart(gantt_chart, segments_per_row)
    figure_height = max(3, 2.2 * len(rows))
    fig, axes = plt.subplots(len(rows), 1, figsize=(16, figure_height), squeeze=False)

    process_ids = sorted({process_id for process_id, _, _ in gantt_chart})
    colormap = plt.get_cmap("tab20")
    colors = {
        process_id: colormap(index % colormap.N)
        for index, process_id in enumerate(process_ids)
    }

    for row_index, row in enumerate(rows):
        ax = axes[row_index][0]
        row_start_time = row[0][1]

        for process_id, start_time, end_time in row:
            duration = end_time - start_time
            left = start_time - row_start_time

            ax.barh(
                y=0,
                width=duration,
                left=left,
                color=colors[process_id],
                edgecolor="black",
                linewidth=1,
            )

            if duration > 0:
                ax.text(
                    left + duration / 2,
                    0,
                    f"P{process_id}",
                    ha="center",
                    va="center",
                    fontsize=8,
                    fontweight="bold",
                )

        row_end_time = row[-1][2]
        ax.set_xlim(-0.5, row_end_time - row_start_time + 0.5)
        ax.set_ylim(-0.5, 0.5)
        ax.set_yticks([])
        ax.set_xlabel(f"Time from {row_start_time}", fontsize=10)
        ax.grid(axis="x", alpha=0.3, linestyle=":", linewidth=0.5)

        if row_index == 0:
            ax.set_title("Round Robin Scheduling - Gantt Chart", fontweight="bold")

    plt.tight_layout()
    plt.savefig(GANTT_IMAGE_FILENAME, dpi=300, bbox_inches="tight")
    plt.close(fig)


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
