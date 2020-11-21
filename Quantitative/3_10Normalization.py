from pylab import *
import pandas as pd
import matplotlib.pyplot as plot


filePath = ("/Users/liuzhongkai/Downloads/Python量化交易实战/code/dataTest.csv")
dataFile = pd.read_csv(filePath, header=None, prefix='V')

summary = dataFile.describe()
dataFile_normalization = dataFile.iloc[:,1:6]

for i in range(5) :
    mean = summary.iloc[1,i+1]
    std = summary.iloc[2,i+1]
    dataFile_normalization.iloc[:,i:i+1] = (dataFile_normalization.iloc[:,i:i+1] - mean)/ std

a = dataFile_normalization.values
b = dataFile.iloc[:,1:6].values
boxplot(a)
plot.xlabel("Attribute")
plot.ylabel("Score")
plot.show()