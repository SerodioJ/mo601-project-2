import numpy as np

from components.memory import Memory
from components.register import RegisterFile
from components.decoder import Decoder
from logger.logger import Logger
from utils.convert import hex_to_bin, bin_to_int, hex_to_int


class RISCVSimulator:
    extend_sign = ["8", "9", "A", "B", "C", "D", "E", "F"]

    def __init__(self, pc, init_memory, disassembly=False):
        np.seterr(all="ignore")
        self.pc = np.uint32(pc)
        self.next_pc = None
        self.memory = Memory(init_memory)
        self.register_file = RegisterFile()
        self.decoder = Decoder()
        self.logger = Logger(disassembly=disassembly)
        self.ebreak = False

    def run(self):
        inst_count = 0
        while True:
            self.logger.set_pc(self.pc)
            inst = self._instruction_fetch()
            self.logger.set_inst(inst)
            inst = hex_to_bin(inst)
            inst_metadata, inst_fields = self._instruction_decode(inst)

            reg_id = bin_to_int(inst[12:17])
            self.logger.set_reg(
                "rs1", reg_id, self.register_file.registers[reg_id].getVal()
            )
            reg_id = bin_to_int(inst[7:12])
            self.logger.set_reg(
                "rs2", reg_id, self.register_file.registers[reg_id].getVal()
            )

            self._execute(inst_metadata[0], inst_fields)

            reg_id = bin_to_int(inst[20:25])
            self.logger.set_reg(
                "rd", reg_id, self.register_file.registers[reg_id].getVal()
            )

            self.logger.log()
            inst_count += 1
            self.pc = self.next_pc if self.next_pc != None else self.pc + 4
            if self.ebreak:
                break
            self.next_pc = None
        return inst_count

    def _instruction_fetch(self):
        inst, _ = self.memory.get_word(self.pc)
        return inst

    def _instruction_decode(self, inst):
        return self.decoder.decode(inst)

    def _execute(self, inst, inst_fields):
        inst_method = getattr(self, "_" + inst)
        inst_method(inst_fields)

    # Operations
    def _LUI(self, inst_fields):
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(inst_fields["imm"])
        self.logger.set_inst_disassembly(f"{'LUI':>8} {self.logger.registers[inst_fields['rd']]},0x{inst_fields['imm'] >> 12:X}")

    def _AUIPC(self, inst_fields):
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(inst_fields["imm"] + self.pc)
        self.logger.set_inst_disassembly(f"{'AUIPC':>8} {self.logger.registers[inst_fields['rd']]},0x{np.uint32(inst_fields['imm']) >> 12:X}")

    def _JAL(self, inst_fields):
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(self.pc + 4)
        self.next_pc = self.pc + inst_fields["imm"]
        self.logger.set_inst_disassembly(f"{'JAL':>8} {self.logger.registers[inst_fields['rd']]},0x{self.next_pc:X}")

    def _JALR(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(self.pc + 4)
        self.next_pc = np.uint32(rs1.getVal()) + inst_fields["imm"]
        self.logger.set_inst_disassembly(f"{'JALR':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},0x{self.next_pc:X}")

    def _BEQ(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        next_pc = self.pc + inst_fields["imm"]
        if rs1.getVal() == rs2.getVal():
            self.next_pc = next_pc
        self.logger.set_inst_disassembly(f"{'BEQ':>8} {self.logger.registers[inst_fields['rs1']]},{self.logger.registers[inst_fields['rs2']]},0x{next_pc:X}")

    def _BNE(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        next_pc = self.pc + inst_fields["imm"]
        if rs1.getVal() != rs2.getVal():
            self.next_pc = next_pc
        self.logger.set_inst_disassembly(f"{'BNE':>8} {self.logger.registers[inst_fields['rs1']]},{self.logger.registers[inst_fields['rs2']]},0x{next_pc:X}")

    def _BLT(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        next_pc = self.pc + inst_fields["imm"]
        if rs1.getVal() < rs2.getVal():
            self.next_pc = next_pc
        self.logger.set_inst_disassembly(f"{'BEQ':>8} {self.logger.registers[inst_fields['rs1']]},{self.logger.registers[inst_fields['rs2']]},0x{next_pc:X}")

    def _BGE(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        next_pc = self.pc + inst_fields["imm"]
        if rs1.getVal() >= rs2.getVal():
            self.next_pc = next_pc
        self.logger.set_inst_disassembly(f"{'BGE':>8} {self.logger.registers[inst_fields['rs1']]},{self.logger.registers[inst_fields['rs2']]},0x{next_pc:X}")

    def _BLTU(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        next_pc = self.pc + inst_fields["imm"]
        if np.uint32(rs1.getVal()) < np.uint32(rs2.getVal()):
            self.next_pc = next_pc
        self.logger.set_inst_disassembly(f"{'BLTU':>8} {self.logger.registers[inst_fields['rs1']]},{self.logger.registers[inst_fields['rs2']]},0x{next_pc:X}")

    def _BGEU(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        next_pc = self.pc + inst_fields["imm"]
        if np.uint32(rs1.getVal()) >= np.uint32(rs2.getVal()):
            self.next_pc = self.pc + inst_fields["imm"]
        self.logger.set_inst_disassembly(f"{'BGEU':>8} {self.logger.registers[inst_fields['rs1']]},{self.logger.registers[inst_fields['rs2']]},0x{next_pc:X}")

    def _LB(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        addr = rs1.getVal() + inst_fields["imm"]
        value, _ = self.memory.get_byte(addr)
        if value[0] in self.extend_sign:
            value = "F" * 12 + value
        rd.setVal(hex_to_int(value))
        self.logger.set_inst_disassembly(f"{'LB':>8} {self.logger.registers[inst_fields['rd']]},{inst_fields['imm']}({self.logger.registers[inst_fields['rs1']]})")

    def _LH(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        addr = rs1.getVal() + inst_fields["imm"]
        value, _ = self.memory.get_halfword(addr)
        if value[0] in self.extend_sign:
            value = "F" * 8 + value
        rd.setVal(hex_to_int(value))
        self.logger.set_inst_disassembly(f"{'LH':>8} {self.logger.registers[inst_fields['rd']]},{inst_fields['imm']}({self.logger.registers[inst_fields['rs1']]})")

    def _LW(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        addr = rs1.getVal() + inst_fields["imm"]
        value = hex_to_int(self.memory.get_word(addr)[0])
        rd.setVal(value)
        self.logger.set_inst_disassembly(f"{'LW':>8} {self.logger.registers[inst_fields['rd']]},{inst_fields['imm']}({self.logger.registers[inst_fields['rs1']]})")

    def _LBU(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        addr = rs1.getVal() + inst_fields["imm"]
        value = hex_to_int(self.memory.get_byte(addr)[0])
        rd.setVal(value)
        self.logger.set_inst_disassembly(f"{'LBU':>8} {self.logger.registers[inst_fields['rd']]},{inst_fields['imm']}({self.logger.registers[inst_fields['rs1']]})")

    def _LHU(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        addr = rs1.getVal() + inst_fields["imm"]
        value = hex_to_int(self.memory.get_halfword(addr)[0])
        rd.setVal(value)
        self.logger.set_inst_disassembly(f"{'LHU':>8} {self.logger.registers[inst_fields['rd']]},{inst_fields['imm']}({self.logger.registers[inst_fields['rs1']]})")

    def _SB(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        addr = rs1.getVal() + inst_fields["imm"]
        self.memory.set_byte(addr, rs2.getVal())
        self.logger.set_inst_disassembly(f"{'SB':>8} {self.logger.registers[inst_fields['rs2']]},{inst_fields['imm']}({self.logger.registers[inst_fields['rs1']]})")

    def _SH(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        addr = rs1.getVal() + inst_fields["imm"]
        self.memory.set_halfword(addr, rs2.getVal())
        self.logger.set_inst_disassembly(f"{'SH':>8} {self.logger.registers[inst_fields['rs2']]},{inst_fields['imm']}({self.logger.registers[inst_fields['rs1']]})")

    def _SW(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        addr = rs1.getVal() + inst_fields["imm"]
        self.memory.set_word(addr, rs2.getVal())
        self.logger.set_inst_disassembly(f"{'SW':>8} {self.logger.registers[inst_fields['rs2']]},{inst_fields['imm']}({self.logger.registers[inst_fields['rs1']]})")

    def _ADDI(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() + inst_fields["imm"])
        self.logger.set_inst_disassembly(f"{'ADDI':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},{inst_fields['imm']}")

    def _SLTI(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(1 if rs1.getVal() < inst_fields["imm"] else 0)
        self.logger.set_inst_disassembly(f"{'SLTI':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},{inst_fields['imm']}")

    def _SLTIU(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(1 if np.uint32(rs1.getVal()) < np.uint32(inst_fields["imm"]) else 0)
        self.logger.set_inst_disassembly(f"{'SLTIU':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},{np.uint32(inst_fields['imm'])}")

    def _XORI(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() ^ inst_fields["imm"])
        self.logger.set_inst_disassembly(f"{'XORI':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},{inst_fields['imm']}")

    def _ORI(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() | inst_fields["imm"])
        self.logger.set_inst_disassembly(f"{'ORI':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},{inst_fields['imm']}")

    def _ANDI(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() & inst_fields["imm"])
        self.logger.set_inst_disassembly(f"{'AND':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},{inst_fields['imm']}")

    def _SLLI(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        shamt = inst_fields["rs2"]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() << shamt)
        self.logger.set_inst_disassembly(f"{'SLLI':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},0x{shamt:X}")


    def _SRLI(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        shamt = inst_fields["rs2"]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(np.uint32(rs1.getVal()) >> shamt)
        self.logger.set_inst_disassembly(f"{'SRLI':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},0x{shamt:X}")

    def _SRAI(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        shamt = inst_fields["rs2"]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() >> shamt)
        self.logger.set_inst_disassembly(f"{'SRAI':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},0x{shamt:X}")

    def _ADD(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() + rs2.getVal())
        self.logger.set_inst_disassembly(f"{'ADD':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},{self.logger.registers[inst_fields['rs2']]}")

    def _SUB(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() - rs2.getVal())
        self.logger.set_inst_disassembly(f"{'SUB':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},{self.logger.registers[inst_fields['rs2']]}")

    def _SLT(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(1 if rs1.getVal() < rs2.getVal() else 0)
        self.logger.set_inst_disassembly(f"{'SLT':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},{self.logger.registers[inst_fields['rs2']]}")

    def _SLTU(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(1 if np.uint32(rs1.getVal()) < np.uint32(rs2.getVal()) else 0)
        self.logger.set_inst_disassembly(f"{'SLTU':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},{self.logger.registers[inst_fields['rs2']]}")

    def _SLL(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() << rs2.getVal())
        self.logger.set_inst_disassembly(f"{'SLL':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},{self.logger.registers[inst_fields['rs2']]}")

    def _SRL(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(np.uint32(rs1.getVal()) >> rs2.getVal())
        self.logger.set_inst_disassembly(f"{'SRL':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},{self.logger.registers[inst_fields['rs2']]}")

    def _SRA(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() >> rs2.getVal())
        self.logger.set_inst_disassembly(f"{'SRA':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},{self.logger.registers[inst_fields['rs2']]}")

    def _XOR(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() ^ rs2.getVal())
        self.logger.set_inst_disassembly(f"{'XOR':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},{self.logger.registers[inst_fields['rs2']]}")

    def _OR(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() | rs2.getVal())
        self.logger.set_inst_disassembly(f"{'OR':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},{self.logger.registers[inst_fields['rs2']]}")

    def _AND(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() & rs2.getVal())
        self.logger.set_inst_disassembly(f"{'AND':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},{self.logger.registers[inst_fields['rs2']]}")

    def _FENCE(self, inst_fields):
        self.logger.set_inst_disassembly(f"{'FENCE':>8}")

    def _ECALL(self, inst_fields):
        self.logger.set_inst_disassembly(f"{'ECALL':>8}")

    def _EBREAK(self, inst_fields):
        self.ebreak = True
        self.logger.set_inst_disassembly(f"{'EBREAK':>8}")

    def _MUL(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() * rs2.getVal())
        self.logger.set_inst_disassembly(f"{'MUL':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},{self.logger.registers[inst_fields['rs2']]}")

    def _MULH(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal((np.int64(rs1.getVal()) * np.int64(rs2.getVal())) >> 32)
        self.logger.set_inst_disassembly(f"{'MULH':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},{self.logger.registers[inst_fields['rs2']]}")

    def _MULHSU(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal((np.int64(rs1.getVal()) * np.uint64(np.uint32(rs2.getVal()))) >> 32)
        self.logger.set_inst_disassembly(f"{'MULHSU':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},{self.logger.registers[inst_fields['rs2']]}")

    def _MULHU(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(
            (np.uint64(np.uint32(rs1.getVal())) * np.uint64(np.uint32(rs2.getVal())))
            >> np.uint32(32)
        )
        self.logger.set_inst_disassembly(f"{'MULHU':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},{self.logger.registers[inst_fields['rs2']]}")

    def _DIV(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() / rs2.getVal())
        self.logger.set_inst_disassembly(f"{'DIV':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},{self.logger.registers[inst_fields['rs2']]}")

    def _DIVU(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(np.uint32(rs1.getVal()) // np.uint32(rs2.getVal()))
        self.logger.set_inst_disassembly(f"{'DIVU':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},{self.logger.registers[inst_fields['rs2']]}")

    def _REM(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() % rs2.getVal())
        self.logger.set_inst_disassembly(f"{'REM':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},{self.logger.registers[inst_fields['rs2']]}")

    def _REMU(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(np.uint32(rs1.getVal()) % np.uint32(rs2.getVal()))
        self.logger.set_inst_disassembly(f"{'REMU':>8} {self.logger.registers[inst_fields['rd']]},{self.logger.registers[inst_fields['rs1']]},{self.logger.registers[inst_fields['rs2']]}")
