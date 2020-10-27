from sys import argv
import pandas as pd

data = pd.read_csv(argv[1])
df = pd.DataFrame(data)
print(df.head(10))