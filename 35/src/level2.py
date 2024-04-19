import os
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List


def is_input_file(infile: str) -> bool:
    return infile.endswith('.in')


def get_outfile(infile: str) -> str:
    return infile.split('.in')[0] + '.out'


class InstType(Enum):
    START = auto()
    END = auto()
    IF = auto()
    ELSE = auto()
    PRINT = auto()
    RETURN = auto()


@dataclass
class Instruction:
    type: InstType
    imm: str = ""
    addr: int = 0

def parse(tokens: List[str]) -> List[Instruction]:
    i = 0
    output = []
    blockstack = []
    while i < len(tokens):
        match tokens[i]:
            case 'start':
                blockstack.append(len(output))
                output.append(Instruction(InstType.START))
            case 'end':
                linked = blockstack.pop()
                output.append(Instruction(InstType.END, addr=linked))
            case 'if':
                blockstack.append(len(output))
                output.append(Instruction(InstType.IF, imm=tokens[i + 1]))
                i += 1
            case 'else':
                blockstack.append(len(output))
                output.append(Instruction(InstType.ELSE))
            case 'return':
                output.append(Instruction(InstType.RETURN, imm=tokens[i + 1]))
                i += 1
            case 'print':
                output.append(Instruction(InstType.PRINT, imm=tokens[i + 1]))
                i += 1
            case other:
                assert False, other
        i += 1
    return output


def link_blocks(program):
    for i, ins in enumerate(program):
        if ins.type == InstType.END:
            match program[ins.addr]:
                case Instruction(type=InstType.IF):
                    program[ins.addr].addr = i+2
                    ins.addr = i+1
                case Instruction(type=InstType.ELSE):
                    program[ins.addr].addr = i+1
                    ins.addr = i+1
                case _:
                    pass


def run_program(program: List[Instruction]) -> str:
    pc = 0
    output = ''
    while pc < len(program):
        match program[pc]:
            case Instruction(type=InstType.PRINT, imm=x):
                output += x
                pc += 1
            case Instruction(type=InstType.START):
                pc += 1
            case Instruction(type=InstType.IF, imm=b, addr=a):
                if b == "false":
                    pc = a
                else:
                    pc += 1
            case Instruction(type=InstType.ELSE, addr=a):
                pc = a
            case Instruction(type=InstType.END):
                pc += 1
            case Instruction(type=InstType.RETURN, imm=x):
                pc = len(program)
            case other:
                assert False, other
    return output

def run_level(infile: str, input: List[str], outfile: str) -> str:
    tokens = ' '.join((l.strip() for l in input[1:])).split(' ')
    program = parse(tokens)
    link_blocks(program)
    return run_program(program)


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
