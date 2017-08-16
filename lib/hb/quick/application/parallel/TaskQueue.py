from quick.application.parallel.Worker import WorkerBootstrapper
import third_party.pp.pp as pp
from quick.util.CommonFunctions import extractIdFromGalaxyFn
from quick.application.parallel.Titan import SlurmWrapper
from multiprocessing.managers import BaseManager

import quick.util.CommonFunctions
from config.Config import PP_NUMBER_OF_LOCAL_WORKERS, PP_PASSPHRASE, PP_PORT, CLUSTER_TEMP_PATH, PP_MANAGER_PORT
from gold.statistic.MagicStatFactory import MagicStatFactory
import threading
from quick.application.parallel.Worker import WorkerBootstrapper

class TaskQueueReferent(object):
    def __init__(self, uniqueId, numberOfWorkers=None):        
        remoteJobServers = ()
        autoDiscover = "*:" + str(PP_PORT)
        remoteJobServers = (autoDiscover,)
            
        if numberOfWorkers == None:
            numberOfWorkers = PP_NUMBER_OF_LOCAL_WORKERS
        self.server = pp.Server(ncpus=numberOfWorkers, ppservers=remoteJobServers, proto=-1, secret=PP_PASSPHRASE)
        
        self.groups = {}
        self.iterators = {}
        self.lock = threading.Lock()
        
    def queueEmpty(self):
        return self.server.queue_empty()
            
    def submit(self, group, restrictions, *task):
        with self.lock:
            if group not in self.groups:
                self.groups[group] = []
                self.iterators[group] = self.groups[group].__iter__()
            
            self.groups[group].append(self.server.submit(*task, group=group, restrictions=restrictions))
        
    def getResult(self, group):
        with self.lock:
            iterator = self.iterators[group]
                       
        try:
            task = iterator.next()
            return task()
        except StopIteration:
            with self.lock:
                del self.groups[group]   
                del self.iterators[group]
                raise                
        except:
            print "Error during task retrieval"
            raise        
    
    def getLoadAverage(self):
        return self.server.get_average_load()
    
    def destroy(self):
        self.server.destroy()
    
    def _startRemoteWorkers(self, uniqueId):
        jobWorkDirectoryPath = self._createJobWorkDirectory(uniqueId)
        slurmWrapper = SlurmWrapper(jobWorkDirectoryPath, uniqueId) #TODO: use a generic batch queue class  
        slurmWrapper.run()
        
    def _createJobWorkDirectory(self, uniqueJobNumber):
        jobWorkDirectoryPath = CLUSTER_TEMP_PATH + "/" + str(uniqueJobNumber)
        os.mkdir(jobWorkDirectoryPath)
        return jobWorkDirectoryPath

class MyManager(BaseManager):
    pass

class ProxyTaskQueue(object):
    def __new__(self, uniqueId):
        MyManager.register("TaskQueueReferent")
        manager = MyManager(address=("", PP_MANAGER_PORT), authkey=PP_PASSPHRASE)
        manager.connect()
        proxy = manager.TaskQueueReferent()
        return proxy
   
# Intended for jobs that for some reason require a non-shared queue, or used
# for debugging - the manager functionality in multiprocessing has severe
# lack of debugging functionality (i.e. it will reraise errors that occured
# in the proxy object, but it will not report _where_ the error occured)
class LocalTaskQueue(TaskQueueReferent):
    pass
    
class TaskQueueFacade(object):
    def __init__(self, uniqueId, queue):
        self.uniqueId = uniqueId
        self.queue = queue
        
    def submit(self, task, restrictions, className, configOptions):
        bootstrapper = WorkerBootstrapper()
        self.queue.submit(self.uniqueId, restrictions, bootstrapper.bootstrap, (task, className, configOptions))
        
    def getResult(self, group):
        return self.queue.getResult(group)
        
existingTaskQueueManager = None
class TaskQueueFactory(object):
    @staticmethod
    def getTaskQueue(uniqueId, useSharedTaskQueue=False):
        import sys
        thisModule = sys.modules[__name__]    
        if thisModule.existingTaskQueueManager is None: 
            if useSharedTaskQueue:
                thisModule.existingTaskQueueManager = ProxyTaskQueue(uniqueId)
            else:
                thisModule.existingTaskQueueManager = LocalTaskQueue(uniqueId)
            
        return TaskQueueFacade(uniqueId, thisModule.existingTaskQueueManager)         
        
        
        