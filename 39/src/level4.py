from __future__ import annotations

from collections import Counter, defaultdict
from functools import reduce
from itertools import accumulate, count
import math
from multiprocessing import Pool
import operator
import os
import random
from typing import List

from tqdm import tqdm

class Vec(tuple[int, ...]):
    def __new__(cls, *args: int | float) -> Vec:
        return super().__new__(cls, args)

    def __add__(self, other):
        return Vec(*map(operator.add, self, other))

    def __sub__(self, other):
        return Vec(*map(operator.sub, self, other))

    def __mul__(self, other):
        if isinstance(other, int | float):
            return Vec(*map(lambda x: x * other, self))
        else:
            raise NotImplemented

    def __truediv__(self, other):
        if isinstance(other, int | float):
            return Vec(*map(lambda x: x // other if x % other == 0 else x / other, self))
        else:
            raise NotImplemented

    def manhatten(self):
        return sum(abs(x) for x in self)

class Box:
    def __init__(self, *corners):
        corners = [tuple(c) for c in corners]
        self.lower = Vec(*map(min, zip(*corners)))
        self.upper = Vec(*map(max, zip(*corners)))

dirs = {"W": Vec(0,-1), "A": Vec(-1,0),  "S": Vec(0,1), "D": Vec(1,0)}


def run_level(infile: str, input: List[str], outfile: str) -> str:
    i = 1
    res = ""
    with tqdm(total=len(input), initial=1) as pbar:
        while i < len(input):
            width, height = Vec(*map(int, input[i].split(' ')))
            mapp = {Vec(x,y): input[i+1+y][x] for x in range(width) for y in range(height)}
            i += height + 1
            res += f"{run_yard(mapp)}\n"
            pbar.update(height + 1)
        return res[:-1]

def run_yard_mp(mapp):
    with Pool(processes=16) as pool:
        multiple_results = [pool.apply_async(run_yard, mapp) for i in range(16)]
        print([res.get(timeout=1) for res in multiple_results])


def run_yard(mapp):
    mapp = defaultdict(lambda: '#', mapp)
    path = ""
    poss = [[p for p, c in mapp.items() if c=="X"][0]+dirs[random.choice("WASD")]] #maybe?
    d = random.choice("WASD")
    for i in count():
        pos = poss[-1]
        opts = [x for x in "WASD" if mapp[pos+dirs[x]] == "." and pos+dirs[x] not in poss]

        if d in opts and not (len(path)>3 and path[-3] == path[-2] !=path[-1]) and mapp[pos+2*dirs[d]]==".":
            path += d
            poss.append(pos+dirs[d])
        else:
            if opts:
                d = random.choice(opts)
                path += d
                poss.append(pos+dirs[d])
            else:
                if validate_path(mapp, path):
                    return path
                else:
                    if i < 1000 or i % 2 == 0:
                        poss = [[p for p, c in mapp.items() if c=="X"][0]+dirs[random.choice("WASD")]]
                    else:
                        poss = [random.choice([p for p, c in mapp.items() if c == "."])]
                    path = ""



    return path

def validate_path(mapp, path):
    poss = [Vec(0,0)] + list(accumulate((dirs[l] for l in path), operator.add))
    mins = Vec(*map(min, zip(*poss)))
    poss = [p-mins for p in poss]
    return max(Counter(poss).values()) == 1 and all(c in poss for c, t in mapp.items() if t == '.') and all(mapp.get(p, '#') == '.' for p in poss)


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
