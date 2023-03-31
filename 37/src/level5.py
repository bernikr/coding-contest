import os
import random
import re
from typing import List

from tqdm import tqdm

wins = {"P": "RY", "R": "SL", "S": "PL", "Y": "RS", "L": "YP"}
looses = {k: ''.join(a for a, v in wins.items() if k in v) for k in wins.keys()}


def winner(a, b):
    if a == b:
        return a
    if b in wins[a]:
        return a
    return winner(b, a)


def tournament(a):
    if len(a) == 1:
        return a
    res = ""
    for i in range(0, len(a), 2):
        res += winner(a[i], a[i + 1])
    return tournament(res)


def starting_order(fighters, winner="S"):
    size = sum(fighters.values())
    hsize = size // 2

    if any(v == size for v in fighters.values()):
        k, v = next((k, v) for k, v in fighters.items() if v > 0)
        return k * v

    winner = max((v, k) for k, v in fighters.items() if k in winner)[1]

    left = {k: 0 for k in fighters.keys()}

    remaining = {k: v for k, v in fighters.items()}
    ks = list(left.keys())
    while sum(left.values()) != hsize:
        a = ks[random.randint(0, 4)]
        if remaining[a]:
            left[a] += 1
            remaining[a] -= 1

    assert sum(left.values()) == hsize
    right = {k: fighters[k] - left[k] for k in fighters.keys()}
    assert sum(right.values()) == hsize
    return starting_order(left, winner) + starting_order(right, wins[winner])


def run_part(line):
    r, p, s, y, l = map(int, re.match(r"(\d+)R (\d+)P (\d+)S (\d+)Y (\d+)L", line).groups())
    while True:
        o = starting_order({"R": r, "P": p, "S": s, "Y": y, "L": l})
        if tournament(o) == "S":
            return o


def run_level(infile: str, input: List[str], outfile: str) -> str:
    return '\n'.join(run_part(l.strip()) for l in tqdm(input[1:]))


#####################################

def is_input_file(infile: str) -> bool:
    return infile.endswith('.in')


def get_outfile(infile: str) -> str:
    return infile.split('.in')[0] + '.out'


if __name__ == '__main__':
    level = os.path.basename(__file__).split('.py')[0]
    print(os.getcwd())

    leveldir = '../levels/' + level + '/'
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
