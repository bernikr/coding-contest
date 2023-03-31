import os
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
    res = ""
    for i in range(0, len(a), 2):
        res += winner(a[i], a[i + 1])
    return res


def run_level(infile: str, input: List[str], outfile: str) -> str:
    return '\n'.join(tournament(tournament(l.strip())) for l in input[1:])


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
