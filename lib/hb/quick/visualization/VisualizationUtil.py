'''
Created on May 18, 2015

@author: boris
'''

    
def normalizeMatrixData(plotData):
    transposed = [list(x) for x in zip(*plotData)]
    transposedNormalized = []
    for row in transposed:
        maxRow = max(row)
        if maxRow == 0:
            maxRow = 1
        transposedNormalized.append([1.0*x/maxRow for x in row])
    return [list(x) for x in zip(*transposedNormalized)]
