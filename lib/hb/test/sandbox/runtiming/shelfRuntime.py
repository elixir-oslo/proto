import shelve
import copy
from cPickle import dump, load

def createS():
    s = shelve.open('slett','c')
    for i in xrange(100000):
        s[str(i)] = i*3    
    print len(s.keys())
    s.close()

def createS2():
    s = shelve.open('slett','c')
    s2 = {}
    for i in xrange(100000):
        s2[str(i)] = i*3        
    print len(s2.keys())
    s.update(s2)
    s.close()
    
def createSpickle():
    #s = open('slett','c')
    s2 = {}
    for i in xrange(100000):
        s2[str(i)] = i*3        
    print len(s2.keys())
    dump(s2,open('slett.pickle','w'))
    #s.close()
    
def loadS1():
    s = shelve.open('slett','r')
    for i in xrange(100000):
        temp = s[str(i)]+1
    s.close()

def loadS2():
    s = shelve.open('slett','r')
    #s2 = dict(s.items())
    s2 = {}
    s2.update(s)
    #s.close()
    print 'mid..'
    for i in xrange(100000):
        temp = s[str(i)]+1
    
def loadPickle():
    s = load(open('slett.pickle'))
    for i in xrange(100000):
        temp = s[str(i)]+1
    #s.close()

print 'starting'
#createSpickle()
loadPickle()
#loadS2()
print 'finished'
