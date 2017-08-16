from weakref import WeakValueDictionary

w = WeakValueDictionary()

class C(object):
    def test1():
        a = set([10])
        w[10] = a
        return w[10]
    
    #def test2():
        

test()
print len(w)

test()
print len(w)

b=test()
print len(w)
