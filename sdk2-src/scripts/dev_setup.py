import argparse
import os
import shutil
import sys
from argparse import Namespace, RawTextHelpFormatter
from pathlib import Path
from platform import system
from typing import Any, Callable
from urllib.request import urlopen

from utils import Color, print_red, run_command


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
            f"Connection error while trying to download file from {from_url}. Please try running the script again."
        )
    with open(f"{to_path}/{with_file_name}", "w") as f:
        f.write(response.read().decode("utf-8"))


def setup_sdk(args: Namespace, command_args: dict) -> None:
    autorest_path = Path("./autorest")
    python_sdk_path = Path("./python-sdk")
    restclient_path = Path("./src/azure-ml/azure/ml/_restclient/")

    print_red("- Downloading the latest MFE swagger from Azure blob storage")
    download_file(
        from_url="https://mfeswaggers.blob.core.windows.net/latest/mfe.json",
        to_path=autorest_path,
        with_file_name="mfe.json",
    )

    print_red("- Downloading the latest machineLearningServices.json swagger from Azure blob storage")
    download_file(
        from_url="https://mfeswaggers.blob.core.windows.net/mlservices/machineLearningServices.json",
        to_path=autorest_path,
        with_file_name="machineLearningServices.json",
    )

    print_red(f"- Cleaning up {python_sdk_path} folder")
    remove_dir(python_sdk_path)

    print_red(f"- Generating autorest Python code under {autorest_path} folder to {python_sdk_path}")
    run_command(
        [
            "autorest",
            "--python",
            "--track2",
            "--use=@autorest/python@5.4.0",
            f"--python-sdks-folder={python_sdk_path.absolute()}",
            "--python-mode=create",
            "--package-version=0.1.0",
            str(Path("./autorest/readme.md").absolute()),
            "--modelerfour.lenient-model-deduplication",
            "--title=Azure Machine Learning Workspaces",
        ],
        throw_on_retcode=True,
        **command_args,
    )

    print_red(f"- Cleaning up {restclient_path} folder")
    remove_dir(restclient_path)

    print_red(f"- Copying over auto generated python code to {restclient_path} folder")
    copy_files(
        from_dir=python_sdk_path / "machinelearning/azure-mgmt-machinelearningservices/azure/mgmt/",
        to_dir=restclient_path,
    )

    if not args.no_install:
        print_red("- Installing Python SDK from local directory")
        run_command(commands=["pip", "install", "-e", str(Path("./src/azure-ml/").absolute())], **command_args)


def setup_cli(args: Namespace, command_args: dict) -> None:
    extension_path = Path("azure-cli-extensions")

    print_red("- Installing azure-cli")
    run_command(["pip", "install", "azure-cli"], **command_args)

    print_red("- Cloning azure-cli-extensions into repository")
    remove_dir(extension_path)
    run_command(["git", "clone", "https://github.com/Azure/azure-cli-extensions", "--depth", "1"], **command_args)
    cli_folder = Path("./src/cli")

    print_red("- Building cli extensions")

    extra = ["--debug"] if args.debug else []
    run_command(
        [
            "autorest",
            "--az",
            "--use=@autorest/az@latest",
            "--version=3.0.6271",
            "--clear-output-folder=true",
            f"--azure-cli-extension-folder={cli_folder.absolute()}",
            str(Path("./autorest/readme.md").absolute()),
            "--title=Azure Machine Learning Workspaces",
            "--modelerfour.lenient-model-deduplication",
        ]
        + extra,
        **command_args,
    )
    cli_src = cli_folder / "src"

    if not args.no_install:
        print_red("- Installing cli extension from source code")
        run_command(["pip", "install", "-e", f'{(cli_src / "machinelearningservices").absolute()}'], **command_args)
        print_red("---------------------------- TO DO For YOU!! -----------------------------------")
        print(f"Please set the environment variable AZURE_EXTENSION_DIR to {cli_src.absolute()}")
        print(f'In Powershell, you can set in this way: $Env:AZURE_EXTENSION_DIR="{cli_src.absolute()}"')
        print(f"In bash, you can set in this way: export AZURE_EXTENSION_DIR={cli_src.absolute()}")


