from third_party.decorator import decorator
#from decorator import decorator
import collections
import signal
import functools
import pickle
from os.path import isfile

@decorator
def obsoleteHbFunction(func, *args, **kwArgs):
    print 'Warning, this function is going to be phased out of the HB codebase..'
    return func(*args, **kwArgs)


PICKLE_PATH = '/Users/trengere/Documents/pFile.txt'
@decorator
def cachePickleParams(f, *args, **kwArgs):
    paramDict = {}
    if isfile(PICKLE_PATH):
        with open(PICKLE_PATH) as fileObj:
            paramDict = pickle.load(fileObj)
            
    paramDict[args] = [f.__name__, kwArgs]
    with open(PICKLE_PATH, 'w') as fileObj:    
        pickle.dump(paramDict, fileObj)
    
    print args, kwArgs
    f(*args)
    print "After f(*args)"
    #return wrapped_f

#When a function runs with the same arguments, it will return the result from the cache, not having to calculate the result an additional time.
def memoize(func):
    cache = {}
    @functools.wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper


class countcalls(object):
   "Decorator that keeps track of the number of times a function is called."

   __instances = {}

   def __init__(self, f):
      self.__f = f
      self.__numcalls = 0
      countcalls.__instances[f] = self

   def __call__(self, *args, **kwargs):
      self.__numcalls += 1
      return self.__f(*args, **kwargs)

   def count(self):
      "Return the number of times the function f was called."
      return countcalls.__instances[self.__f].__numcalls

   @staticmethod
   def counts():
      "Return a dict of {function: # of calls} for all registered functions."
      return dict([(f.__name__, countcalls.__instances[f].__numcalls) for f in countcalls.__instances])

#@countcalls
#def f():
#   print 'f called
#f()
#f()
#print f.count() # prints 3


##### Function Timeout #####



class TimeoutError(Exception): pass

def timeout(seconds, error_message = 'Function call timed out'):
    def decorated(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return functools.wraps(func)(wrapper)

    return decorated

@cachePickleParams
def sayHello(a1, a2, a3, a4):
    print 'sayHello arguments:', a1, a2, a3, a4
    
