import pandas as pd 

data = pd.read_csv("./static/data", index_col="process_id"   )

print(data.head())
