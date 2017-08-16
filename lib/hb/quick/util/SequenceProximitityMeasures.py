import Levenshtein as lev
from Bio import pairwise2
from Bio.SubsMat import MatrixInfo as matlist


#decorator for pretifying name of function
def rename(newname):
    def decorator(f):
        f.__name__ = newname
        return f
    return decorator


def levenshteinDistance(seq1, seq2):
    return lev.distance(seq1, seq2)


def levenshteinSimilarity(seq1, seq2, normalizationFactor=None):
    """https://rawgit.com/ztane/python-Levenshtein/master/docs/Levenshtein.html
    1 - (edit distance / normalization factor)
    If normalization factor is not defined use {length of the larger of the two strings}"""
    return 1 - levenshteinDistanceNormalized(seq1, seq2, normalizationFactor=normalizationFactor)


def levenshteinDistanceNormalized(seq1, seq2, normalizationFactor=None):
    """https://rawgit.com/ztane/python-Levenshtein/master/docs/Levenshtein.html
    (edit distance / normalization factor)
    If normalization factor is not defined use {length of the larger of the two strings}"""
    normFactor = normalizationFactor if normalizationFactor else (max(len(seq1), len(seq2)))
    return float(levenshteinDistance(seq1, seq2)) / normFactor


# def editDistance(seq1, seq2):
#     """same as levenshteing distance, implemented for convenience"""
#     return lev.distance(seq1, seq2)


def hammingDistance(seq1, seq2):
    """https://rawgit.com/ztane/python-Levenshtein/master/docs/Levenshtein.html"""
    assert len(seq1) == len(seq2), "Both sequences must be of same length."
    return lev.hamming(seq1, seq2)


def jaroSimilarity(seq1, seq2):
    """https://rawgit.com/ztane/python-Levenshtein/master/docs/Levenshtein.html"""
    return lev.jaro(seq1, seq2)


def jaroDistance(seq1, seq2):
    return 1 - jaroSimilarity(seq1, seq2)


def jaroWinklerSimilarity(seq1, seq2):
    """https://rawgit.com/ztane/python-Levenshtein/master/docs/Levenshtein.html"""
    return lev.jaro_winkler(seq1, seq2)


def jaroWinklerDistance(seq1, seq2):
    return 1 - jaroWinklerSimilarity(seq1, seq2)


def alignmentScoreSimilarity(seq1, seq2):
    """As defined in the Bio.Pairwise2 package"""
    return pairwise2.align.globalxx(seq1, seq2, score_only=True)


def alignmentScoreDistance(seq1, seq2):
    if seq1 == seq2:
        return 0.0
    algnScore = alignmentScoreSimilarity(seq1, seq2)
    if algnScore == 0:
        return 1.0
    return 1.0 / algnScore


def centeredLevenshteinDistance(seq1, seq2):
    return centeredAlignmentScore(seq1, seq2, levenshteinDistance, isSimilarityMeasure=False)


def alignmentScoreBlosum100(seq1, seq2):
    return _customAlignmentScore(seq1, seq2, matlist.blosum100)


def alignmentScoreBlosum100Distance(seq1, seq2):
    return customAlignmentScoreDistance(seq1, seq2, alignmentScoreBlosum100)


def alignmentScoreBlosum62(seq1, seq2):
    return _customAlignmentScore(seq1, seq2, matlist.blosum62)


def alignmentScoreBlosum62Distance(seq1, seq2):
    return customAlignmentScoreDistance(seq1, seq2, alignmentScoreBlosum62)


def centeredAlignmentScoreBlosum100(seq1, seq2):
    return centeredAlignmentScore(seq1, seq2, alignmentScoreBlosum100)


def centeredAlignmentScoreBlosum100Distance(seq1, seq2):
    return customAlignmentScoreDistance(seq1, seq2, centeredAlignmentScoreBlosum100)


def centeredAlignmentScoreBlosum62(seq1, seq2):
    return centeredAlignmentScore(seq1, seq2, alignmentScoreBlosum62)


def centeredAlignmentScoreBlosum62Distance(seq1, seq2):
    return customAlignmentScoreDistance(seq1, seq2, centeredAlignmentScoreBlosum62)


def fixedAlignmentScoreBlosum62(seq1, seq2):
    return _fixedAlignmentScore(seq1, seq2, matlist.blosum62)


def fixedAlignmentScoreBlosum100(seq1, seq2):
    return _fixedAlignmentScore(seq1, seq2, matlist.blosum100)


def fixedCenteredAlignmentScoreBlosum62(seq1, seq2):
    return centeredAlignmentScore(seq1, seq2, fixedAlignmentScoreBlosum62)


def fixedCenteredAlignmentScoreBlosum100(seq1, seq2):
    return centeredAlignmentScore(seq1, seq2, fixedAlignmentScoreBlosum100)


def fixedCenteredAlignmentScoreBlosum62Distance(seq1, seq2):
    return customAlignmentScoreDistance(seq1, seq2, fixedCenteredAlignmentScoreBlosum62)


