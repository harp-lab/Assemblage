import os
import datetime
import glob
from collections import Counter
import json
from tqdm import tqdm

dates = []

print("Total binaries:", len(glob.glob("/binaries/ftp/*/*.dll"))+len(glob.glob("/binaries/ftp/*/*.exe")))
print("Total repos:", len(glob.glob("/binaries/ftp/*/pdbinfo.json")))

# 'Platform', 'Build_mode', 'Toolset_version', 'URL', 'Binary_info_list', 'Optimization', 'Pushed_at'

urls=[]
configs = []
sizes = []


for f in tqdm(glob.glob("/binaries/ftp/*/*.exe")):
    file_size = os.path.getsize(f)
    sizes.append(file_size)
for f in tqdm(glob.glob("/binaries/ftp/*/*.dll")):
    file_size = os.path.getsize(f)
    sizes.append(file_size)

print(sum(sizes)/len(sizes)/1024/1024, "MBytes")

for bin_path in tqdm(glob.glob("/binaries/ftp/*/pdbinfo.json")):
            with open(bin_path) as f:
                body = json.load(f)
            try:
                configs.append(f"{body['Platform']}{body['Build_mode']}{body['Toolset_version']}{body['Optimization']}")
                urls.append(body["URL"])
            except Exception as err:
                print(err)

print("Total", len(set(urls)), 'unique repos')




configs_d = Counter(configs)


for k,v in configs_d.items():
    print(k,": ", v)

