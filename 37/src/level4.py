import os
import re
from typing import List


def winner(a, b):
    if a == b:
        return a
    if a == "P" and b == "R":
        return "P"
    if a == "R" and b == "S":
        return "R"
    if a == "S" and b == "P":
        return "S"
    return winner(b, a)


def tournament(a):
    if len(a) == 1:
        return a
    res = ""
    for i in range(0, len(a), 2):
        res += winner(a[i], a[i + 1])
    return tournament(res)


def starting_order(r, p, s):
    size = r + p + s
    hsize = size // 2

    if p == s == 0:
        return "R" * r
    if r == s == 0:
        return "P" * p
    if r == p == 0:
        return "S" * s

    if r < hsize:
        lr = r
        lp = hsize - r
        if lp > p:
            lp = p
        ls = hsize - lr - lp

    elif p >= 1:
        lr = hsize - 1
        lp = 1
        ls = 0
    elif r >= hsize:
        lr = hsize
        ls = 0
        lp = 0
    else:
        assert False

    rr = r - lr
    rp = p - lp
    rs = s - ls

    assert lr + lp + ls == rr + rp + rs == hsize
    assert lr >= 0
    assert lr >= 0
    assert ls >= 0
    assert rr >= 0
    assert rp >= 0
    assert rs >= 0
    return starting_order(lr, lp, ls) + starting_order(rr, rp, rs)


def run_part(line):
    r, p, s = map(int, re.match(r"(\d+)R (\d+)P (\d+)S", line).groups())
    o = starting_order(r, p, s)
    if tournament(o) == "S":
        return o
    else:
        assert False, "Tournament failed"


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
