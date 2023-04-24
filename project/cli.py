import argparse
import subprocess
from contextlib import redirect_stdout
from glob import glob
from pathlib import Path
from tqdm import tqdm


from utils import program_load
from simulator import RISCVSimulator


def compile_to_hex(file, cmd_prefix):
    subprocess.run(
        [
            f"{cmd_prefix}gcc",
            "-march=rv32im",
            "-mabi=ilp32",
            "-Ttext=000",
            "--entry=main",
            "-nostartfiles",
            "-o",
            f"{file}.o",
            f"{file}.c",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    subprocess.run(
        [
            f"{cmd_prefix}objcopy",
            "-I",
            "elf32-littleriscv",
            "-O",
            "ihex",
            f"{file}.o",
            f"{file}.hex",
        ]
    )


def run_simulations(args):
    files = args.files
    if args.files == None:
        files = sorted(glob(args.path))
    for file in tqdm(files):
        if args.compile:
            compile_to_hex(str(file)[:-2], args.executable_prefix)
        _, mem_init = program_load.read_file(f"{str(file)[:-2]}.hex")
        risc_v = RISCVSimulator(0, mem_init)
        with open(f"{str(file)[:-2]}.log", "w") as f:
            with redirect_stdout(f):
                risc_v.run()

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-f",
        "--files",
        help="path to input files to use, if not set will run with all files at test/",
        type=Path,
        nargs="+",
    )

    parser.add_argument(
        "-p", "--path", help="path for test folder", type=str, default="test/*.c"
    )

    parser.add_argument(
        "-e",
        "--executable-prefix",
        help="RISC-V executable prefix",
        type=str,
        default="riscv32-unknown-elf-",
    )

    parser.add_argument(
        "-c",
        "--compile",
        help="Compile C files and perform objcopy to get simulators' input file",
        action="store_true",
    )

    args = parser.parse_args()
    run_simulations(args)
