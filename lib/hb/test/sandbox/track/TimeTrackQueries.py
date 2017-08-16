
from timeit import Timer

setup = '''
from gold.track.Track import PlainTrack
from gold.track.GenomeRegion import GenomeRegion
from quick.util.GenomeInfo import GenomeInfo
from random import choice, randint
from numpy import array

track = PlainTrack(['Private','Sveinung','Human ESTs'])
#chrList = GenomeInfo().getChrList('hg18')
chrList = ['chr1']
chrLens = dict([(chr,GenomeInfo().getChrLen('hg18', chr)) for chr in chrList])
numIterations = 1000
randChrs = [choice(chrList) for x in xrange(numIterations)]
randStarts = [randint(0, chrLens[randChrs[x]]-1000) for x in xrange(numIterations)]
randEnds = [randStarts[x] + randint(1, 1000) for x in xrange(numIterations)]
'''

expression = '''
for x in xrange(numIterations):
    region = GenomeRegion('hg18',randChrs[x],randStarts[x],randEnds[x])
    #array(track.getTrackView(region, includeSource=True)._sourceList)
    #str(track.getTrackView(region, includeSource=True)._sourceList)
    print str(track.getTrackView(region, includeSource=True)._sourceList)
'''

print Timer(stmt=expression, setup=setup).timeit(1)