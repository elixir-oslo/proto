import os
import re
import subprocess
import getpass
import sys

from config.Config import PP_PASSPHRASE, PP_PORT, CLUSTER_ACCOUNTNAME, SBATCH_PATH, CLUSTER_ACCOUNTNAME, DEFAULT_WALLCLOCK_LIMIT_IN_SECONDS, \
DEFAULT_NUMBER_OF_REMOTE_WORKERS, CLUSTER_MEMORY_PER_CORE_IN_MB, CLUSTER_MEMORY_PER_CORE_IN_MB, CLUSTER_CORES_PER_NODE, CLUSTER_SOURCE_CODE_DIRECTORY, \
ONLY_USE_ENTIRE_CLUSTER_NODES

#Wraps SLURM, to allow for the resource manager to change in the future 
class SlurmWrapper(object):
    def __init__(self, jobWorkDirectoryPath, uniqueJobNumber, batchScriptFileName):
        self.workDirectoryPath = jobWorkDirectoryPath
        self.uniqueJobNumber = uniqueJobNumber
        self.batchScriptFileName = batchScriptFileName
    
    def submitBatchJob(self):
        print "Submitting batch job"
        currentWorkingDirectory = os.getcwd()
        os.chdir(self.workDirectoryPath) #otherwise sbatch command tries to change wd to cwd which is
                                            #not mounted on titan
                                            
        if self._userIsCorrectUser():
            command = [SBATCH_PATH, self.batchScriptFileName]
        else:
            command = ["sudo", "-u", CLUSTER_ACCOUNTNAME, SBATCH_PATH, self.batchScriptFileName]
        try:  
            output = subprocess.check_output(command)
            print output
        except subprocess.CalledProcessError:
            print "Submitting job failed:"
            print sys.exc_info()
            raise
        os.chdir(currentWorkingDirectory)
        self.extractSlurmJobNumber(output)
        
    def _userIsCorrectUser(self):
        #This is somewhat cryptic, but is required if running for example tests as another
        #user than the user that should be the only one that runs jobs on the cluster
        return getpass.getuser() == CLUSTER_ACCOUNTNAME
        
    def extractSlurmJobNumber(self, output):
        self.slurmJobNumber = output.split()[-1]
        
    def getJobNumber(self):
        return self.slurmJobNumber    
    
class SlurmBatchScriptBuilder(object):
    def __init__(self, workDirectoryPath, uniqueJobNumber = None):
        if uniqueJobNumber == None:
            #TODO fix unique job number here
            pass
        
        self.batchScript = SlurmBatchScript(workDirectoryPath, uniqueJobNumber)
        
    def setWallclockLimit(self, wallclockLimit):
        self.batchScript.wallclockLimit = wallclockLimit
        
    def setNumberOfRemoteWorkers(self, numberOfRemoteWorkers):
        self.batchScript.numberOfRemoteWorkers = numberOfRemoteWorkers
        
    def setMemoryPerCore(self, memoryPerCore):
        self.batchScript.memoryPerCore = memoryPerCore
        
    def setPort(self, port):
        self.batchScript.communicationPort = port
        
    def buildBatchScript(self):
        self.batchScript.writeBatchScript()
        return self.batchScript.batchScriptFileName
    
