import numpy as np

from components.memory import Memory
from components.register import RegisterFile
from components.decoder import Decoder
from logger.logger import Logger
from utils.convert import hex_to_bin, bin_to_int, hex_to_int


class RISCVSimulator:
    extend_sign = ["8", "9", "A", "B", "C", "D", "E", "F"]

    def __init__(self, pc, init_memory):
        self.pc = pc
        self.next_pc = None
        self.memory = Memory(init_memory)
        self.register_file = RegisterFile()
        self.decoder = Decoder()
        self.logger = Logger()

    def run(self):
        while True:
            self.logger.set_pc(self.pc)
            inst = self._instruction_fetch()
            self.logger.set_inst(inst)
            inst = hex_to_bin(inst)
            inst_metadata, inst_fields = self._instruction_decode(inst)
            self.logger.set_inst_disassembly(inst_metadata[0], inst_fields)
            reg_id = bin_to_int(inst[12:17])
            self.logger.set_reg(
                "rs1", reg_id, self.register_file.registers[reg_id].getVal()
            )
            reg_id = bin_to_int(inst[7:12])
            self.logger.set_reg(
                "rs2", reg_id, self.register_file.registers[reg_id].getVal()
            )

            self._execute(inst_metadata[0], inst_fields)
            # self._execute(inst_metadata, inst_fields)
            reg_id = bin_to_int(inst[20:25])
            self.logger.set_reg(
                "rd", reg_id, self.register_file.registers[reg_id].getVal()
            )

            self.logger.log()
            self.pc = self.next_pc if self.next_pc != None else self.pc + 4
            if self.pc == 0:
                break
            self.next_pc = None

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

    def _AUIPC(self, inst_fields):
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(inst_fields["imm"] + self.pc)

    def _JAL(self, inst_fields):
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(self.pc + 4)
        self.next_pc = self.pc + inst_fields["imm"]

    def _JALR(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(self.pc + 4)
        self.next_pc = rs1.getVal() + inst_fields["imm"]

    def _BEQ(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        if rs1.getVal() == rs2.getVal():
            self.next_pc = self.pc + inst_fields["imm"]

    def _BNE(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        if rs1.getVal() != rs2.getVal():
            self.next_pc = self.pc + inst_fields["imm"]

    def _BLT(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        if rs1.getVal() < rs2.getVal():
            self.next_pc = self.pc + inst_fields["imm"]

    def _BGE(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        if rs1.getVal() >= rs2.getVal():
            self.next_pc = self.pc + inst_fields["imm"]

    def _BLTU(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        if np.uint32(rs1.getVal()) < np.uint32(rs2.getVal()):
            self.next_pc = self.pc + inst_fields["imm"]

    def _BGEU(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        if np.uint32(rs1.getVal()) >= np.uint32(rs2.getVal()):
            self.next_pc = self.pc + inst_fields["imm"]

    def _LB(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        addr = rs1.getVal() + inst_fields["imm"]
        value, _ = self.memory.get_byte(addr)
        if value[0] in self.extend_sign:
            value = "F" * 12 + value
        rd.setVal(hex_to_int(value))

    def _LH(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        addr = rs1.getVal() + inst_fields["imm"]
        value, _ = self.memory.get_halfword(addr)
        if value[0] in self.extend_sign:
            value = "F" * 8 + value
        rd.setVal(hex_to_int(value))

    def _LW(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        addr = rs1.getVal() + inst_fields["imm"]
        value = hex_to_int(self.memory.get_word(addr)[0])
        rd.setVal(value)

    def _LBU(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        addr = rs1.getVal() + inst_fields["imm"]
        value = hex_to_int(self.memory.get_byte(addr)[0])
        rd.setVal(value)

    def _LHU(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        addr = rs1.getVal() + inst_fields["imm"]
        value = hex_to_int(self.memory.get_halfword(addr)[0])
        rd.setVal(value)

    def _SB(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        addr = rs1.getVal() + inst_fields["imm"]
        self.memory.set_byte(addr, rs2.getVal())

    def _SH(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        addr = rs1.getVal() + inst_fields["imm"]
        self.memory.set_halfword(addr, rs2.getVal())

    def _SW(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        addr = rs1.getVal() + inst_fields["imm"]
        self.memory.set_word(addr, rs2.getVal())

    def _ADDI(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() + inst_fields["imm"])

    def _SLTI(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(1 if rs1.getVal() < inst_fields["imm"] else 0)

    def _SLTIU(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(1 if np.uint32(rs1.getVal()) < np.uint32(inst_fields["imm"]) else 0)

    def _XORI(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() ^ inst_fields["imm"])

    def _ORI(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() | inst_fields["imm"])

    def _ANDI(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() & inst_fields["imm"])

    def _SLLI(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        shamt = inst_fields["rs2"]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() << shamt)

    def _SRLI(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        shamt = inst_fields["rs2"]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(np.uint32(rs1.getVal()) >> shamt)

    def _SRAI(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        shamt = inst_fields["rs2"]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() >> shamt)

    def _ADD(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() + rs2.getVal())

    def _SUB(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() - rs2.getVal())

    def _SLT(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(1 if rs1.getVal() < rs2.getVal() else 0)

    def _SLTU(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(1 if np.uint32(rs1.getVal()) < np.uint32(rs2.getVal()) else 0)

    def _SLL(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() << rs2.getVal())

    def _SRL(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(np.uint32(rs1.getVal()) >> rs2.getVal())

    def _SRA(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() >> rs2.getVal())

    def _XOR(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() ^ rs2.getVal())

    def _OR(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() | rs2.getVal())

    def _AND(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() & rs2.getVal())

    def _FENCE(self, inst_fields):
        pass

    def _ECALL(self, inst_fields):
        pass

    def _EBREAK(self, inst_fields):
        pass

    def _MUL(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() * rs2.getVal())

    def _MULH(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal((np.int64(rs1.getVal()) * np.int64(rs2.getVal())) >> 32)

    def _MULHSU(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal((np.int64(rs1.getVal()) * np.uint64(rs2.getVal())) >> 32)

    def _MULHU(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal((np.uint64(rs1.getVal()) * np.uint64(rs2.getVal())) >> np.uint32(32))

    def _DIV(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() // rs2.getVal())

    def _DIVU(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(np.uint32(rs1.getVal()) // np.uint32(rs2.getVal()))

    def _REM(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(rs1.getVal() % rs2.getVal())

    def _REMU(self, inst_fields):
        rs1 = self.register_file.registers[inst_fields["rs1"]]
        rs2 = self.register_file.registers[inst_fields["rs2"]]
        rd = self.register_file.registers[inst_fields["rd"]]
        rd.setVal(np.uint32(rs1.getVal()) % np.uint32(rs2.getVal()))
