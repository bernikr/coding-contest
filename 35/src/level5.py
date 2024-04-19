import os
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Type


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
    VAR = auto()
    SET = auto()
    POSTPONE = auto()
    CALL = auto()




@dataclass
class Instruction:
    type: InstType
    imm: str | Type["Instruction"] = ""
    name: str = ""
    addr: int = 0
    link: InstType = InstType.END


def parse(tokens: List[str]) -> List[Instruction]:
    i = 0
    output = []
    blockstack = []

    def loadimm(s):
        t = tokens[s]
        if t == "call":
            l, val = loadimm(s+1)
            c = Instruction(InstType.CALL, imm=val)
            return l+1, c
        else:
            return 1, t

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
                l, val = loadimm(i+1)
                output.append(Instruction(InstType.IF, imm=val))
                i += l
            case 'else':
                blockstack.append(len(output))
                output.append(Instruction(InstType.ELSE))
            case 'return':
                l, val = loadimm(i+1)
                output.append(Instruction(InstType.RETURN, imm=val))
                i += l
            case 'print':
                l, val = loadimm(i+1)
                output.append(Instruction(InstType.PRINT, imm=val))
                i += l
            case 'var':
                l, val = loadimm(i+2)
                output.append(Instruction(InstType.VAR, name=tokens[i + 1], imm=val))
                i += l+1
            case 'set':
                l, val = loadimm(i+2)
                output.append(Instruction(InstType.SET, name=tokens[i + 1], imm=val))
                i += l+1
            case 'postpone':
                blockstack.append(len(output))
                output.append(Instruction(InstType.POSTPONE))
            case 'call':
                l, val = loadimm(i+1)
                output.append(Instruction(InstType.CALL, imm=val))
                i += l
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
                    ins.link = InstType.IF
                case Instruction(type=InstType.ELSE):
                    program[ins.addr].addr = i+1
                    ins.addr = i+1
                    ins.link = InstType.ELSE
                case Instruction(type=InstType.START):
                    program[ins.addr].addr = i+1
                    ins.link = InstType.START
                case Instruction(type=InstType.POSTPONE):
                    program[ins.addr].addr = i+1
                    ins.link = InstType.POSTPONE
                case _:
                    pass


class InternalError(Exception):
    pass


def run_instruction(program: List[Instruction], function_map, variables: dict = None, start=0, end=None, postpone_queues=None) \
        -> tuple[str, Optional[str]]:
    pc = start
    output = ''
    if variables is None:
        variables = {}
    if postpone_queues is None:
        postpone_queues = [[]]
    if end is None:
        end = len(program)

    def call_function(i: int):
        nonlocal output
        try:
            p, ret = run_instruction(program, function_map, variables=variables.copy(), start=function_map[int(i)][0], end=function_map[int(i)][1])
            output += p
            return ret
        except ValueError:
            raise InternalError

    def resolve(name):
        if isinstance(name, Instruction):
            return call_function(resolve(name.imm))
        else:
            return variables.get(name, name)

    while pc < end:
        match program[pc]:
            case Instruction(type=InstType.PRINT, imm=x):
                o = resolve(x)
                output += o
                pc += 1
            case Instruction(type=InstType.START):
                pc += 1
            case Instruction(type=InstType.IF, imm=b, addr=a):
                postpone_queues.append([])
                b = resolve(b)
                if b == "false":
                    pc = a
                elif b == "true":
                    pc += 1
                else:
                    raise InternalError
            case Instruction(type=InstType.ELSE, addr=a):
                pc = a
            case Instruction(type=InstType.END, link=l, addr=a):
                if l == InstType.START or l == InstType.IF or l == InstType.ELSE:
                    for nstart, nend in postpone_queues[-1]:
                        res, ret = run_instruction(program, function_map, variables, start=nstart, end=nend, postpone_queues=postpone_queues)
                        output += res
                        if ret is not None:
                            return output, ret
                if l == InstType.START:
                    return output, "true"
                if l == InstType.IF or l == InstType.ELSE:
                    postpone_queues = postpone_queues[:-1]
                pc += 1
            case Instruction(type=InstType.RETURN, imm=a):
                return output, resolve(a)
            case Instruction(type=InstType.VAR, imm=val, name=n):
                if n in variables:
                    raise InternalError
                else:
                    variables[n] = resolve(val)
                    pc += 1
            case Instruction(type=InstType.SET, imm=val, name=n):
                if n not in variables:
                    raise InternalError
                else:
                    variables[n] = resolve(val)
                    pc += 1
            case Instruction(type=InstType.POSTPONE, addr=a):
                postpone_queues[-1].append((pc+1, a))
                pc = a
            case Instruction(type=InstType.CALL, imm=n):
                call_function(resolve(n))
                pc += 1
            case other:
                assert False, other
    return output, None


def run_program(program: List[Instruction]) -> str:
    output = ''
    ip = 0
    function_map = [None]
    while ip < len(program):
        assert program[ip].type == InstType.START
        function_map.append((ip, program[ip].addr))
        ip = program[ip].addr
    ip=0
    while ip < len(program):
        assert program[ip].type == InstType.START
        try:
            res, ret = run_instruction(program, function_map, start=ip, end=program[ip].addr)
            output += res + "\n"
        except InternalError:
            output += "ERROR\n"
        except RecursionError:
            output += "ERROR\n"
        ip = program[ip].addr
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
