from __future__ import annotations

import filecmp
import re
import sys
from functools import partial
from itertools import count
from pathlib import Path
from typing import List, Iterator

from tqdm.contrib import tmap
from tqdm.contrib.concurrent import thread_map


##################################################

def split_input(inp: List[str]) -> Iterator[tuple]:
    for line in inp:
        yield (line,)  # output tuple will be input params of solve method


def solve(line) -> str:
    return str(len(line))


##################################################
WORKERS = 1
RECOMPUTE = True
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
            cmap = partial(thread_map, max_workers=WORKERS)
        else:
            cmap = tmap
        cmap = partial(cmap, miniters=1, file=sys.stdout, mininterval=0)
        results = list(cmap(partial(_solve, outfile=outfile), preprocessed_input, count()))

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
    if not example_in_file.exists():
        print("⚠️ No example file found")
    else:
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
