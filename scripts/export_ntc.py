from ntru_py.ntc.ntc import *
from ntru_py.sage import sage_generate_testcase
from pathlib import Path
import random

if __name__ == '__main__':

    # Generate Small testcase subset
    N_TESTS = 10
    random.seed(42)
    root_path = Path('assets')

    if not root_path.is_dir():
        print(f"[!] root_path: {root_path} does not exist.")
        exit(1)

    for test_type in NTRU_PARAM_TYPES:

        for i in range(N_TESTS):
            test_path = root_path / f"ntc_{test_type}_{i:02}.json" 
            ntc = sage_generate_testcase(test_type)

            with open(test_path, 'w') as test_file:
                test_file.write(ntc_to_str(ntc))



