
# the txt path, you must change it to your file path.
path = 'C:/Users/zhongkailiu.TENCENT/Desktop/'
txt = 'Arkfoliage.txt'
f = open(path+txt)
line = f.readline()

path = []

while line :
    p = line.split(" ")[2]
    if p not in path :
        path.append(p)
        print(p)
    line = f.readline()



