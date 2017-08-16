import sys
IS_WORKER = False   

class WorkerTaskExecutor(object):        
    def getClass(self, fullyQualifiedClassName):
        moduleName, ignore, className = fullyQualifiedClassName.rpartition(".")
        __import__(moduleName)
        module = sys.modules[moduleName]
        cls = getattr(module, className)          
        return cls
    
    def run(self, task, fullyQualifiedWorkerJobWrapperClassName, configSettings, tid):
        taskWrapper = self.getClass(fullyQualifiedWorkerJobWrapperClassName)()
        self.parseConfigSettings(configSettings)
        return taskWrapper.handleTask(task)
       
    def parseConfigSettings(self, configSettings):
        import sys
        for moduleName, classNameDict in configSettings.iteritems():
            for className, settingDict in classNameDict.iteritems():
                __import__(moduleName)
                module = sys.modules[moduleName]
                cls = getattr(module, className)
                for key, value in settingDict.iteritems():
                    setattr(cls, key, value)

#This class is intentionally kept as small as possible to minimize
#source code transferral
class WorkerBootstrapper(object):
    import quick.application.parallel.Worker
    def bootstrap(self, *args):
        import quick.application.parallel.Worker
        quick.application.parallel.Worker.IS_WORKER = True
        taskExecutor = quick.application.parallel.Worker.WorkerTaskExecutor() 
        return taskExecutor.run(*args) 
