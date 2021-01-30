import os
import time

def train():
    time.sleep(300)
    print("Training...")
    import torch
    print(torch.cuda.current_device())
    print(torch.cuda.device(0))
    print(torch.cuda.device_count())
    print(torch.cuda.get_device_name(0))
    time.sleep(1)

train()
