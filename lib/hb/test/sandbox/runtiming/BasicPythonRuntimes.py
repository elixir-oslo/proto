from timeit import Timer
from time import sleep
import gc
import copy

def doTiming(title, setup, expressions, numIterations=int(1e6)):
    print title + ':'
    for expr in expressions:
        print '\t', expr[0]+': ', Timer(stmt=expr[1], setup=setup).timeit(numIterations)
    print

def template():
    title = 'Template'

    setup = '''
pass
    '''

    expressions =  [['Test 1', 'pass'],\
                    ['Test 2', 'pass']]

    doTiming(title, setup, expressions)

def objects():
    title = 'Objects'

    setup = '''
class A:
    pass

class B(object):
    pass

class C(object):
    def a():
        return 1
        
    def b():
        return 2
        
    def c():
        return 3
        
    def d():
        return 4
        
    def e():
        return 5
        
class D(object):
    def __init__(self, a):
        self.a = a

class E(object):
    def __init__(self, a,b,c,d,e):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e

class F(object):
    def __init__(self, **kwArgs):
        self.args = kwArgs
        
class G(object):
    def a(self):
        pass

class H(object):
    def a(self):
        pass
        
    def b(self):
        pass
        
    def c(self):
        pass
        
    def d(self):
        pass
        
    def e(self):
        pass

obj_d = D({1:1})
obj_e = E({1:1},None,None,None,None)
obj_g = G()
obj_h = H()
    '''

    expressions =  [['Create empty object (oldstyle)', 'a = A()'],\
                    ['Create empty object (newstyle)', 'b = B()'],\
                    ['Create object (5 methods)', 'c = C()'],\
                    ['Create object (1 arg)', 'd = D(5)'],\
                    ['Create object (5 args)', 'e = E(1,2,3,4,5)'],\
                    ['Create object (5 kwArgs)', 'f = F(a=1, b=2, c=3, d=4, e=5)'],
                    ['Member access (1 member)', 'obj_d.a'],
                    ['Member access (5 members)', 'obj_e.a'],
                    ['Member dict access (1 member)', 'obj_d.a[1]'],
                    ['Member dict access (5 members)', 'obj_e.a[1]'],
                    ['Method call (1 member)', 'obj_g.a()'],
                    ['Method call (5 members)', 'obj_h.a()']]

    doTiming(title, setup, expressions)
###################################Dictionaries##################################################
def dicts():
    title = 'Dictionaries'
#why three '?
    setup = '''
from copy import copy
from collections import OrderedDict
d = dict((x,y) for x,y in enumerate(range(20,1,-1)))
o = OrderedDict((x,y) for x,y in enumerate(range(20,1,-1)))
l = range(0,20,2)
    '''

    expressions =  [['Create empty dict', 'a = {}'],\
                    ['Create empty OrderedDict', 'a = OrderedDict()'],\
                    ['Access dict, d[key]', 'd[10]'],\
                    ['Access OrderedDict, o[key]', 'o[10]'],\
                    ['Access dict, d.get(key)', 'd.get(10)'],\
                    ['Access OrderedDict, o.get(key)', 'o.get(10)'],\
                    ['Access dict, key in d', '10 in d'],\
                    ['Access OrderedDict, key in o', '10 in o'],\
                    #['key in d, key in d', 'for k, v in d.items():'],\ #why does it hang here?
                    ['Keys of dict, d.keys()', 'd.keys()'],\
                    ['Keys of OrderedDict, o.keys()', 'o.keys()'],\
                    ['Values of dict, d.values()', 'd.values()'],\
                    ['Values of OrderedDict, o.values()', 'o.values()'],\
                    ['Items of dict, d.items()', 'd.items()'],\
                    ['Items of OrderedDict, o.items()', 'o.items()'],\
                    ['Copy of dict, copy(d)', 'copy(d)'],\
                    ['Copy of dict, dict(d)', 'dict(d)'],\
                    ['Copy of OrderedDict, copy(o)', 'copy(o)'],\
                    ['Copy of OrderedDict, OrderedDict(o)', 'OrderedDict(o)'],\
                    ['Dict subset, a = dict((x,d[x]) for x in l)', 'a = dict((x,d[x]) for x in l)'],\
                    ['OrderedDict subset, a = OrderedDict((x,o[x]) for x in l)', 'a = OrderedDict((x,o[x]) for x in l)'],\
                    ['Dict comprehension, a = {x:d[x] for x in l}', 'a = {x:d[x] for x in l}']
                    ]
    doTiming(title, setup, expressions, int(1e5))
    
