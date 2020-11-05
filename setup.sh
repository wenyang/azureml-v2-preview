conda create -n cli_v2 python=3.6
conda activate cli_v2
pip install azure-cli
pip install --extra-index-url https://azuremlsdktestpypi.azureedge.net/sdk-cli-v2 azure-ml==0.0.1
wget https://paulshaml18829289173.blob.core.windows.net/wheels/ml-0.1.0-py3-none-any.whl
az extension remove -n azure-cli-ml
az extension add --source ml-0.1.0-py3-none-any.whl -y
