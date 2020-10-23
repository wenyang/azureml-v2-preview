from argparse import Namespace
from ast import parse
import os
from os import environ, remove
import shutil
import argparse
from typing import Any, Callable
from urllib.request import urlopen
import sys
from utils import run_command, Color, print_red
from pathlib import Path
from platform import system


def path_exists(dir: Path) -> bool:
    return dir.exists()


def remove_dir(dir: Path) -> None:
    def onerror(func: Callable[..., Any], path: Path, exe_info: Any) -> None:
        import stat
        if not os.access(path, os.W_OK):
            # Is the error an access error ?
            os.chmod(path, stat.S_IWUSR)
            func(path)
        else:
            raise Exception(f"other errors happened when removing path: {dir}")

    if path_exists(dir):
        shutil.rmtree(dir, onerror=onerror)
    else:
        print_red(f"{dir} does not exists. Skip removing it")


def create_dir(dir: Path) -> None:
    if path_exists(dir) is False:
        dir.mkdir()
    else:
        print_red("f{path} already exists. Skip creating it.")


def copy_files(from_dir: Path, to_dir: Path) -> None:
    if path_exists(from_dir) and path_exists(to_dir):
        file_names = os.listdir(from_dir)
        for file_name in file_names:
            srcname = os.path.join(from_dir, file_name)
            dstname = os.path.join(to_dir, file_name)
            shutil.copy2(srcname, dstname)
    elif path_exists(from_dir):
        shutil.copytree(from_dir, to_dir)
    else:
        print_red(f"from_dir: {from_dir} does not exists. Skip copying files.")


def download_file(from_url: str, to_path: Path, with_file_name: str) -> None:
    try:
        response = urlopen(from_url)
    except Exception:
        sys.exit(
            f"Connection error while trying to download file from {from_url}. Please try running the script again.")
    with open(f"{to_path}/{with_file_name}", 'w') as f:
        f.write(response.read().decode('utf-8'))


def setup_sdk(args: Namespace, shell: bool) -> None:
    autorest_path = Path("./autorest")
    python_sdk_path = Path("./python-sdk")
    restclient_path = Path("./src/azure-ml/azure/ml/_restclient/")

    print_red("- Downloading the latest MFE swagger from Azure blob storage")
    download_file(from_url="https://mfeswaggers.blob.core.windows.net/latest/mfe.json",
                  to_path=autorest_path,
                  with_file_name='mfe.json')

    print_red("- Downloading the latest machineLearningServices.json swagger from Azure blob storage")
    download_file(from_url="https://mfeswaggers.blob.core.windows.net/mlservices/machineLearningServices.json",
                  to_path=autorest_path,
                  with_file_name='machineLearningServices.json')

    print_red(f"- Cleaning up {python_sdk_path} folder")
    remove_dir(python_sdk_path)

    print_red(f"- Generating autorest Python code under {autorest_path} folder to {python_sdk_path}")
    run_command([
        'autorest', '--python', '--track2', '--use=@autorest/python@5.4.0',
        f'--python-sdks-folder={python_sdk_path.absolute()}', '--python-mode=create', '--package-version=0.1.0',
        f'{Path("./autorest/readme.md").absolute()}', '--modelerfour.lenient-model-deduplication',
        '--title=Azure Machine Learning Workspaces'
    ],
                throw_on_retcode=True,
                shell=shell)

    print_red(f"- Cleaning up {restclient_path} folder")
    remove_dir(restclient_path)

    print_red(f"- Copying over auto generated python code to {restclient_path} folder")
    copy_files(from_dir=python_sdk_path / "machinelearning/azure-mgmt-machinelearningservices/azure/mgmt/",
               to_dir=restclient_path)

    print_red("- Installing Python SDK from local directory")
    run_command(commands=['pip', 'install', '-e', f'{Path("./src/azure-ml/").absolute()}'], shell=shell)


def setup_cli(shell: bool, debug: bool) -> None:
    extension_path = Path('azure-cli-extensions')

    print_red("- Installing azure-cli")
    run_command(['pip', 'install', 'azure-cli'], shell=shell)

    print_red("- Cloning azure-cli-extensions into repository")
    remove_dir(extension_path)
    run_command(['git', 'clone', 'https://github.com/Azure/azure-cli-extensions', '--depth', '1'], shell=shell)
    cli_folder = Path('./src/cli')

    print_red("- Building cli extensions")
    extra = []
    if debug:
        extra.append("--debug")
    run_command([
        "autorest", "--az", "--use=@autorest/az@latest", "--version=3.0.6271", "--clear-output-folder=true",
        f"--azure-cli-extension-folder={cli_folder.absolute()}", f"{Path('./autorest/readme.md').absolute()}",
        "--title=Azure Machine Learning Workspaces", "--modelerfour.lenient-model-deduplication"
    ] + extra,
                shell=shell)
    cli_src = cli_folder / "src"

    print_red("- Installing cli extension from source code")
    run_command(['pip', 'install', '-e', f'{(cli_src / "machinelearningservices").absolute()}'], shell=shell)
    print_red("---------------------------- TO DO For YOU!! -----------------------------------")
    print_red(f"Please set the environment variable AZURE_EXTENSION_DIR to {cli_src.absolute()}")
    print(f'In Powershell, you can set in this way: $Env:AZURE_EXTENSION_DIR="{cli_src.absolute()}"')
    print(f"In bash, you can set in this way: export AZURE_EXTENSION_DIR={cli_src.absolute()}")


if __name__ == "__main__":
    welcome_message = """
    This script builds the Python SDK and CLI for a development environment. You need to run it from the root sdk-cli-v2 directory
    Example: python ./scripts/dev_setup.py ~/code/vienna/src/azureml-api/src/ManagementFrontEnd -sdk -cli
    Prerequisites: 
        1. Ensure you have node installed on your machine. You can find the node install here: https://nodejs.org/en/download/
        2. Install autorest with the command "npm install -g autorest"
        3. You cannot setup the CLI unless you have set up the SDK. If you already set up the SDK, then you can run -cli flag alone. 
    """
    parser = argparse.ArgumentParser(description=Color.RED + 'Welcome to sdk-cli-v2 dev setup!' + Color.END + '\n' +
                                     welcome_message)

    parser.add_argument('-cli', action='store_true', required=False, help='the flag to setup CLI.')
    parser.add_argument('-sdk', action='store_true', required=False, help='the flag to setup SDK.')
    parser.add_argument('-t', action='store_true', required=False, help='running the unit tests after SDK setup')
    parser.add_argument('-debug', action='store_true', required=False, help='the flag to turn on debug mode for cli')
    args = parser.parse_args()

    shell = system() == "Windows"
    if not args.sdk and not args.cli:
        print_red("please enter either sdk or cli flag")
        exit()

    if args.sdk:
        print_red("- Setting up the SDK ")
        setup_sdk(args, shell)
        print_red("- Install test dependnecies")
        run_command(commands=['pip', 'install', '-r', f'{Path("./tests/test-requirements.txt").absolute()}'],
                    shell=shell)
        if system() == "Windows":
            run_command(commands=['pip', 'install', 'pywin32==227'], shell=shell)
            run_command(commands=['pip', 'install', 'portalocker==1.6.0'], shell=shell)
    if args.cli:
        print_red("- Setting up the CLI ")
        setup_cli(shell, args.debug)
    if args.t:
        print_red("- Runnung unit tests for the SDK ")
        run_command(commands=['pytest', f'{Path("tests/azure-ml/unittests").absolute()}'], shell=shell)

    print_red("Hooray, you are all set!")