###################################ListOperations##################################################
def listOperations():
    title = 'ListOperations'
    setup = '''
from numpy import array
l = list(range(200000,1,-1))
n = array(range(200000,1,-1))
    '''

    expressions =  [['Create empty list', 'a = []'],\
                    ['Create small list', 'a = [1,2,3,4,5,6,7,8,9,10]'],\
                    ['Access list, l[index]', 'l[10]'],\
                    ['Create empty numpy array', 'a = array([])'],\
                    ['Access numpy array, a[index]', 'n[10]']\
                    ]
    doTiming(title, setup, expressions)

###################################TupleOperations##################################################
def tupleOperations():
    title = 'TupleOperations'
    setup = '''
from numpy import array
t = tuple(range(200000,1,-1))
n = array(range(200000,1,-1))
    '''

    expressions =  [['Create empty tuple', 'a = ()'],\
                    ['Create small tuple', 'a = (1,2,3,4,5,6,7,8,9,10)'],\
                    ['Access tuple, t[index]', 't[10]']\
                    ]
    doTiming(title, setup, expressions)

##########################################ListOperations###########################################
#def listOperations():
#    title = 'Dictionaries'
#
#    setup = '''
#l = [1,5,8]
#    '''
#
#    expressions =  [[]]
###############################################ListIteration#######################################
#def listIteration():
#    title = 'Dictionaries'
#
#    setup = '''
#l = [1,5,8]
#    '''
#
#    expressions =  [[]]
####################################################If##################################
#def testOfIf():
#    title = 'Dictionaries'
#
#    setup = '''
#l = [1,5,8]
#    '''
#
#    expressions =  [[]]
####################################################Basic calls#################################
def basicCalls():
    title = 'Function calls'

    setup = '''
def a(p):
    return p
    '''

    expressions =  [['Method call, 1 param', 'a(5)']]
    doTiming(title, setup, expressions)
    
######################################################Try/except###############################
def tryExcept():
    title = 'Dictionaries'

    setup = '''
l = [1,5,8]
    '''

    expressions =  [[]]
    doTiming(title, setup, expressions)

###################################################### Looping ###############################
def looping():
    title = 'Looping'

    setup = '''
import numpy
loopSize = 10000
a = numpy.arange(loopSize)
d = dict(zip(range(loopSize),range(loopSize)))
    '''

    expressions =  [['for', '''
temp = 0
for i in xrange(loopSize):
    temp+=i
                     '''],\
                    ['for-loop creating list', '''
myList = []
for i in xrange(loopSize):
    myList.append(i)
sum(myList)
                     '''],
                    ['for with if', '''
temp = 0
for i in xrange(loopSize):
    if i%2==0:
        temp+=i
                     '''],
                    ['for with dict', '''
temp = 0
for i in xrange(loopSize):
    temp+=d[i]
                     '''],\
                    ['sum implicit', 'sum(xrange(loopSize))'],
                    ['sum explicit', 'sum(range(loopSize))' ],
                    ['explicit set comprehension', 'sum([i for i in xrange(loopSize)])'],
                    ['implicit set comprehension', 'sum(i for i in xrange(loopSize))'],
                    ['explicit set comprehension with if', 'sum([i for i in xrange(loopSize) if i%2==0])'],
                    ['implicit set comprehension with if', 'sum(i for i in xrange(loopSize) if i%2==0)'],
                    ['set compr with dict','sum(d[i] for i in xrange(loopSize))'],
                    ['set compr with numpy-access','sum(a[i] for i in xrange(loopSize))'],
                    ['sum on numpy','sum(a)'],
                    ['numpy-sum','a.sum()'],
                    ['numpy-if','a[a%2==0].sum()']]

    doTiming(title, setup, expressions, 1000)

