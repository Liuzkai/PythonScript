from pylab import *
import pandas as pd
import matplotlib.pyplot as plot

filePath = ("/Users/liuzhongkai/Downloads/Python量化交易实战/code/dataTest.csv")
dataFile = pd.read_csv(filePath, header=None, prefix='V')

summary = dataFile.iloc[:,10:16].describe()

dataArray = dataFile.iloc[:,10:16].values
boxplot(dataArray)
plot.xlabel('Attribute')
plot.ylabel('Score')
plot.show()


print(summary)