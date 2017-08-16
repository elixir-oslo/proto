from multiprocessing.managers import BaseManager
from config.Config import GALAXY_BASE_DIR, PP_PASSPHRASE, PP_MANAGER_PORT, PP_NUMBER_OF_LOCAL_WORKERS
from quick.application.parallel.TaskQueue import TaskQueueReferent
from quick.application.parallel.StartTitanJob import TitanJobScript
import sys
import threading
import time
#import logging
from gold.application.LogSetup import PARALLEL_LOGGER, logMessage
import os

#Over this threshold, ask for more computing power (1.0 = 100% load)
LOAD_THRESHOLD = 0.95

#Delay between asking for more computing power in seconds
JOB_SUBMISSION_WAIT_PERIOD = 1800

existingTaskQueueManager = None
numberOfWorkers = PP_NUMBER_OF_LOCAL_WORKERS
if len(sys.argv) > 1:
    numberOfWorkers = int(sys.argv[1])

class TaskQueueManagerFactory(object):
    @staticmethod
    def getTaskQueueManager():                
        import sys
        thisModule = sys.modules[__name__]    
        if thisModule.existingTaskQueueManager is None:    
            thisModule.existingTaskQueueManager = TaskQueueReferent("shared", numberOfWorkers)
            
        return thisModule.existingTaskQueueManager
        
def shutdown():
    TaskQueueManagerFactory.getTaskQueueManager().destroy()
    import sys
    thisModule = sys.modules[__name__]    
    thisModule.existingTaskQueueManager = None


def monitor_load():
    taskQueueManager = TaskQueueManagerFactory.getTaskQueueManager()
    nextPossibleJobRequestTime = time.time()
    while True:        
        loadAverage = taskQueueManager.getLoadAverage()
        #logging.getLogger(PARALLEL_LOGGER).debug("load average is %f", loadAverage)
        #logMessage("load average is %f" % loadAverage, level=5, logger=PARALLEL_LOGGER)
        if loadAverage > LOAD_THRESHOLD:
            if time.time() > nextPossibleJobRequestTime:
                #logging.getLogger(PARALLEL_LOGGER).debug("load over threshold, submitting titan job")
                logMessage("load over threshold, submitting titan job", level=5, logger=PARALLEL_LOGGER)
                nextPossibleJobRequestTime = time.time() + JOB_SUBMISSION_WAIT_PERIOD
                TitanJobScript.submitJob()
        time.sleep(5)

class MyManager(BaseManager):
    pass

pid = os.getpid()

pidFileName = GALAXY_BASE_DIR + "/taskQueue.pid"

with open(pidFileName, "w") as f:
    f.write(str(pid))

MyManager.register("TaskQueueReferent", TaskQueueManagerFactory.getTaskQueueManager)
MyManager.register("shutdown", shutdown)

loadThread = threading.Thread(target=monitor_load)
loadThread.daemon = True
loadThread.start()

manager = MyManager(address=("", PP_MANAGER_PORT), authkey=PP_PASSPHRASE)
server = manager.get_server()

#logging.getLogger(PARALLEL_LOGGER).debug("Task queue started, serving forever...")
logMessage("Task queue started, serving forever...", level=5, logger=PARALLEL_LOGGER)
server.serve_forever()
