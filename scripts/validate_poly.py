import random
from pathlib import Path
from ntru_py.ntc.ntc import ntc_from_str
from ntru_py.poly.ntc_api import poly_validate_testcase


if __name__ == '__main__':

    # Generate Small testcase subset
    root_path = Path('assets')

    if not root_path.is_dir():
        print(f"[!] root_path: {root_path} does not exist.")
        exit(1)

    for testcase in sorted(root_path.iterdir()):
        with open(testcase) as test_file:
            ntc = ntc_from_str(test_file.read())
            valid = poly_validate_testcase(ntc)
            if valid:
                print(f"[+] valid testcase. - {testcase}")
            else:
                print(f"Woops! - {testcase}")

