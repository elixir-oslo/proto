import time
from quick.application.parallel.TaskQueue import TaskQueueFactory
from quick.application.parallel.JobWrapper import JobWrapperHelper

class JobHandler(object):
    def __init__(self, uniqueId, useSharedTaskQueue=True, restrictions=[]):
        self.uniqueId = uniqueId
        self.taskQueue = TaskQueueFactory.getTaskQueue(uniqueId, useSharedTaskQueue)
        self.restrictions = restrictions
        
    def run(self, jobWrapper):
        self.startTime = time.time()
        self._distributeTasks(jobWrapper)
        results = self._getResults(jobWrapper)
        
        print("<br/>Got results from worker, took %f seconds from submitting<br/>" % (time.time() - self.startTime))   
        
        return results  
    
    def _distributeTasks(self, jobWrapper):
        helper = JobWrapperHelper()
        
        for task in jobWrapper:
            self.taskQueue.submit(task, self.restrictions, helper.getFullyQualifiedTaskWrapperClassName(jobWrapper), helper.getConfigSettings(jobWrapper))
            
    def _getResults(self, jobWrapper):
        try:
            while True:
                result = self.taskQueue.getResult(self.uniqueId)
                jobWrapper.handleResult(result)     
        except StopIteration:
            pass           
        
        return jobWrapper.handleResults()