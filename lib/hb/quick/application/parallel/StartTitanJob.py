from quick.application.parallel.Titan import SlurmBatchScriptBuilder, SlurmWrapper
import sys

class TitanJobScript:
    @staticmethod
    def submitJob(numberOfWorkers=8):
        workDirectory = "/xanadu/project/rrresearch/jonathal/titanRuns/shared"
        id = "shared"
        builder = SlurmBatchScriptBuilder(workDirectory, id)
        builder.setNumberOfRemoteWorkers(numberOfWorkers)
        fileName = builder.buildBatchScript()
        slurm = SlurmWrapper(workDirectory, id, fileName)
        slurm.submitBatchJob()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        TitanJobScript.submitJob(sys.argv[1])
    else:
        TitanJobScript.submitJob()

