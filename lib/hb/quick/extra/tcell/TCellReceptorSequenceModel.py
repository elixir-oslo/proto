from collections import defaultdict, Counter, OrderedDict
from sklearn import metrics

from sklearn.cluster.dbscan_ import DBSCAN
from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler

import random
from quick.util.SequenceProximitityMeasures import levenshteinDistance, jaroDistance, generateProximityMatrix, \
    levenshteinDistanceNormalized, alignmentScoreBlosum100Distance, jaroWinklerDistance, alignmentScoreDistance
import numpy as np

class TCellReceptorSequenceModel(object):
    def __init__(self, sequence, label=None):
        """Label can be None in the special case when the label is
        determined through the headers."""
        self._sequence = sequence
        self._label = label
        self._headers = []
        self._chainSet = None

    @property
    def sequence(self):
        return self._sequence

    @property
    def label(self):
        if self._label:
            return self._label
        else:
            return self.chainsLabel

    @property
    def headers(self):
        return self._headers

    @property
    def copyNumber(self):
        return len(self.headers)

    @property
    def chains(self):
        if self._chainSet:
            return list(self._chainSet)
        chainSet = set()
        for currHeader in self.headers:
            if "TRA_In" in currHeader:
                chainSet.add("A-")
            elif "TRB_In" in currHeader:
                chainSet.add("B-")
            elif "TRA" in currHeader:
                chainSet.add("A+")
            elif "TRB" in currHeader:
                chainSet.add("B+")
            else:
                chainSet.add("X")
        if not chainSet:
            chainSet.add("X")
        self._chainSet = chainSet
        return list(chainSet)

    @property
    def chainsLabel(self):
        return "|".join(sorted(self.chains))

    def addHeader(self, header):
        self._chainSet = None
        self._headers.append(header)

    def __len__(self):
        if self.sequence:
            return len(self.sequence)
        return 0

    def __str__(self):
        retStr = self.sequence
        for header in self.headers:
            retStr = retStr + "\n" + header
        return retStr

    def __hash__(self):
        return hash(self.sequence)

    def __eq__(self, other):
        return self.sequence == other.sequence

    def __ne__(self, other):
        return not (self == other)