def checkMemory(infoInsteadOfEval=False):
    #This will run a series of statements.
    #Between statements the program will give a prompt and sleep to allow the user to check mem usage by e.g. top.
    #The user will put values seen in top back to this script
    smallDict = dict(zip(range(10),range(10)))
    largeDict = dict(zip(range(100),range(100)))
    
    newstyleObjCode = '''
class A(object):
    def __init__(self,i):
        self.i = i
    
temp=[ A(i) for i in xrange(numRepl)]
'''

    oldstyleObjCode = '''
class B:
    def __init__(self,i):
        self.i = i
    
temp=[ B(i) for i in xrange(numRepl)]
'''
    numRepl = 100000
    #list of: [prompt to user while checking mem, numReplication, code, value put in by user while checking mem usage(MB)..]
    promptSetupList = [['Initial mem',0,'pass',2.24],
        ['baseline holder-list',numRepl,'temp=[1]*numRepl',2.64],
        ['unique int',numRepl,'temp=[ i for i in xrange(12345678, 12345678 + numRepl)]',3.8],
        ['lists of 2 el',numRepl,'temp=[ [1]*2 for i in xrange(numRepl)]',7.77],
        ['lists of 10 el',numRepl,'temp=[ [1]*10 for i in xrange(numRepl)]',11],
        ['lists of 100 el',numRepl,'temp=[ [1]*100 for i in xrange(numRepl)]',45],
        ['lists of 1000 el',numRepl,'temp=[ [1]*1000 for i in xrange(numRepl)]',398],
        ['dict of 2 el',numRepl,'temp=[ {1:1, 2:2} for i in xrange(numRepl)]',16],
        ['dict of 10 el',numRepl,'temp=[ copy.copy(smallDict) for i in xrange(numRepl)]',53],
        ['dict of 100 el',numRepl,'temp=[ copy.copy(largeDict) for i in xrange(numRepl)]',310],
        ['minimal new-style object',numRepl,newstyleObjCode,21],
        ['minimal old-style object',numRepl,oldstyleObjCode,22],
        #[,],
        ]
    
    if infoInsteadOfEval:
        for prompt,numReplications,code,userVal in promptSetupList[1:]:
            print prompt,'(KB) : ', '%.3f' % (1000.0*(userVal-promptSetupList[0][-1])/numReplications)
    else:
        for prompt,numReplications,code,userVal in promptSetupList:
            exec(code)
            print prompt,
            sleep(8)
            print '..OK..'
            temp=None
            gc.collect()
            sleep(5)
        
objects()
dicts()
listOperations()
tupleOperations()
basicCalls()
looping()
checkMemory(True)

#Objects:
#        Create empty object (oldstyle):  0.188121080399
#        Create empty object (newstyle):  0.118880033493
#        Create object (5 methods):  0.11452794075
#        Create object (1 arg):  0.4612429142
#        Create object (5 args):  0.898408174515
#        Create object (5 kwArgs):  1.16548013687
#        Member access (1 member):  0.0624980926514
#        Member access (5 members):  0.0624561309814
#        Member dict access (1 member):  0.111968994141
#        Member dict access (5 members):  0.110795021057
#        Method call (1 member):  0.173436164856
#        Method call (5 members):  0.178912878036
#
#Dictionaries:
#        Create empty dict:  0.0434610843658
#        Access dict, d[key]:  0.0768129825592
#        Access dict, d.get(key):  0.139780044556
#        Access dict, d.keys():  0.288527011871
#        Access dict, d.values():  0.281654119492
#        Access dict, d.items():  0.862854003906
#
#ListOperations:
#        Create empty list:  0.0457820892334
#        Access list, l[index]:  0.0479121208191
#        Create empty numpy array:  6.65299797058
#        Access numpy array, a[index]:  0.156456947327
#
#Function calls:
#        Method call, 1 param:  0.128889799118
#
#Looping:
#        for:  0.737576007843
#        for-loop creating list:  1.16569900513
#        for with if:  1.29890990257
#        for with dict:  1.31846404076
#        sum implicit:  0.137672901154
#        sum explicit:  0.238667011261
#        explicit set comprehension:  0.50581908226
#        implicit set comprehension:  0.721059083939
#        explicit set comprehension with if:  1.16366195679
#        implicit set comprehension with if:  1.26919698715
#        set compr with dict:  1.59137201309
#        set compr with numpy-access:  4.71646213531
#        sum on numpy:  3.84871006012
#        numpy-sum:  0.0117228031158
#        numpy-if:  0.255083084106
#
#baseline holder-list (KB) :  0.004
#unique int (KB) :  0.016
#lists of 2 el (KB) :  0.055
#lists of 10 el (KB) :  0.088
#lists of 100 el (KB) :  0.428
#lists of 1000 el (KB) :  3.958
#dict of 2 el (KB) :  0.138
#dict of 10 el (KB) :  0.508
#dict of 100 el (KB) :  3.078
#minimal new-style object (KB) :  0.188
#minimal old-style object (KB) :  0.198
