import os
import datetime
import glob
from collections import Counter

dates = []

for bin_path in glob.glob("/binaries/ftp/*/*"):
    if (bin_path.endswith(".dll") or bin_path.endswith(".exe")):
        mtime = os.path.getmtime(bin_path)
        dt = str(datetime.datetime.fromtimestamp(mtime))
        day = dt[:10]
        dates.append(day)

print(Counter(dates))
