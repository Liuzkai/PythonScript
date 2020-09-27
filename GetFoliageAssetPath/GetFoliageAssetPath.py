import os
import pandas as pd

files = os.listdir(os.path.dirname(__file__))
print(files)
foliages = []

for f in files :
    if f.split(".")[-1:] == ["txt"] :
        path = os.path.dirname(__file__) + '/' + f 
        txt = open(path,'r')
        line = txt.readline()
        while line :
            if line.find('/Game/') == 0 :
                out = line.replace('\n','')
                out = out.split('.')
                out_f = out[0]+'_FoliageType.'+out[1]+'_FoliageType'
                foliages.append(out_f)
            line = txt.readline()
        txt.close()

foliageSet = set(foliages)
foliagelist = [s for s in foliageSet]
targetlist = ['']*len(foliagelist)
percent = [1]*len(foliagelist)
dataframe = pd.DataFrame({'source':foliagelist, 'target':targetlist, 'percent':percent})
path = os.path.dirname(__file__) + '/foliages.csv'

# ------- Export TXT Method -------
# path = os.path.dirname(__file__) + '/foliages.txt'
# f = open(path,'w')
# for s in foliagelist:
#     f.write(s)
# f.close()

dataframe.to_csv(path, index=False, sep=',')