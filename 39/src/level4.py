from __future__ import annotations

import filecmp
import functools
import operator
import random
import re
import sys
from collections import Counter, defaultdict
from itertools import accumulate, count
from pathlib import Path
from typing import List, Iterator

from tqdm.contrib import tmap
from tqdm.contrib.concurrent import thread_map


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


dirs = {"W": Vec(0, -1), "A": Vec(-1, 0), "S": Vec(0, 1), "D": Vec(1, 0)}


def split_input(inp: List[str]) -> Iterator[tuple]:
    i = 1
    while i < len(inp):
        width, height = Vec(*map(int, inp[i].split(" ")))
        mapp = {Vec(x, y): inp[i + 1 + y][x] for x in range(width) for y in range(height)}
        i += height + 1
        yield (mapp,)


def solve(mapp) -> str:
    mapp = defaultdict(lambda: "#", mapp)
    path = ""
    poss = [[p for p, c in mapp.items() if c == "X"][0] + dirs[random.choice("WASD")]]  # maybe?
    d = random.choice("WASD")
    for i in count():
        pos = poss[-1]
        opts = [x for x in "WASD" if mapp[pos + dirs[x]] == "." and pos + dirs[x] not in poss]

        if d in opts and not (len(path) > 3 and path[-3] == path[-2] != path[-1]) and mapp[pos + 2 * dirs[d]] == ".":
            path += d
            poss.append(pos + dirs[d])
        else:
            if opts:
                d = random.choice(opts)
                path += d
                poss.append(pos + dirs[d])
            else:
                if validate_path(mapp, path):
                    return path
                else:
                    if i < 1000 or i % 2 == 0:
                        poss = [[p for p, c in mapp.items() if c == "X"][0] + dirs[random.choice("WASD")]]
                    else:
                        poss = [random.choice([p for p, c in mapp.items() if c == "."])]
                    path = ""
    return path


def validate_path(mapp, path):
    poss = [Vec(0, 0)] + list(accumulate((dirs[l] for l in path), operator.add))
    mins = Vec(*map(min, zip(*poss)))
    poss = [p - mins for p in poss]
    return max(Counter(poss).values()) == 1 and all(c in poss for c, t in mapp.items() if t == ".") and all(
        mapp.get(p, "#") == "." for p in poss)


#####################################
WORKERS = 1
RECOMPUTE = False
CACHING = True


def _main():
    level = Path(__file__).name.split(".py")[0]
    leveldir = Path(__file__).parents[1] / "levels" / level
    partsdir = leveldir / "parts"

    def _solve(inp, index, outfile):
        if not CACHING:
            return solve(*inp)
        partfile = partsdir / (outfile.name + f".{index}")
        if partfile.exists():
            with partfile.open() as f:
                return f.read()
        else:
            res = solve(*inp)
            with partfile.open(mode="w") as f:
                f.write(res)
            return res

    def _run_file(infile, outfile):
        with open(leveldir / infile) as f:
            content = f.readlines()

        print(f"{infile.name}")
        preprocessed_input = list(split_input(content))

        if WORKERS > 1:
            cmap = functools.partial(thread_map, max_workers=WORKERS)
        else:
            cmap = tmap
        cmap = functools.partial(cmap, miniters=1, file=sys.stdout, mininterval=0)
        results = list(cmap(functools.partial(_solve, outfile=outfile), preprocessed_input, count()))

        if results and len(results) > 0:
            with open(leveldir / outfile, "w") as f:
                f.write("\n".join(results))
                f.write("\n")

    if CACHING:
        partsdir.mkdir(exist_ok=True)
        if RECOMPUTE:
            for f in partsdir.iterdir():
                f.unlink()

    for file in leveldir.iterdir():
        if re.match(r"level\d+_\d+\.out", file.name):
            file.unlink()

    example_in_file = leveldir / (level + "_example.in")
    _run_file(example_in_file, example_in_file.with_suffix(".out.computed"))
    if filecmp.cmp(example_in_file.with_suffix(".out"), example_in_file.with_suffix(".out.computed")):
        print("✅ Example check passed")
    else:
        print("⚠️ Example check failed")

    for file in leveldir.iterdir():
        if re.match(r"level\d+_\d+\.in", file.name):
            _run_file(file, file.with_suffix(".out"))


if __name__ == "__main__":
    _main()
