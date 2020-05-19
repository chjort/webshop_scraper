import glob
import os
import shutil
import sys

# Removes directories with less than 2 .jpg images.
data_dir = sys.argv[1]
dirs = glob.glob(os.path.join(data_dir, "*"))
for dir_ in dirs:
    files = glob.glob(os.path.join(dir_, "*.jpg"))
    if len(files) < 2:
        print(dir_)
        shutil.rmtree(dir_)
