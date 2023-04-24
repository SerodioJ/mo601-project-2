import argparse
import subprocess
from contextlib import redirect_stdout
from glob import glob
from pathlib import Path
from tqdm import tqdm


from utils import program_load
from simulator import RISCVSimulator


def compile_to_hex(file, cmd_prefix):
    compilation = subprocess.Popen(
        [
            f"{cmd_prefix}gcc",
            "-g",
            "-march=rv32imafd",
            "-std=gnu99",
            "-mabi=ilp32d",
            "-Ttext=000",
            "--entry=main",
            "-nostdlib",
            "-o",
            f"{file}.o",
            f"{file}.c",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    compilation.communicate()
    obj_copy = subprocess.Popen(
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
    obj_copy.communicate()


def run_simulations(args):
    files = args.files
    if args.files == None:
        files = sorted(glob(args.path))
    for file in tqdm(files):
        if args.compile:
            compile_to_hex(str(file)[:-2], args.executable_prefix)
        start_addr, mem_init = program_load.read_file(f"{str(file)[:-2]}.hex")
        risc_v = RISCVSimulator(start_addr, mem_init, sp=args.stack_pointer)
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
        default="riscv32-unknown-linux-gnu-",
    )

    parser.add_argument(
        "-c",
        "--compile",
        help="Compile C files and perform objcopy to get simulators' input file",
        action="store_true",
    )

    parser.add_argument(
        "-s",
        "--stack-pointer",
        help="Stack pointer initial address",
        type=int,
        default=400000,
    )

    args = parser.parse_args()
    run_simulations(args)
