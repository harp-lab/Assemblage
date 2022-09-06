import glob, shutil
import tqdm
import random
import string

for i in tqdm.tqdm(glob.glob('ftp/*/*.exe')):
    shutil.copy(i, 'exes/' + i.split("/")[-2] + i.split("/")[-1])
for i in tqdm.tqdm(glob.glob('ftp/*/*.dll')):
    shutil.copy(i, 'exes/' + i.split("/")[-2] + i.split("/")[-1])

