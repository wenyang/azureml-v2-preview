import os
import json
import glob
from utils import run_command

MLN = 10000


def run_flake8(testpath, flake_rules):
    cmd = [
        'flake8',
        '--ignore={0}'.format(",".join(flake_rules.get('ignore', []))),
        '--exclude={0}'.format(",".join(flake_rules.get('exclude', []))),
        '--max-line-length={0}'.format(flake_rules.get('max-line-length', MLN)),
        testpath]

    return run_command(cmd, throw_on_retcode=False, stream_stdout=False)


def load_rules(testpath):
    flake_rules_file = os.path.join(testpath, "flake_rules.json")
    flake_rules = {}
    if os.path.isfile(flake_rules_file):
        with open(flake_rules_file) as f:
            flake_rules = json.loads(f.read()).get("pep8", {})
    resolved = []
    for a in flake_rules.get('exclude', []):
        if a.endswith('/'):
            resolved.append(a.rstrip('/'))
        else:
            resolved.append(os.path.realpath(os.path.join(testpath, a.strip())))

    flake_rules['exclude'] = resolved

    return flake_rules


def combine_rules(rule_a, rule_b):
    rule = {}
    rule['ignore'] = rule_a.get('ignore', []) + rule_b.get('ignore', [])
    rule['exclude'] = rule_a.get('exclude', []) + rule_b.get('exclude', [])
    rule['max-line-length'] = min(rule_a.get('max-line-length', MLN), rule_b.get('max-line-length', MLN))

    return rule


def inherit_flake_rules(rootpath, testpath):
    flake_rules = {}
    upperpath = testpath
    while (upperpath != rootpath):
        upperpath = os.path.dirname(upperpath)
        flake_rules = combine_rules(flake_rules, load_rules(upperpath))
    return flake_rules


def test(rootpath, testpath):
    test_path_flake_rules = inherit_flake_rules(rootpath, testpath)

    custom = [os.path.dirname(a) for a in glob.glob(testpath + "/**/flake_rules.json", recursive=True)]

    if testpath not in custom:
        custom.append(testpath)

    output = []

    for path in custom:
        flake_rules = {}
        flake_rules["exclude"] = [os.path.dirname(a) for a in glob.glob(path + "/**/flake_rules.json",
                                                                        recursive=True) if os.path.dirname(a) != path]
        inherited_rules = inherit_flake_rules(testpath, path)
        flake_rules = combine_rules(combine_rules(flake_rules, test_path_flake_rules),
                                    combine_rules(inherited_rules, load_rules(path)))
        output.extend([x for x in run_flake8(path, flake_rules).split('\n') if len(x) > 0])

    if len(output) > 0:
        print('#' * 79)
        for line in output:
            print(line)
        print('#' * 79)
        raise Exception('Code is unhealthy. See tests/framework/readme.md for more information')


def main(testpath=None):
    rootpath = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", ".."))
    test(rootpath, testpath)


if __name__ == '__main__':
    print("*******[TEST]: START*******")
    import argparse

    parser = argparse.ArgumentParser(description='Run AzureML SDK tests')
    parser.add_argument('--testpath')

    args = parser.parse_args()
    print(args)
    main(os.path.realpath(args.testpath))

    print("*******[TEST]: COMPLETE*******")
