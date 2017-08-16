import os
import os.path
import cPickle
import fcntl
from fcntl import LOCK_SH, LOCK_EX, LOCK_UN, LOCK_NB
from gold.util.CustomExceptions import ShouldNotOccurError

class DiskMirroredDict(dict):
    def __new__(cls, fn):
        if os.path.exists(fn):
            return cPickle.load( open(fn) )
        else:
            return dict.__new__(cls)

    def __init__(self, fn):
        self._fn = fn
        self._dirty = False
        dict.__init__(self)

    def update(self, other):
        self._dirty = True
        return dict.update(self, other)

    def __setitem__(self, key, value):
        self._dirty = True
        return dict.__setitem__(self, key, value)

    def close(self):
        if self._dirty:
            cPickle.dump( self, open(self._fn, 'w'))
            self._dirty = False

    #def __del__(self):
        #as del is not always safe, make sure to instead call close manually..
        #self.close()

class SafeDiskMirroredDict(DiskMirroredDict):
    def __init__(self, fn, flag='r', block=False, lckfilename=None):
        if lckfilename == None:
            lckfilename = os.path.dirname(fn) + os.sep + '.' + os.path.basename(fn) + '.lck'
        old_umask = os.umask(000) #as os.umask returns previous umask..

        self._flag = flag
        self._block = block
        self._lckfilename=lckfilename
        os.umask(old_umask)

        self._acquireLock()
        self._isClosed = False

        DiskMirroredDict.__init__(self, fn)

    def _acquireLock(self):
        if self._flag == 'r':
            lockflags = LOCK_SH
        else:
            lockflags = LOCK_EX
        if not self._block:
            lockflags |= LOCK_NB

        #os.open with os.O_SHLOCK instead?
        lckfile = open(self._lckfilename, 'w')
        fcntl.flock(lckfile.fileno(), lockflags)
        self._lckfile = lckfile

    def _releaseLock(self):
        fcntl.flock(self._lckfile.fileno(), LOCK_UN)
        self._lckfile.close()
        del self._lckfile

    def close(self):
        if not hasattr(self, '_lckfile'): #to avoid closing lckfile multiple times..
            raise ShouldNotOccurError

        if self._dirty:
            if self._flag == 'r':
                #must try to upgrade lock..
                self._releaseLock()
                self._flag = 'w'
                self._acquireLock()

            lckfile = self._lckfile
            del self._lckfile #as open files cannot be pickled
            DiskMirroredDict.close(self)
            self._lckfile = lckfile

        self._releaseLock()