def fixedCenteredAlignmentScoreBlosum100Distance(seq1, seq2):
    return customAlignmentScoreDistance(seq1, seq2, fixedCenteredAlignmentScoreBlosum100)


def _fixedAlignmentScore(seq1, seq2, scoreMatrix):
    "No gaps, just sum scores per matching position character"
    assert(len(seq1) == len(seq2))
    return sum([scoreMatrix[pair] if pair in scoreMatrix else scoreMatrix[pair[::-1]] for pair in zip(seq1, seq2)])



def customAlignmentScoreDistance(seq1, seq2, scoreFunc, *args, **kwargs):
    if seq1 == seq2:
        return 0.0
    score = scoreFunc(seq1, seq2, *args, **kwargs)
    #TODO boris: handle negative scores for fixed alignment scores
    if score < 0:
        return 1.0
    if score == 0:
        return 1.0
    return 1.0 / score


def _customAlignmentScore(seq1, seq2, scoreMatrix):
    return pairwise2.align.globaldx(seq1, seq2, scoreMatrix, score_only=True)


def centeredAlignmentScore(seq1, seq2, scoreFunc, isSimilarityMeasure = True):
    """return best alignment score of the shorter sequence to the central part of same length of the longer sequence
    with a 1 character shift left and right"""
    if len(seq1) == len(seq2):
        return scoreFunc(seq1, seq2)
    longerSeq, shorterSeq = (seq2, seq1) if len(seq2) > len(seq1) else (seq1, seq2)

    diffInLength = len(longerSeq) - len(shorterSeq)
    shifters = [0, 1] if diffInLength % 2 else [-1, 0, 1]
    scores = []
    for i in shifters:
        startIndex = diffInLength/2 + i
        endIndex = diffInLength/2 + i + len(shorterSeq)
        scores.append(scoreFunc(longerSeq[startIndex:endIndex], shorterSeq))
    return max(scores) if isSimilarityMeasure else min(scores)


#TODO: temporarily here, should move to a Util class
def generateProximityMatrix(sequenceList, proximityFunc, isSymmetrical=False,
                            *args, **kwargs):
    from numpy import zeros
    n = len(sequenceList)
    assert n > 0, "Empty sequence list"
    resultMatrix = zeros((n, n))
    if isSymmetrical:
        for i, seq1 in enumerate(sequenceList):
            for j, seq2 in enumerate(sequenceList):
                if i > j:
                    resultMatrix[i, j] = resultMatrix[j, i]
                else:
                    resultMatrix[i, j] = proximityFunc(seq1, seq2, *args, **kwargs)
    else:
        for i, seq1 in enumerate(sequenceList):
            for j, seq2 in enumerate(sequenceList):
                resultMatrix[i, j] = proximityFunc(seq1, seq2, *args, **kwargs)

    return resultMatrix


if __name__ == '__main__':
    print pairwise2.align.globalmx("ALSEAFGAGGTSYGKLT", "IVWNNDMR", 0, 1, score_only=True)
    print pairwise2.align.localmx("ALSEAFGAGGTSYGKLT", "IVWNNDMR", 0, 1, score_only=True)
    print levenshteinSimilarity("ALSEAFGAGGTSYGKLT", "IVWNNDMR")
    print jaroSimilarity("ALSEAFGAGGTSYGKLT", "IVWNNDMR")
    print jaroWinklerSimilarity("ALSEAFGAGGTSYGKLT", "IVWNNDMR")
    print hammingDistance("ALSEAFGAGGTSYGKLT", "GGTSYGKLTIVWNNDMR")
    print alignmentScoreBlosum100Distance("ALSEAFGAGGTSYGKLT", "IVWNNDMR")

    print ""
    print ""

    print pairwise2.align.globalmx("ASSLRAGGGDTQY", "ASSLRAGGADTQY", 0, 1, score_only=True)
    print pairwise2.align.localmx("ASSLRAGGGDTQY", "ASSLRAGGADTQY", 0, 1, score_only=True)
    print levenshteinSimilarity("ASSLRAGGGDTQY", "ASSLRAGGADTQY")
    print jaroSimilarity("ASSLRAGGGDTQY", "ASSLRAGGADTQY")
    print jaroWinklerSimilarity("ASSLRAGGGDTQY", "ASSLRAGGADTQY")
    print alignmentScoreBlosum100Distance("ASSLRAGGGDTQY", "ASSLRAGGADTQY")

    print ""
    print ""

    print pairwise2.align.globalmx("ALSTDSWGKLQ", "SVEPARGHEQY", 0, 1, score_only=True)
    print pairwise2.align.localmx("ALSTDSWGKLQ", "SVEPARGHEQY", 0, 1, score_only=True)
    print levenshteinSimilarity("ALSTDSWGKLQ", "SVEPARGHEQY")
    print jaroSimilarity("ALSTDSWGKLQ", "SVEPARGHEQY")
    print jaroWinklerSimilarity("ALSTDSWGKLQ", "SVEPARGHEQY")
    print alignmentScoreBlosum100Distance("ALSTDSWGKLQ", "SVEPARGHEQY")

    print jaroWinklerSimilarity.__name__
