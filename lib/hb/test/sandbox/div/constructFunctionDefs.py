from quick.result.model.ResultTypes import FunctionDefResultType

#class FunctionDefResultType(object):
#    def __init__(self):
#        self.functionText = None
#        self.testTexts = []
#    
#    def addFunctionDef(self, functionText, testText):
#        if self.functionText is None:
#            self.functionText = functionText
#        else:
#            assert self._functionText == functionText
#            
#        self.testTexts.append(testTexts)

    
def constructFunctionDefWithTest(functionName, paramNames, paramValues, returnValue):
    #kwArgs = ', '.join(['='.join(pair) for pair in zip(paramNames, paramValues)])
    arguments = ', '.join([repr(x) for x in paramValues])
    params = ', '.join(paramNames)
    types = ', '.join([repr(type(x)) for x in paramValues])
    docText = '@takes(%s)' % types
    funcText = 'def %s(%s):\n    #put your code here\n    return yourAnswer\n' % (functionName, params)
    testText = 'assert %s(%s) == %s' % (functionName, arguments, repr(returnValue))
    #return funcText + '\n' + testText
    return FunctionDefResultType(docText+'\n'+funcText, [testText])

#f1 = constructFunctionDefWithTest('myAdder', ['A','B'], [1,2], 3)
#f2 = constructFunctionDefWithTest('myAdder', ['A','B'], [1,3], 4)
#print f1+f2