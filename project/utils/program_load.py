def read_file(path):
    content = {}
    EOF = False
    base_addr = 0
    start_addr = 0
    with open(path, "r") as f:
        while not EOF:
            line = f.readline().strip()
            r_type = line[7:9]
            if r_type == "00":
                addr = int(line[3:7], 16) + base_addr
                num_bytes = int(line[1:3], 16)
                line = line[9:]
                for start in range(num_bytes):
                    content[addr] = line[start * 2 : (start + 1) * 2]
                    addr += 1
            elif r_type == "01":
                EOF = True
            elif r_type == "02":
                base_addr = int(line[9:13], 16) * 16
            elif r_type == "03":
                start_addr = int(line[9:13], 16) * 16 + int(line[13:17], 16)
            elif r_type == "04":
                base_addr = int(line[9:13], 16) << 16
            elif r_type == "05":
                start_addr = int(line[9:17], 16)
    return start_addr, content
