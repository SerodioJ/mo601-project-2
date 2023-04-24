import numpy as np


def little_endian(content):
    converted = ""
    num_bytes = len(content) // 2
    for byte in range(num_bytes):
        start = (num_bytes - byte - 1) * 2
        converted += content[start : start + 2]
    return converted


def hex_to_int(content):
    return np.int32(int(content, 16))


def bin_to_int(content):
    return np.int32(int(content, 2))


def hex_to_bin(content):
    return format(int(content, 16), "0>32b")


def bin_to_hex(content):
    return format(int(content, 2), "0>8X")


def int_to_hex(content):
    return format(content & ((1 << 32) - 1), "0>8X")


def int_to_bin(content):
    return np.binary_repr(content, width=32)
