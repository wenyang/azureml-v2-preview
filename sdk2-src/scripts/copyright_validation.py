import os
import glob


def main(testpath):

    badfiles = []

    ignore = set(["build", "stresstest", "test", "tests", "vendor", "_vendor",
                  "azext_ml", "oldworld", "restclient", "restclients", "_restclients",
                  "external", "_external", "_limit_function_call.py", "e2e_tests", "setup.py"])

    ignore.add("_restclient")
    
    copyright = [
        "# ---------------------------------------------------------\n",
        "# Copyright (c) Microsoft Corporation. All rights reserved.\n",
        "# ---------------------------------------------------------\n"
    ]

    for file in glob.glob(testpath + "/**/*.py", recursive=True):
        bad = False
        file = os.path.normpath(file)
        if len(set.intersection(ignore, set(file.split('\\')))) > 0:
            continue
        # print(file)
        filelines = []
        with open(file, encoding="utf8") as f:
            filelines = f.readlines()

        if len(filelines) >= len(copyright):
            for i in range(0, len(copyright)):
                if filelines[i].rstrip() != copyright[i].rstrip():
                    bad = True
                    break
        else:
            bad = True

        if bad:
            badfiles.append(file)

    if len(badfiles) > 0:
        print('#' * 79)
        for line in badfiles:
            print(line)
        print('#' * 79)
        print('e-mail yuc if any issues')
        raise Exception(
            "Missing copyright headers. If you think that's a mistake check scripts/copyright_validation.py")


if __name__ == '__main__':
    print("*******[TEST]: START*******")
    import argparse

    parser = argparse.ArgumentParser(description='Run AzureML SDK tests')
    parser.add_argument('--testpath')

    args = parser.parse_args()
    print(args)
    if not args.testpath:
        args.testpath = "./src"
    main(os.path.realpath(args.testpath))

    print("*******[TEST]: COMPLETE*******")
