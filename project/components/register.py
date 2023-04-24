import numpy as np


class Register:
    def __init__(self):
        self.val = np.int32(0)

    def getVal(self):
        return self.val

    def setVal(self, val):
        self.val = np.int32(val)


class x0(Register):
    def getVal(self):
        return np.int32(0)


class RegisterFile:
    def __init__(self, sp):
        self.registers = {i: Register() for i in range(1, 32)}
        self.registers[0] = x0()
        self.registers[2].setVal(sp)