if __name__ == '__main__':
    filePath = "/Users/boris/Desktop/iris/tempdataset/allalpha_balanced.fasta"
    with open(filePath, "r") as fastaSeq:
        lines = fastaSeq.readlines()
    # titleLinesCount = 0
    seqToTCellReceptorSeqObjDict = dict()
    header = ''
    for line in lines:
        linStrpd = line.strip()
        if linStrpd.startswith(">"):
            # titleLinesCount += 1
            header = linStrpd
        else:
            currSeq = linStrpd
            if currSeq in seqToTCellReceptorSeqObjDict:
                currSeqObj = seqToTCellReceptorSeqObjDict[currSeq]
            else:
                currSeqObj = TCellReceptorSequenceModel(currSeq)
                seqToTCellReceptorSeqObjDict[currSeq] = currSeqObj
            currSeqObj.addHeader(header)

    print "Number of sequences: ", str(len(seqToTCellReceptorSeqObjDict))

    seqNr = len(seqToTCellReceptorSeqObjDict)
    n = 80
    randomSample = random.sample(list(xrange(seqNr)), n)
    randomSample.sort()
    randomSeqList = [seqToTCellReceptorSeqObjDict.keys()[x] for x in randomSample]
    # randomSeqList = seqToTCellReceptorSeqObjDict.keys()
    # n = len(randomSeqList)

    print
    labelToListOfSequencesDict = defaultdict(list)
    for seq, seqModel in seqToTCellReceptorSeqObjDict.iteritems():
        labelToListOfSequencesDict[seqModel.chainsLabel].append(seq)

    print "Class counts: "
    for classLabel, seqsPerClass in labelToListOfSequencesDict.iteritems():
        print classLabel, ": ", str(len(seqsPerClass))

    print
    print
    #
    # seqLenList = [len(x) for x in seqToTCellReceptorSeqObjDict]
    #
    # from numpy import mean, percentile
    #
    # print "Summary for sequence lengths:"
    # print "Min len: ", min(seqLenList)
    # print "1% :", percentile(seqLenList, 1)
    # print "5% :", percentile(seqLenList, 5)
    # print "25% :", percentile(seqLenList, 25)
    # print "Avg len: ", mean(seqLenList)
    # print "75% :", percentile(seqLenList, 75)
    # print "95% :", percentile(seqLenList, 95)
    # print "99% :", percentile(seqLenList, 99)
    # print "Max len: ", max(seqLenList)
    # print ""
    # print ""
    #
    # copyNumberList = [x.copyNumber for _, x in seqToTCellReceptorSeqObjDict.iteritems()]
    #
    # print "Summary for sequence copy numbers:"
    # print "Min len: ", min(copyNumberList)
    # print "1% :", percentile(copyNumberList, 1)
    # print "5% :", percentile(copyNumberList, 5)
    # print "25% :", percentile(copyNumberList, 25)
    # print "Avg len: ", mean(copyNumberList)
    # print "75% :", percentile(copyNumberList, 75)
    # print "95% :", percentile(copyNumberList, 95)
    # print "99% :", percentile(copyNumberList, 99)
    # print "Max len: ", max(copyNumberList)
    # print ""
    # print ""
    #
    # # from scipy.cluster.hierarchy import fclusterdata
    # from sklearn.cluster import dbscan
    #
    # permutIndex = np.random.permutation(len(seqToTCellReceptorSeqObjDict))
    # print permutIndex
    # randomSeqs = np.array(seqToTCellReceptorSeqObjDict.keys())[permutIndex[:250]]

    #doesn't work with strings
    # fclust1 = fclusterdata(randomSeqs, 1.0, metric=levenshteinDistance)
    # fclust2 = fclusterdata(randomSeqs, 1.0, metric=jaroDistance)
    #
    # print(np.allclose(fclust1, fclust2))
    #
    # data = ["ACCTCCTAGAAG", "ACCTACTAGAAGTT", "GAATATTAGGCCGA"]
    #
    #
    # def lev_metric(x, y):
    #     i, j = int(x[0]), int(y[0])  # extract indices
    #     return levenshteinDistance(data[i], data[j])
    #
    #
    # X = np.arange(len(data)).reshape(-1, 1)
    # print dbscan(X, metric=lev_metric, eps=5, min_samples=2)
    #
    # centers = [[1, 1], [-1, -1], [1, -1]]
    # X, labels_true = make_blobs(n_samples=750, centers=centers, cluster_std=0.4,
    #                             random_state=0)
    # X = StandardScaler().fit_transform(X)

    distanceMatrix = generateProximityMatrix(randomSeqList, jaroDistance)
    rndInd1 = random.sample(range(len(randomSeqList)), 3)
    rndInd2 = random.sample(range(len(randomSeqList)), 3)
    #
    # rndInd1 = xrange(n)
    # rndInd2 = xrange(n)

    labelList = [x.chainsLabel for x in
                 [seqToTCellReceptorSeqObjDict[t] for t in randomSeqList]]
    print "Distance matrix:"
    for i in rndInd1:
        for j in rndInd2:
            print "[%s %s,%s %s] = %f" % \
            (randomSeqList[i], labelList[i], randomSeqList[j], labelList[j], distanceMatrix[i,j])

    print
    print labelList
    print "All counts: ", Counter(labelList)



    print
    #Hierarchical code
    from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
    import scipy.spatial.distance as ssd
    distArray = ssd.squareform(distanceMatrix)
    print len(distArray)
    print np.shape(distanceMatrix)

    Z = linkage(distArray, method='complete')
    print np.shape(Z)
    for z in Z:
        idx = int(z[0])
        idy = int(z[1])
        if idx < n and idy < n:
            print "[%s %s,%s %s] = %f" % \
                  (randomSeqList[idx], labelList[idx],
                   randomSeqList[idy], labelList[idy],
                   distanceMatrix[idx, idy])

    fc1 = fcluster(Z, 8,criterion='maxclust')
    print Counter(fc1)
    clusters = defaultdict(list)
    for i, clusterId in enumerate(fc1):
        clusters[clusterId].append(labelList[i])

    for clusterId, cluster in clusters.iteritems():
        print "Cluster ID: ", clusterId
        print Counter(cluster)
    print
    from matplotlib import pyplot as plt

    plt.figure(figsize=(25, 10))
    plt.title('Hierarchical Clustering Dendrogram')
    plt.xlabel('sample index')
    plt.ylabel('distance')
    dendrogram(
        Z,
        # truncate_mode='lastp',  # show only the last p merged clusters
        # p=6,  # show only the last p merged clusters
        # show_leaf_counts=True,  # otherwise numbers in brackets are counts
        leaf_rotation=90.,  # rotates the x axis labels
        leaf_font_size=8.,  # font size for the x axis labels
        labels=labelList, #use labelList for class
        # show_contracted=True,  # to get a distribution impression in truncated branches

    )
    plt.show()


    #
    # print Z[0]
    # print "[%s %s,%s %s] = %f" % \
    #       (randomSeqList[int(Z[0, 0])], labelList[int(Z[0, 0])],
    #        randomSeqList[int(Z[0, 1])], labelList[int(Z[0, 1])], distanceMatrix[int(Z[0, 0]), int(Z[0, 1])])
    #


    #DBSCAN code
    # db = DBSCAN(eps=5, min_samples=20, metric="precomputed").fit(distanceMatrix)
    # print db
    # print db.labels_
    # cluster1Labels = [labelList[i] for i, x in enumerate(db.labels_) if x == -1]
    # cluster2Labels = [labelList[i] for i, x in enumerate(db.labels_) if x == 0]
    # print "cluster 1", Counter(cluster1Labels)
    # print "cluster 2", Counter(cluster2Labels)
    #
    # core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    # core_samples_mask[db.core_sample_indices_] = True
    # labels = db.labels_
    #
    # # Number of clusters in labels, ignoring noise if present.
    # n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    #
    # print('Estimated number of clusters: %d' % n_clusters_)
    # print("Homogeneity: %0.3f" % metrics.homogeneity_score(labelList, labels))
    # print("Completeness: %0.3f" % metrics.completeness_score(labelList, labels))
    # print("V-measure: %0.3f" % metrics.v_measure_score(labelList, labels))
    # print("Adjusted Rand Index: %0.3f"
    #       % metrics.adjusted_rand_score(labelList, labels))
    # print("Adjusted Mutual Information: %0.3f"
    #       % metrics.adjusted_mutual_info_score(labelList, labels))
    # print("Silhouette Coefficient: %0.3f"
    #       % metrics.silhouette_score(X, labels))


    #output:
    # Summary for sequence lengths:
    #     Min
    #     len:  1
    # 1 %: 8.0
    # 5 %: 9.0
    # 25 %: 11.0
    # Avg
    # len:  11.9879368458
    # 75 %: 13.0
    # 95 %: 15.0
    # 99 %: 17.0
    # Max
    # len:  51
    #
    # Summary for sequence copy numbers:
    #     Min
    #     len:  1
    # 1 %: 1.0
    # 5 %: 1.0
    # 25 %: 1.0
    # Avg
    # len:  1.96970019514
    # 75 %: 2.0
    # 95 %: 5.0
    # 99 %: 8.0
    # Max
    # len:  61
