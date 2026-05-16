import csv
import os
from random import randint


STATIC_FOLDER = "./static"
CSV_FILENAME = "./static/data.csv"
NUMBER_OF_PROCESSES = 20
ARRIVAL_TIME_MIN = 0
ARRIVAL_TIME_MAX = 30
BURST_TIME_MIN = 1
BURST_TIME_MAX = 50


def generate_process_data(number_of_processes=NUMBER_OF_PROCESSES):
    """Generate random process data for the scheduler simulations."""
    processes = []

    for process_id in range(1, number_of_processes + 1):
        processes.append(
            {
                "process_id": process_id,
                "arrival_time": randint(ARRIVAL_TIME_MIN, ARRIVAL_TIME_MAX),
                "burst_time": randint(BURST_TIME_MIN, BURST_TIME_MAX),
            }
        )

    return processes


def save_process_data(processes, filename=CSV_FILENAME):
    """Save generated process data to a CSV file."""
    os.makedirs(STATIC_FOLDER, exist_ok=True)

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["process_id", "arrival_time", "burst_time"],
        )
        writer.writeheader()
        writer.writerows(processes)


def main():
    processes = generate_process_data()
    save_process_data(processes)

    print(f"Generated {len(processes)} processes.")
    print(f"Data saved to {CSV_FILENAME}")


if __name__ == "__main__":
    main()
