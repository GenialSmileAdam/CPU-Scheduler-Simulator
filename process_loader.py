import csv

from process import Process


CSV_FILENAME = "./static/data.csv"


def get_processes(filename=CSV_FILENAME):
    """Load process data from the CSV file."""
    processes = []

    with open(filename, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            processes.append(
                Process(
                    id=int(row["process_id"]),
                    arrival_time=int(row["arrival_time"]),
                    burst_time=int(row["burst_time"]),
                )
            )

    return processes


def arrange_processes(processes):
    """Sort processes by arrival time, then by process id."""
    return sorted(processes, key=lambda process: (process.arrival_time, process.id))