class SlurmBatchScript(object):
    def __init__(self, workDirectoryPath, uniqueJobNumber):
        self.workDirectoryPath = workDirectoryPath
        self.uniqueJobNumber = uniqueJobNumber
        self.wallclockLimit = DEFAULT_WALLCLOCK_LIMIT_IN_SECONDS    
        self.numberOfRemoteWorkers = DEFAULT_NUMBER_OF_REMOTE_WORKERS
        self.memoryPerCore = CLUSTER_MEMORY_PER_CORE_IN_MB
        self.communicationPort = PP_PORT
        
    def writeBatchScript(self):
        batchFileName = (self.workDirectoryPath + "/" + "dataset" + self.uniqueJobNumber + ".sh")
        batchFile = open(batchFileName, "w")
        batchFile.write("#!/bin/bash\n#SBATCH --job-name=hyperBrowserJob" + self.uniqueJobNumber + "\n#SBATCH --account=nrr")
        
        #workdir
        batchFile.write("\n#SBATCH --workdir=" + self.workDirectoryPath)
        
        #output path
        batchFile.write("\n#SBATCH --output=" + self.workDirectoryPath + "/slurm_%j.out")
        
        #wallclock limit
        batchFile.write("\n#SBATCH --time=" + self._convertNumberOfSecondsToSlurmTimeFormat(self.wallclockLimit))
        
        ntasks = self.numberOfRemoteWorkers
        
        #number of total tasks
        nodes = int(ntasks) / int(CLUSTER_CORES_PER_NODE)
        if nodes == 0:
            nodes = 1
        batchFile.write("\n#SBATCH --nodes=" + str(nodes))
        batchFile.write("\n#SBATCH --ntasks-per-node=1")
        
        #this wastes resources if the number of requested workers is less than
        #CLUSTER_CORES_PER_NODE, but that only really happens for testing,
        #and for testing knowing that the node is reserved is desired
        batchFile.write("\n#SBATCH --cpus-per-task=" + str(CLUSTER_CORES_PER_NODE))
            
        batchFile.write("\n#SBATCH --mem-per-cpu=" + str(self.memoryPerCore)+"M")
        
        #FOR TESTING: only to ensure somewhat consistent results. rack4-rack14 all have 2.2ghz opterons
        batchFile.write("\n#SBATCH --constraint=\"rack4|rack5|rack6|rack7|rack8|rack9|rack10|rack11|rack12|rack13|rack14\"")
        
        #required to start a job; imports things like the module command and prepares the job
        batchFile.write("\nsource /site/bin/jobsetup")
        
        #a path to a working copy on a titan-accessible disk is required
        batchFile.write("\nexport PYTHONPATH=$PYTHONPATH:" + CLUSTER_SOURCE_CODE_DIRECTORY)
        
        #copy over input data to local disk on each node
        #batchFile.write("\ncp " + self.workDirectoryPath + "/" + self.argumentPickleFileName + " $SCRATCH")   
        
        #save output data
        batchFile.write("\ncleanup \"$SCRATCH/* " + self.workDirectoryPath + "/\"")
        
        #change to work directory
        batchFile.write("\ncd $SCRATCH")
        #load python module
        batchFile.write("\nmodule load python/2.7.gcc45")
        
        scriptLocation = CLUSTER_SOURCE_CODE_DIRECTORY + "/third_party/pp/ppserver.py"
        
        serverOptions = ""
        #add various command line options
        serverOptions += " -a" #autodiscover job server        
        serverOptions += " -s \""+ PP_PASSPHRASE + "\"" #secret passphrase
        serverOptions += " -w " + (str(self.numberOfRemoteWorkers) if int(self.numberOfRemoteWorkers) < int(CLUSTER_CORES_PER_NODE) else str(CLUSTER_CORES_PER_NODE))
            
        serverOptions += " -d"
        serverOptions += " -p " + str(self.communicationPort) #We use a non-default port
        serverOptions += " -t 3600" #Timeout if no client connections exist
        
            
        batchFile.write("\nsrun " + scriptLocation + serverOptions)
        batchFile.close()
        self.batchScriptFileName = batchFileName
    
    def _convertNumberOfSecondsToSlurmTimeFormat(self, numberOfSeconds):
        if numberOfSeconds <= 0:
            raise ValueError("convertNumberOfSecondsToSlurmTimeFormat: number of seconds should be more than zero")
        
        secondsLeft = numberOfSeconds
        secondsPerHour = 60 * 60
        secondsPerMinute = 60
        
        hours = secondsLeft / secondsPerHour
        secondsLeft -= secondsPerHour * hours
        
        minutes = secondsLeft / secondsPerMinute
        secondsLeft -= secondsPerMinute * minutes
        
        seconds = secondsLeft
        
        return "%02d:%02d:%02d" % (hours, minutes, seconds)        