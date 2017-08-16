import csv
import math
from collections import OrderedDict
import cPickle as cPickle
import numpy
from pandas import DataFrame
import random

#import rpy2.robjects as robjects
#r = robjects.r

######Pseudocode for how to compute all pairwise distances, give the daysColPosition only if you want to include the number of days of usage in the calculation of the distances between women; the default is to not use this info in the distance
def womanDifference(w1List, w2List, problemColPosition=1, week0_4ColPosition=2, week13ColPosition=5, daysColPosition='', coDrugColPosition=7):

    problemDiff = 3 if w1List[problemColPosition] != w2List[problemColPosition] else 0
    weekDiffs = [math.sqrt(float(int(w1List[k]))) - math.sqrt(float(int(w2List[k]))) for k in range(week0_4ColPosition,week13ColPosition+1)]
    sumWeekDiff = sum(weekDiffs)
    daysDiff = 0
    if daysColPosition != '':
        daysDiff = int(w1List[daysColPosition]) - int(w2List[daysColPosition])
        if w1List[daysColPosition]=='0' or w2List[daysColPosition]=='0':
            daysDiff += 5
    coDrugDiff = 3 if w1List[coDrugColPosition] != w2List[coDrugColPosition] else 0
    return problemDiff + sumWeekDiff + coDrugDiff + daysDiff



    ## Function which creates the distance matrix as .pkl file
def createDistanceMatrix(inFn, outFn, outFileType='pkl', womanIDcolPosition = 0, numRows=None):
    listRow = readFromDisk(inFn)
    if numRows is not None:
        selectedRows = random.sample(range(len(listRow)), numRows)
        listRow = [listRow[i] for i in selectedRows]

    distanceMatrix = generateMatrix(listRow, outFileType, womanIDcolPosition)
    writeMatrix(distanceMatrix, outFn)

    print 'distance matrix created'


def writeMatrix(distanceMatrix, outFn):
    with open(outFn, 'wb') as fp:
        # cPickle.dump(differenceDict, fp, protocol=2)
        cPickle.dump(distanceMatrix, fp, protocol=2)


def generateMatrix(listRow, outFileType, womanIDcolPosition):
    assert outFileType == 'pkl'
    # differenceDict = {} #OrderedDict()
    print "Dist.matrix size: ", len(listRow) ** 2 * 2 / 1e9
    distanceMatrix = numpy.zeros([len(listRow)] * 2, dtype="h") - 1
    secondKeys = []
    for numW1 in range(len(listRow)):
        if numW1%100==0:
            print ".100",
        for numW2 in range(numW1 + 1, len(listRow)):
            idW1 = listRow[numW1][womanIDcolPosition]

            # if not idW1 in differenceDict.keys():
            #     differenceDict[idW1] = {} #OrderedDict()

            idW2 = listRow[numW2][womanIDcolPosition]
            # if not idW2 in differenceDict[idW1].keys():
            #     differenceDict[idW1][idW2] = womanDifference(listRow[numW1], listRow[numW2]
            # print "TEMP1: ", numW1, numW2, type(numW1), type(numW2), distanceMatrix.shape
            diff = womanDifference(listRow[numW1], listRow[numW2])
            distanceMatrix[numW1, numW2] = diff
            if not idW2 in secondKeys:
                secondKeys.append(idW2)

    return distanceMatrix


def readFromDisk(inFn):
    listRow = []
    with open(inFn, 'r') as csvfile:
        data = csv.reader(csvfile, delimiter=',')
        header = None
        for line in data:
            if header is None:
                header = line
            else:
                row = line
                listRow.append(row)
    return listRow



    ### Code to run the hierarchical cluster analysis
def clusteringFunction(inFn, outFn, clustersFileOutput1, clustersFileOutput2, type='hierarchical', method1= 'centroid', method2='complete', maxClust=6):

    with open(inFn, 'rb') as fp:
        import cPickle as cPickle
        differenceDict = cPickle.load(fp)
        #print differenceDict
    df = DataFrame(differenceDict).T.fillna(0)

    if type == 'hierarchical':
        import pylab
        import scipy.cluster.hierarchy as sch

        womanID  = df.columns.values
        D = numpy.array(df)

        # Compute and plot first dendrogram.
        fig = pylab.figure(figsize=(8, 8))
        ax1 = fig.add_axes([0.09, 0.1, 0.2, 0.6])
        Y1 = sch.linkage(D, method=method1)
        Z1 = sch.dendrogram(Y1, orientation='left')
        ax1.set_xticks([])
        ax1.set_yticks([])

        # Compute and plot second dendrogram.
        ax2 = fig.add_axes([0.3, 0.71, 0.6, 0.2])
        Y2 = sch.linkage(D, method=method2)
        Z2 = sch.dendrogram(Y2)
        ax2.set_xticks([])
        ax2.set_yticks([])

        # FlutCluster.
        # flat1 = sch.fcluster(Y1, t=2, criterion='inconsistent', depth=20, R=None, monocrit=None)
        # flat2 = sch.fcluster(Y2, t=1, criterion='inconsistent', depth=20, R=None, monocrit=None)
        # print Z1
        allclustersMethod1 = []
        allclustersMethod2 = []
        for x in range(1, maxClust + 1):
            allclustersMethod1.append(numpy.append([], sch.cut_tree(Y1, x)).tolist())
            allclustersMethod2.append(numpy.append([], sch.cut_tree(Y2, x)).tolist())
        allclustersTransformMethod1 = zip(*allclustersMethod1)
        allclustersTransformMethod2 = zip(*allclustersMethod2)

        w1 = csv.writer(open(clustersFileOutput1, 'wb'))
        w2 = csv.writer(open(clustersFileOutput2, 'wb'))

        header = ["WomanID"] + ['nClusters=' + str(i) for i in range(1, maxClust + 1)]
        w1.writerow(header)
        w2.writerow(header)
        for ii in range(0, len(womanID)):
            w1.writerow([womanID[ii]] + list(allclustersTransformMethod1[ii]))
            w2.writerow([womanID[ii]] + list(allclustersTransformMethod2[ii]))
        # Plot distance matrix.
        axmatrix = fig.add_axes([0.3, 0.1, 0.6, 0.6])
        idx1 = Z1['leaves']
        idx2 = Z2['leaves']
        D = D[idx1, :]
        D = D[:, idx2]
        im = axmatrix.matshow(D, aspect='auto', origin='lower')
        axmatrix.set_xticks([])
        axmatrix.set_yticks([])

        # Plot colorbar.
        axcolor = fig.add_axes([0.91, 0.1, 0.02, 0.6])
        pylab.colorbar(im, cax=axcolor)
        fig.savefig(outFn)
    print 'clustering done'

#import time
#startTime = time.time()
#clusteringFunction('differenceDict_CombinedSectionsSmall38_39_40.pkl', 'dendrogram.png', clusterFileOutput1='flatCluster1.csv', clusterFileOutput2='flatCluster2.csv', type='hierarchical')

#createDistanceMatrix('MergedTable_Q1_CombinedSectionsSmall38_39_40.csv', 'differenceDict_CombinedSectionsSmall38_39_40.pkl', outFileType='pkl', womanIDcolPosition = 0, numRows=5)
#createDistanceMatrix('MergedTable_Q1_CombinedSections38_39_40.csv', 'differenceDict_CombinedSections38_39_40.pkl', outFileType='pkl', womanIDcolPosition = 0, numRows=1000)
#print "Time in seconds: ", time.time() - startTime