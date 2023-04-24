from utils.convert import little_endian, int_to_hex


class Memory:
    def __init__(self, init_mem, access_time=10):
        self.mem = init_mem
        self.access_time = access_time

    def write(self, pos, content):
        content = little_endian(content)
        for i, b in enumerate(range(0, len(content), 2)):
            self.mem[pos + i] = content[b : b + 2]

    def get_word(self, pos):
        word = (
            self.mem.get(pos, "00")
            + self.mem.get(pos + 1, "00")
            + self.mem.get(pos + 2, "00")
            + self.mem.get(pos + 3, "00")
        )
        word = little_endian(word)
        return word, self.access_time

    def get_halfword(self, pos):
        hw = self.mem.get(pos, "00") + self.mem.get(pos + 1, "00")
        hw = little_endian(hw)
        return hw, self.access_time

    def get_byte(self, pos):
        b = self.mem.get(pos, "00")
        b = little_endian(b)
        return b, self.access_time

    def set_word(self, pos, value):
        hex_value = int_to_hex(value)
        self.write(pos, hex_value)
        return self.access_time

    def set_halfword(self, pos, value):
        hex_value = int_to_hex(value)[4:]
        self.write(pos, hex_value)
        return self.access_time

    def set_byte(self, pos, value):
        hex_value = int_to_hex(value)[6:]
        self.write(pos, hex_value)
        return self.access_time
