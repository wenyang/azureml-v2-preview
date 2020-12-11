from sys import argv
import pandas as pd
from pathlib import Path
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--dataset", type=str, default=False)
parser.add_argument("--lr", type=float, default=False)

args = parser.parse_args()

# what's in my current working directory?
ls_output = os.system("ls -l")
print(ls_output)

# what's in the dataset file/directory?
ls_output = os.system(f"ls -l {args.dataset}")
print(ls_output)

print(f"Got learning rate {args.lr}")

print(f"Got dataset {args.dataset}")

# the only dataset available currently has an asset path to the containing directory
# Temporarily add suffix to get the data in the dir
path = Path(args.dataset, "sample1.csv")
# path = Path(args.dataset)

data = pd.read_csv(str(path))
df = pd.DataFrame(data)
print(df.head(10))
