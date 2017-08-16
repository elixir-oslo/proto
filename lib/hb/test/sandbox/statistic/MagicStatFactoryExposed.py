from weakref import WeakValueDictionary

class Computation():
    weakDict = WeakValueDictionary()
    
    def __new__(self, *args, **kwArgs):
        key = self.createHash(args, kwArgs)
        if not key in self.weakDict:
            self.weakDict[key] = self.__class__(*args, **kwArgs)
        return self.weakDict[key]
        
    def getResult(self):
        if self._result is None:
            self._result = self._compute()
        return self._result
    
class Data():
    def __init__(self, dataId):
        self._dataId = dataId

    def _compute(self):
        return DataCollection.getData(self._dataId)
        
class Mean():
    def __init__(self, dataId):
        self._dataId = dataId
        
    def _compute(self):
        data = Data(self._dataId).getResult()
        return data.mean()
        
class Variance():
    def __init__(self, dataId):
        self._dataId = dataId
        
    def _compute(self):
        mean = Mean(self._dataId).getResult()
        meanSquares = MeanSquares(self._dataId).getResult()
        return meanSquares - mean**2
        