import filecmp
from glob import glob

if __name__ == "__main__":
    log_files = sorted(glob("test/*.log"))
    log_files = [f.split("/")[-1] for f in log_files]
    a = filecmp.cmpfiles("spike/outputs", "test", log_files)
    print(f"Matching Logs: {len(a[0])}/{len(log_files)}")
    if len(a[1]) != 0:
        print(f"These files do not match: {a[1]}")
    if len(a[2]) != 0:
        print(f"These files do not have a corresponding pair: {a[2]}")
