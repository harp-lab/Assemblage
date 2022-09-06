f = open("rec.txt")
lines = f.readlines()
f.close()


winbinlines = list(map(lambda x:x.strip().replace("Windows binaries Saved: ", "").split("/past hour")[0], list(filter(lambda x:x.startswith("Windows binaries Saved"), lines))))
for x in winbinlines:
    print(x)