import pandas as pd 
from collections import deque

data = pd.read_csv("./static/data", index_col="process_id"   )

print(data.head())
