import argparse
from pathlib import Path
from utils import run_command, Color, print_red

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=Color.RED + 'Static Type Checker for SDK v2' + Color.END + '\n')

    parser.add_argument('-s', required=True, help='The source directory to type check.')
    parser.add_argument('-r', required=False, help='The file path for report. Default is "."')
    args = parser.parse_args()

    src_path = Path(args.s)
    report_path = Path(args.r) if args.r else Path(".")

    print_red("Installing dependencies")
    # pip install mypy==0.782 lxml
    run_command(['pip', 'install', 'mypy==0.782', 'lxml'])

    print_red('Running mypy')
    # mypy src\azure-ml --cobertura-xml-report $(System.DefaultWorkingDirectory)
    run_command(['mypy', str(src_path.absolute()), "--cobertura-xml-report", str(report_path.absolute())])
