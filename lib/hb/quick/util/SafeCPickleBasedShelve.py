import os, fcntl, new
import __builtin__
from fcntl import LOCK_SH, LOCK_EX, LOCK_UN, LOCK_NB
import cPickle

class picklingDict(dict):
    pass

def _close(self):
    #shelve.Shelf.close(self)
    lckfile = self.lckfile
    del self.lckfile
    del self.close
    if self._filename != None: # is none when they was read..
        cPickle.dump(self, __builtin__.open(self._filename,'w') )
    
    fcntl.flock(lckfile.fileno(), LOCK_UN)
    lckfile.close()

def open(filename, flag='c', block=True, lckfilename=None):
    """Open the shelve file, creating a lockfile at '.filename.lck'.  If 
    block is False then a IOError will be raised if the lock cannot
    be acquired."""
    if lckfilename == None:
        lckfilename = os.path.dirname(filename) + os.sep + '.' + os.path.basename(filename) + '.lck'
#        print filename, lckfilename
        old_umask = os.umask(000)
        lckfile = __builtin__.open(lckfilename, 'w')
        os.umask(old_umask)

    # Accquire the lock
    if flag == 'r':
    	lockflags = LOCK_SH
    else:
    	lockflags = LOCK_EX
    if not block:
        lockflags |= LOCK_NB
    fcntl.flock(lckfile.fileno(), lockflags)

    # Open the shelf
    #shelf = shelve.open(filename, flag, protocol, writeback)
    if flag == 'r':
        shelf = cPickle.load(__builtin__.open(filename,'r'))
        shelf._filename = None
    else:
        shelf = picklingDict()
        shelf._filename = filename
        

    # Override close 
    shelf.close = new.instancemethod(_close, shelf, dict)
    shelf.lckfile = lckfile 

    # And return it
    return shelf
