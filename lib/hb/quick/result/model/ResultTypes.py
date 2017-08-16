class LinePlotResultType(dict):
    def setXLabel(self, xLabel):
        self._xLabel = xLabel
        
    def setYLabel(self, yLabel):
        self._yLabel = yLabel
        
    def getXLabel(self):
        return self._xLabel if hasattr(self, '_xLabel') else 'X-values'
        
    def getYLabel(self):
        return self._yLabel if hasattr(self, '_yLabel') else 'Y-values'

class GlobalVisualizationResultType:
    def __init__(self, localResults):
        #self._localResults = localResults
        lists = zip(*localResults)
        regs = lists[0]
        if len(set([reg.chr for reg in regs])) == 1:
            #only single chromosome
            self._xList = [reg.start for reg in regs]
        else:
            self._xList = ['%s-%i'%(reg.chr,reg.start) for reg in regs]
        
        self._yLists = lists[1:]
        
    def getXlist(self):
        return self._xList
    
    def getYlists(self):
        return self._yLists
    
class RawVisualizationResultType:
    def __init__(self, localTrackViews):
        self._localTrackViews = localTrackViews
        
    def getAllTrackViews(self):
        return self._localTrackViews
    
#class GlobalVisualizationResultType(dict):
#    def __init__(self, localResults):
#        #self._localResults = localResults
#        lists = zip(*localResults)
#        regs = lists[0]
#        assert len(set([x.chr for x in regs])) == 1, 'for now, only support single chromosome'
#        self['xList'] = [x.start for reg in regs]
#        
#        self['yLists'] = lists[1:]
#        
#    def getXlist(self):
#        return self['xList']
#    
#    def getYlists(self):
#        return self['yLists']

class FunctionDefResultType(object):
    #@takes(str,list)
    def __init__(self, functionText, testTexts):
        self.functionText = functionText
        self.testTexts = testTexts
    
    def __add__(self, other):
        assert self.functionText == other.functionText
        #self.testTexts.append(other.testTexts)
        #return self
        return FunctionDefResultType(self.functionText, self.testTexts+other.testTexts)
    
    def __str__(self):
        text = self.functionText + '\n' + '\n'.join(self.testTexts)
        return text
        #return text.replace('\n','<br>')
        #from proto.hyperbrowser.StaticFile import
