from utils.convert import int_to_hex


class Logger:
    registers = [
        "zero",
        "ra",
        "sp",
        "gp",
        "tp",
        "t0",
        "t1",
        "t2",
        "s0",
        "s1",
        "a0",
        "a1",
        "a2",
        "a3",
        "a4",
        "a5",
        "a6",
        "a7",
        "s2",
        "s3",
        "s4",
        "s5",
        "s6",
        "s7",
        "s8",
        "s9",
        "s10",
        "s11",
        "t3",
        "t4",
        "t5",
        "t6",
    ]

    disassembly_pattern = [
        ["SLLI", "SRLI", "SRAI"],
        ["LW", "LH", "LB", "LHU", "LBU", "SW", "SH", "SB", "JALR"],
    ]

    def __init__(self, disassembly):
        self.inst = {}
        self.disassembly = disassembly

    def log(self):
        inst = self.inst
        if self.disassembly:
            print(
                f"{inst.get('pc')} [{inst.get('inst')}] {inst.get('rd_str')} {inst.get('rs1_str')} {inst.get('rs2_str')} {inst.get('disassembly')}"
            )
        else:
            print(
                f"{inst.get('pc')} [{inst.get('inst')}] {inst.get('rd_str')} {inst.get('rs1_str')} {inst.get('rs2_str')}"
            )
        self.flush()

    def flush(self):
        self.inst = {}

    def set_pc(self, pc):
        self.inst["pc"] = f"PC={pc:08X}"

    def set_inst(self, inst):
        self.inst["inst"] = inst

    def set_inst_disassembly(self, disassembly):
            self.inst["disassembly"] = disassembly

    def set_reg(self, reg_cat, reg_id, reg_value):
        self.inst[reg_cat] = reg_id
        self.inst[f"{reg_cat}_str"] = f"x{reg_id:02d}={int_to_hex(reg_value)}"
