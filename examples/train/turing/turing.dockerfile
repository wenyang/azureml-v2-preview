FROM mcr.microsoft.com/azureml/openmpi3.1.2-cuda10.2-cudnn8-ubuntu18.04
# Install Common Dependencies
RUN  pip install ninja torch torchvision transformers==2.10.0 tensorboardX
# Install Apex for fp16
RUN pip install -v --install-option="--cpp_ext" --install-option="--cuda_ext" 'git+https://github.com/NVIDIA/apex.git'