Here's a brief and simple README:


# Process Data Generator

Generates random process scheduling data (arrival time & burst time) for 30-60 processes.

## Setup

```bash
pip install pandas numpy
```

## Generate Data

Run the script:
```bash
python generator.py
```

This creates:
- `static/` folder
- `static/data` CSV file with process data

## Load the Data

```python
import pandas as pd

data = pd.read_csv("./static/data")
print(data.head())
```

## Output Format

| process_id | arrival_time | burst_time |
|------------|--------------|------------|
| 0 | 12 | 35 |
| 1 | 5 | 42 |

- **arrival_time**: 0-30 time units
- **burst_time**: 0-50 time units



That's it! Just run the script and load the CSV with pandas.