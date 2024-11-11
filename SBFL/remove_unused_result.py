# This script is used to remove the unused results in the results directory.
# So as to save the disk space.
import os
import sys

from tqdm import tqdm # type: ignore

res_dir = sys.argv[1]

# recursively list all files in a directory
for root, dirs, files in tqdm(os.walk(res_dir)):
    for file in files:
        file_path = os.path.join(root, file)
        if file_path.endswith("ranking.csv"):
            write_f = open(file_path + ".new", 'w')
            with open(file_path, 'r') as f:
                line = f.readline()
                while line:
                    if line.endswith("0.0\n"):
                        break
                    write_f.write(line)
                    line = f.readline()
            write_f.close()
            os.remove(file_path)
            os.rename(file_path + ".new", file_path)
        else:
            os.remove(file_path)