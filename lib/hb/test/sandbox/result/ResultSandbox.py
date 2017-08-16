from gold.result.ResultsViewer import ResultsViewerCollection
from gold.application.GalaxyInterface import GalaxyInterface
import cPickle
import functools
import gold.description.Analysis
from quick.application.UserBinSource import MinimalBinSource

gold.description.Analysis.MinimalBinSource = \
    functools.partial(MinimalBinSource, genome='TestGenome')

#res = GalaxyInterface.run(["segsLen1"],["segs"],'Raw -> RawOverlapStat','TestGenome:chr1:1-4001','2000','TestGenome')
#cPickle.dump(res, open('ResultSandbox.pickle','w'))
res = cPickle.load(open('ResultSandbox.pickle'))
print ResultsViewerCollection([res],'/Users/sandve/DATA/__div/tempBaseDir/')
