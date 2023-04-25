from glob import glob
from tqdm import tqdm

import numpy as np


def bin_to_int(content):
    return np.int32(int(content, 2))


def hex_to_bin(content):
    return format(int(content, 16), "0>32b")


def decode_line(line):
    pc = line[12:20]
    inst = line[24:32]
    bin_inst = hex_to_bin(inst)

    reg_ids = {
        "rs1": bin_to_int(bin_inst[12:17]),
        "rs2": bin_to_int(bin_inst[7:12]),
        "rd": bin_to_int(bin_inst[20:25]),
    }
    return pc.upper(), inst.upper(), reg_ids


def get_regs(file):
    regs = []
    for _ in range(8):
        line_regs = [
            item for item in file.readline().strip().split(" ") if len(item) == 10
        ]
        for reg_value in line_regs:
            regs.append(reg_value[2:].upper())
    return regs


if __name__ == "__main__":
    reg_files = sorted(glob("spike/outputs/*.r"))
    inst_files = sorted(glob("spike/outputs/*.i"))
    with open("sp.txt", "w") as sp:
        for reg, inst in tqdm(zip(reg_files, inst_files)):
            log_file = f"{reg[:-2]}.log"
            with open(inst, "r") as i, open(reg, "r") as r, open(log_file, "w") as log:
                prev_regs = get_regs(r)
                sp.write(f"{int(prev_regs[2], 16)}\n")
                i.readline()
                for line in i:
                    pc, inst_hex, reg_ids = decode_line(line)
                    cur_regs = get_regs(r)
                    log.write(
                        f"PC={pc} [{inst_hex}] x{reg_ids['rd']:02d}={cur_regs[reg_ids['rd']]} x{reg_ids['rs1']:02d}={prev_regs[reg_ids['rs1']]} x{reg_ids['rs2']:02d}={prev_regs[reg_ids['rs2']]}\n"
                    )
                    prev_regs = cur_regs
