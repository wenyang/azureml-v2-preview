import argparse
from utils import run_command, Color, print_red
from pathlib import Path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=Color.RED + "Test Coverage for SDK v2!" + Color.END + "\n")

    parser.add_argument("-p", required=True, help="The package to test (example: azure.ml)")
    parser.add_argument("-t", required=True, help="The path to the tests. (example: tests/azure-ml/unittests")
    args = parser.parse_args()

    # pytest --junitxml=junit1.xml --cov=azure.ml --cov-report=html --cov-report=xml -ra ./tests/*/unittests/
    run_command(
        [
            "pytest",
            "--junitxml=junit1.xml",
            f"--cov={args.p}",
            "--cov-report=html",
            "--cov-report=xml",
            "-ra",
            f"{Path(args.t).absolute()}",
            "-n",
            "10",
        ]
    )
