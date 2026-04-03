from db import engine
import pandas as pd

df = pd.read_sql("SELECT 1", engine)
print(df)