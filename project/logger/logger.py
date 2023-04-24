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

    def __init__(self) -> None:
        self.inst = {}

    def log(self):
        inst = self.inst
        print(
            f"{inst.get('pc')} [{inst.get('inst')}] {inst.get('rd_str')} {inst.get('rs1_str')} {inst.get('rs2_str')} {inst.get('inst_abi'):>8} {inst.get('inst_fields')}"
        )

    def flush(self):
        self.inst = {}

    def set_pc(self, pc):
        self.inst["pc"] = f"PC={pc:08X}"

    def set_inst(self, inst):
        self.inst["inst"] = inst

    def set_inst_disassembly(self, inst_abi, inst_fields):
        self.inst["inst_abi"] = inst_abi
        if inst_abi in self.disassembly_pattern[0]:
            self.inst[
                "inst_fields"
            ] = f"{self.registers[inst_fields['rd']]},{self.registers[inst_fields['rs1']]},{inst_fields['rs2']}"
        elif inst_abi in self.disassembly_pattern[1]:
            self.inst[
                "inst_fields"
            ] = f"{self.registers[inst_fields['rd' if 'rd' in inst_fields else 'rs2']]},{inst_fields['imm']}({self.registers[inst_fields['rs1']]})"
        elif len(inst_fields) == 2:
            self.inst[
                "inst_fields"
            ] = f"{self.registers[inst_fields['rd']]},{inst_fields['imm']}"
        elif "rs2" in inst_fields and "imm" in inst_fields:
            self.inst[
                "inst_fields"
            ] = f"{self.registers[inst_fields['rs1']]},{self.registers[inst_fields['rs2']]},{inst_fields['imm']}"
        elif "rd" in inst_fields and "imm" in inst_fields:
            self.inst[
                "inst_fields"
            ] = f"{self.registers[inst_fields['rd']]},{self.registers[inst_fields['rs1']]},{inst_fields['imm']}"
        else:
            self.inst[
                "inst_fields"
            ] = f"{self.registers[inst_fields['rd']]},{self.registers[inst_fields['rs1']]},{self.registers[inst_fields['rs2']]}"

    def set_reg(self, reg_cat, reg_id, reg_value):
        self.inst[reg_cat] = reg_id
        self.inst[f"{reg_cat}_str"] = f"x{reg_id:02d}={int_to_hex(reg_value)}"
