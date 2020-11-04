from sys import argv
import pandas as pd
from pathlib import Path

# the only dataset available currently has an asset path to the containing directory
# Temporarily add suffix to get the data in the dir
path = Path(argv[1], "test_data.csv")

data = pd.read_csv(str(path))
df = pd.DataFrame(data)
print(df.head(10))