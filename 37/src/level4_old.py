import math
import os
import re
from typing import List

import numpy as np
from cpmpy import *
from cpmpy.solvers import CPM_ortools


def run_part(line):
    r, p, s = map(int, re.match(r"(\d+)R (\d+)P (\d+)S", line).groups())
    size = r + p + s
    lsize = int(math.log2(size)) + 1

    rulesa = np.array([
        0, 1, 0,
        1, 1, 2,
        0, 2, 2
    ])

    m = Model()

    tournament = intvar(0, 2, shape=(lsize, size))
    rules = intvar(0, 2, shape=9)

    m += rules == rulesa

    m += sum(tournament[0] == 0) == r
    m += sum(tournament[0] == 1) == p
    m += sum(tournament[0] == 2) == s

    m += tournament[lsize - 1, 0] == 2

    for i in range(1, lsize):
        for j in range(pow(2, lsize - 1 - i)):
            m += tournament[i, j] == rules[tournament[i - 1, j * 2] * 3 + tournament[i - 1, j * 2 + 1]]

    s = CPM_ortools(m)
    if not s.solve(num_search_workers=8, log_search_progress=False):
        assert False
    t = tournament.value()
    res = ""
    for c in list(t[0]):
        res += "RPS"[c]
    return res


def run_level(infile: str, input: List[str], outfile: str) -> str:
    return '\n'.join(run_part(l.strip()) for l in input[1:])


#####################################

def is_input_file(infile: str) -> bool:
    return infile.endswith('.in')


def get_outfile(infile: str) -> str:
    return infile.split('.in')[0] + '.out'


if __name__ == '__main__':
    level = os.path.basename(__file__).split('.py')[0]
    print(os.getcwd())

    leveldir = os.path.join(os.path.dirname(__file__), '../levels/' + level + '/')
    for file in os.listdir(leveldir):
        infile = leveldir + file

        if not is_input_file(infile):
            continue

        with open(infile) as f:
            content = f.readlines()

        outfile = get_outfile(infile)
        result = run_level(infile, content, outfile)

        if result and len(result) > 0:
            with open(outfile, 'w') as f:
                f.write(result)
                f.write('\n')
