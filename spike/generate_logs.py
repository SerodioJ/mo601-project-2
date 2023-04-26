import subprocess
import os
from glob import glob
from tqdm import tqdm


def run_spike(file, debug_file):
    file_base = str(file).split("/")[-1][:-2]
    with open(os.path.join("spike", "outputs", f"{file_base}.r"), "w") as f:
        subprocess.run(
            [
                "spike",
                "--isa=RV32IM",
                "-m0x10000:0x500000",
                "-l",
                f"--log={os.path.join('spike', 'outputs', f'{file_base}.i')}",
                "-d",
                f"--debug-cmd={debug_file}",
                file,
            ],
            stderr=f,
        )


def generate_debug_file(inst_file):
    lines = 0
    with open(inst_file, "r") as f:
        for line in f:
            if line[10:12] == "0x":
                lines += 1

    with open(f"{inst_file[:-2]}.d", "w") as f:
        f.write("until pc 0 10094\n")
        for i in range(lines):
            f.write("run 1\n")
            f.write("reg 0\n")
        f.write("quit\n")


if __name__ == "__main__":
    input_files = sorted(glob("test/*.o"))
    for file in input_files:
        run_spike(file, "spike/initial_debug.d")
    for inst_file in sorted(glob("spike/outputs/*.i")):
        generate_debug_file(inst_file)
    debug_files = tqdm(sorted(glob("spike/outputs/*.d")))
    for i, d in tqdm(zip(input_files, debug_files)):
        run_spike(i, d)
