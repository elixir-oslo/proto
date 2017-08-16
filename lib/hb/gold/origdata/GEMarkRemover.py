from gold.origdata.GEFilter import GEFilter

class GEMarkRemover(GEFilter):
    def __init__(self, geSource):
        GEFilter.__init__(self, geSource)

    def next(self):
        nextEl = self._geIter.next().getCopy()
        nextEl.val = None
        return nextEl

    def getValDataType(self):
        return None
