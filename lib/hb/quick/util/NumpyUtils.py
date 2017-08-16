# Utility functions for Numpy objects
import numpy as np


def getNumpyMatrixMaxElement(npMat):
    maxRowInd, maxColInd = np.unravel_index(np.nanargmax(npMat), npMat.shape)
    return npMat[maxRowInd, maxColInd], maxRowInd, maxColInd


def getNumpyMatrixMinElement(npMat):
    minRowInd, minColInd = np.unravel_index(np.nanargmin(npMat), npMat.shape)
    return npMat[minRowInd, minColInd], minRowInd, minColInd