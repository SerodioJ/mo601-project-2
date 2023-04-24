from utils.convert import bin_to_int


class Decoder:
    op_codes = {
        # I - Base Instruction Set
        "0110111": ("LUI", "U"),
        "0010111": ("AUIPC", "U"),
        "1101111": ("JAL", "J"),
        "1100111": ("JALR", "I"),
        "1100011": {
            "000": ("BEQ", "B"),
            "001": ("BNE", "B"),
            "100": ("BLT", "B"),
            "101": ("BGE", "B"),
            "110": ("BLTU", "B"),
            "111": ("BGEU", "B"),
        },
        "0000011": {
            "000": ("LB", "I"),
            "001": ("LH", "I"),
            "010": ("LW", "I"),
            "100": ("LBU", "I"),
            "101": ("LHU", "I"),
        },
        "0100011": {
            "000": ("SB", "S"),
            "001": ("SH", "S"),
            "010": ("SW", "S"),
        },
        "0010011": {
            "000": ("ADDI", "I"),
            "010": ("SLTI", "I"),
            "011": ("SLTIU", "I"),
            "100": ("XORI", "I"),
            "110": ("ORI", "I"),
            "111": ("ANDI", "I"),
            "001": {
                "0000000": ("SLLI", "R"),
            },
            "101": {
                "0000000": ("SRLI", "R"),
                "0100000": ("SRAI", "R"),
            },
        },
        "0110011": {
            "000": {
                "0000000": ("ADD", "R"),
                "0100000": ("SUB", "R"),
                "0000001": ("MUL", "R"),
            },
            "001": {
                "0000000": ("SLL", "R"),
                "0000001": ("MULH", "R"),
            },
            "010": {
                "0000000": ("SLT", "R"),
                "0000001": ("MULHSU", "R"),
            },
            "011": {
                "0000000": ("SLTU", "R"),
                "0000001": ("MULHU", "R"),
            },
            "100": {
                "0000000": ("XOR", "R"),
                "0000001": ("DIV", "R"),
            },
            "101": {
                "0000000": ("SRL", "R"),
                "0100000": ("SRA", "R"),
                "0000001": ("DIVU", "R"),
            },
            "110": {
                "0000000": ("OR", "R"),
                "0000001": ("REM", "R"),
            },
            "111": {
                "0000000": ("AND", "R"),
                "0000001": ("REMU", "R"),
            },
        },
        "0001111": ("FENCE", "I"),
        "1110011": {
            "000000000000": ("ECALL", "I"),
            "000000000001": ("EBREAK", "I"),
        },
    }

    def decode(self, inst):
        code = inst[25:]
        inst_dict = self.op_codes
        if code == "1110011":
            inst_metadata = inst_dict[code][inst[:12]]
        else:
            for start, end in [(25, 32), (17, 20), (0, 7)]:
                key = inst[start:end]
                if isinstance(inst_dict[key], tuple):
                    inst_metadata = inst_dict[key]
                    break
                inst_dict = inst_dict[key]

        inst_fields = self.get_inst_fields(inst, inst_metadata)

        return inst_metadata, inst_fields

    def get_inst_fields(self, inst, inst_metadata):
        fields = {}
        if inst_metadata[1] == "R":
            fields = {
                "rd": bin_to_int(inst[20:25]),
                "rs1": bin_to_int(inst[12:17]),
                "rs2": bin_to_int(inst[7:12]),
            }
        elif inst_metadata[1] == "I":
            fields = {
                "rd": bin_to_int(inst[20:25]),
                "rs1": bin_to_int(inst[12:17]),
                "imm": bin_to_int(inst[0] * 20 + inst[:12]),
            }
        elif inst_metadata[1] == "S":
            fields = {
                "rs1": bin_to_int(inst[12:17]),
                "rs2": bin_to_int(inst[7:12]),
                "imm": bin_to_int(inst[0] * 20 + inst[:7] + inst[20:25]),
            }
        elif inst_metadata[1] == "B":
            fields = {
                "rs1": bin_to_int(inst[12:17]),
                "rs2": bin_to_int(inst[7:12]),
                "imm": bin_to_int(
                    inst[0] * 20 + inst[24] + inst[1:7] + inst[20:24] + "0"
                ),
            }

        elif inst_metadata[1] == "U":
            fields = {
                "rd": bin_to_int(inst[20:25]),
                "imm": bin_to_int(inst[:20] + "0" * 12),
            }
        elif inst_metadata[1] == "J":
            fields = {
                "rd": bin_to_int(inst[20:25]),
                "imm": bin_to_int(
                    inst[0] * 12 + inst[12:20] + inst[11] + inst[1:7] + inst[7:11] + "0"
                ),
            }
        return fields