if __name__ == "__main__":
    welcome_message = f"""
This script builds the Python SDK and CLI for a development environment. You need to run it from the root sdk-cli-v2 directory
Example: {Color.BLUE} python ./scripts/dev_setup.py -scu {Color.END}
Prerequisites:
    1. Ensure you have npm installed on your machine. You can find the node install here: https://nodejs.org/en/download/
    2. Install autorest with the command "npm install -g autorest"
    3. You cannot setup the CLI unless you have set up the SDK. If you already set up the SDK, then you can run -cli flag alone.
    """
    epilog = f"""
Sample Usages:
setup sdk, cli and run unittests:                           {Color.BLUE} python scripts/dev_setup -scu {Color.END}
setup sdk, cli without install locally and build the wheel: {Color.BLUE} python scripts/dev_setup -scunw {Color.END}
run e2e tests:                                              {Color.BLUE} python scripts/dev_setup -e {Color.END}
run unittests:                                              {Color.BLUE} python sciprts/dev_setup -u {Color.END}
setup sdk, cli with debug and verbose mode:                 {Color.BLUE} python scripts/dev_setup -scdv {Color.END}
    """
    parser = argparse.ArgumentParser(
        description=Color.RED + "Welcome to sdk-cli-v2 dev setup!" + Color.END + "\n" + welcome_message,
        epilog=epilog,
        formatter_class=RawTextHelpFormatter,
    )

    parser.add_argument("-c", "--cli", action="store_true", required=False, help="the flag to setup CLI.")
    parser.add_argument("-s", "--sdk", action="store_true", required=False, help="the flag to setup SDK.")
    parser.add_argument("-u", "--unittest", action="store_true", required=False, help="running the unit tests")
    parser.add_argument(
        "-d", "--debug", action="store_true", required=False, help="the flag to turn on debug mode for cli"
    )
    parser.add_argument("-v", "--verbose", action="store_true", required=False, help="turn on verbose output")
    parser.add_argument(
        "-n",
        "--no-install",
        action="store_true",
        required=False,
        help="if set, sdk and cli will not run `pip install -e package`",
    )
    parser.add_argument("-e", "--e2etest", action="store_true", required=False, help="run the e2e tests")
    parser.add_argument(
        "-w", "--wheel", action="store_true", required=False, help="build the wheel for package azure-ml."
    )
    parser.add_argument("--clean", action="store_true", help="clean up the directory")
    args = parser.parse_args()

    command_args = {"shell": system() == "Windows", "stream_stdout": args.verbose}
    if args.sdk:
        print_red("- Setting up the SDK ")
        setup_sdk(args, command_args)
        print_red("- Install dev dependencies")
        run_command(commands=["pip", "install", "-r", str(Path("requirements-dev.txt").absolute())], **command_args)
        print_red("- Install test dependencies")
        run_command(
            commands=["pip", "install", "-r", str(Path("./tests/test-requirements.txt").absolute())], **command_args
        )
        if system() == "Windows":
            run_command(commands=["pip", "install", "pywin32==227"], **command_args)
            run_command(commands=["pip", "install", "portalocker==1.6.0"], **command_args)
    if args.cli:
        print_red("- Setting up the CLI ")
        setup_cli(args, command_args)
    if args.unittest:
        print_red("- Runnung unit tests for the SDK ")
        run_command(commands=["pytest", str(Path("tests/azure-ml/unittests").absolute())], shell=command_args["shell"])
    if args.e2etest:
        print_red("- Running end-to-end tests for the SDK ")
        # default 10 workers - TODO: change this to take an argument
        run_command(
            commands=["pytest", str(Path("tests").absolute()), "-m", "e2etest", "-n", "10"], shell=command_args["shell"]
        )
    if args.wheel:
        print_red("- Build wheels for the SDK and CLi")
        run_command(commands=["pip", "install", "--upgrade", "setuptools", "wheel", "cython"], **command_args)
        run_command(
            commands=["python", "scripts/build_wheel.py", "-s", "./src/azure-ml", "-v", "./src/azure-ml/azure/ml"],
            **command_args,
        )
        run_command(
            commands=[
                "python",
                "scripts/build_wheel.py",
                "-s",
                "./src/cli/src/machinelearningservices",
                "-v",
                "./src/cli/src/machinelearningservices/azext_ml/manual",
            ],
            **command_args,
        )
    if args.clean:
        print_red("- Clean up the project")
        azure_ml_path = Path("./src/azure-ml")
        cli_path = Path("./src/cli/src/machinelearningservices")
        python_sdk_path = Path("./python-sdk")
        extension_path = Path("azure-cli-extensions")
        remove_dir(azure_ml_path / "build")
        remove_dir(azure_ml_path / "dist")
        remove_dir(cli_path / "build")
        remove_dir(cli_path / "dist")
        remove_dir(python_sdk_path)
        remove_dir(extension_path)
    print_red("Hooray, you are all set!")
