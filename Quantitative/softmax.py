import numpy as np
import math

def softmax(inMartix):
    m,n = np.shape(inMartix)
    outMatrix = np.mat(np.zeros((m,n)))
    soft_sum = 0
    for idx in range(0,n):
        outMatrix[0,idx] = math.exp(inMartix[0,idx])
        soft_sum += outMatrix[0, idx]
    for idx in range(0,n):
        outMatrix[0,idx]=outMatrix[0,idx]/soft_sum
    return outMatrix


a = np.array([[1,2,3]])
sm = softmax(a)
print(sm)
print(sm.sum())
