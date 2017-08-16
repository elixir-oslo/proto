#UNTESTED
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.ZipperStat import ZipperStatUnsplittable

class DictZipperStat(MagicStatFactory):
    pass

class DictZipperStatUnsplittable(ZipperStatUnsplittable):
    def _compute(self):
        allDicts = [child.getResult() for child in self._children]
        assert all(type(x)==dict for x in allDicts)
        allItems = reduce(lambda x,y:x+y, [x.items() for x in allDicts])
        zippedDict = dict(allItems)
        assert len(zippedDict) == len(allItems), "Collision of resDictKeys from child stats: " + zip(allItems)[0]
        return zippedDict
    
