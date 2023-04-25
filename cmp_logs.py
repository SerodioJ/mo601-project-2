import filecmp
from glob import glob

if __name__ == "__main__":
    log_files = sorted(glob("test/*.log"))
    log_files = [f.split("/")[-1] for f in log_files]
    a = filecmp.cmpfiles("spike/outputs", "test", log_files)
    print(a)
