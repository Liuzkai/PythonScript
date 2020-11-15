import pandas as pd
import matplotlib.pyplot as plot

filePath = ("/Users/liuzhongkai/Downloads/Python量化交易实战/code/dataTest.csv")
dataFile = pd.read_csv(filePath,header=None,prefix='V')
dataRow1 = dataFile.iloc[100,1:300]
dataRow2 = dataFile.iloc[101,1:300]
plot.scatter(dataRow1, dataRow2)
plot.ylabel('dataRow2')
plot.xlabel('dataRow1')
plot.show()