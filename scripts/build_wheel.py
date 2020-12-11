import argparse
from pathlib import Path
from utils import run_command, Color, print_red

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=Color.BLUE + "Wheel builder for v2" + Color.END + "\n")

    parser.add_argument("-v", required=True, help="directory that contains version.py")
    parser.add_argument("-s", required=True, help="directory that contains setup.py")
    args = parser.parse_args()

    version_path = Path(args.v)
    version_file = version_path / "version.py"
    package_path = Path(args.s)
    setup_file = package_path / "setup.py"
    if not setup_file.is_file():
        raise FileNotFoundError(
            "cannot find the setup.py. Make sure you in the root directory and setup sdk and cli properly"
        )
    if not version_file.is_file():
        raise FileNotFoundError(
            "cannot find the version.py. Make sure you in the root directory and setup sdk and cli properly"
        )

    print_red("Build the wheel")
    run_command(commands=["python", "setup.py", "bdist_wheel"], cwd=str(package_path.absolute()))

    print_red("Bump up version")
    run_command(commands=["pip", "install", "bump2version>=1.0.1"])
    run_command(commands=["python", "-m", "bumpversion", "patch", "version.py"], cwd=str(version_path.absolute()))
