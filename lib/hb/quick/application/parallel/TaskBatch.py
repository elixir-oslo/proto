#Used for bundling large numbers of small tasks into chunks for
#decreased overhead   
class ChunkGenerator(object):
    def __init__(self, iterable, chunkSize):
        self.iterable = iterable
        self.chunkSize = chunkSize
        self.chunk = []
    
    def __iter__(self):
        for item in self.iterable:
            self.chunk.append(item)
            if len(self.chunk) == self.chunkSize:
                yield self.chunk
                self.chunk = []
            
        if len(self.chunk) > 0:
            yield self.chunk
    
class TaskBatch(object):
    def __init__(self, iterable):
        self.iterable = iterable
        
    def __iter__(self):
        for task in self.iterable:
            yield task
    
class TaskBatchListCreator(object):
    def __init__(self, iterable, length=1):
        self.iterable = iterable
        self.length = length
        
    def createList(self):
        taskBatchList = []
        chunkGenerator = ChunkGenerator(self.iterable, self.length)
        for chunk in chunkGenerator:
            taskBatchList.append(TaskBatch(chunk))
            
        return taskBatchList     