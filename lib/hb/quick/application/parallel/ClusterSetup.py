import signal
import resource

from config.Config import CLUSTER_MEMORY_LIMIT

class WorkerTerminatedError(Exception):
    pass

def sigTermHandler(signum, frame):
    raise WorkerTerminatedError("WorkerTerminatedError: Worker process received SIGTERM signal. Check logs for more information.")

class ClusterSetup(object):
    def __init__(self):
        pass
    
    def registerSignalHandlers(self):
        signal.signal(signal.SIGTERM, sigTermHandler)
        
    def registerResourceLimits(self):
        memoryLimit = (int(CLUSTER_MEMORY_LIMIT) - 1) * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (memoryLimit - 1, memoryLimit))