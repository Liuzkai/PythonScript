



nas = [[1,2,3],[2,3,4],[3,4,5]]
i = 0
result = set(nas[i])
while i < (len(nas)-1):
    i += 1
    result = set(result).intersection(set(nas[i]))

print result