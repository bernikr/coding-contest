import os
from typing import List


def is_input_file(infile: str) -> bool:
    return infile.endswith('.in')


def get_outfile(infile: str) -> str:
    return infile.split('.in')[0] + '.out'


def run_level(infile: str, input: List[str], outfile: str) -> str:
    tokens = ' '.join((l.strip() for l in input[1:])).split(' ')
    pc = 0
    output = ""
    while pc < len(tokens):
        match tokens[pc]:
            case 'print':
                output += tokens[pc+1]
                pc += 2
            case _:
                pc += 1
    return output


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
