pip install --extra-index-url https://azuremlsdktestpypi.azureedge.net/sdk-cli-v2 azure-ml==0.0.1
wget https://mldevplatv2.blob.core.windows.net/cli/cli.zip
mkdir ~/azmlcli; tar xvf cli.zip -C ~/azmlcli
export AZURE_EXTENSION_DIR=~/azmlcli

az ml -h
