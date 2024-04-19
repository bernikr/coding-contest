import os
from typing import List

def is_input_file(infile: str) -> bool:
    return infile.endswith('.in')

def get_outfile(infile: str) -> str:
    return infile.split('.in')[0] + '.out'

def run_level(infile: str, input: List[str], outfile: str) -> str:
    return str(len(input))

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
