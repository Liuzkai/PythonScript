import os
import hou

hipdir = hou.getenv('HIP')
bpdir = hipdir+"/backup"

files = os.listdir(bpdir)

sortfiles = sorted(files, key=lambda x: os.path.getmtime(os.path.join(bpdir, x)))
delfilepath = [bpdir + '/' + f for f in sortfiles[:-2]]
for d in delfilepath:
    os.remove(d)