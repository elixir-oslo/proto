from numpy import float64
'''
Created on Jan 16, 2015

@author: boris
'''
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from collections import OrderedDict
from quick.extra.plot import RPlotUtil

class ExamResultsAnalysis(object):
    '''
    Abstract class. Inheritted by all other analysis classes.
    '''
    
    GRADES = ['A', 'B', 'C', 'D', 'E', 'F']
    COLORS = ['forestgreen', 'blue', 'blueviolet', 'darkgoldenrod', 'magenta', 'red']

    COL_STUDENT_NR = 'Student nr'
    COL_GRADE = 'Grade'
    COL_GENDER = 'Gender'
    COL_TOTAL_SCORE = 'Total score'
    COL_STUDENT_PROGRAM = 'Student program'
    COL_STUDENT_FEATURE = 'Student feature'
    
    REQUIRED_COLUMNS = [COL_STUDENT_NR, COL_GRADE]
    OPTIONAL_COLUMNS = [COL_GENDER, COL_TOTAL_SCORE, COL_STUDENT_PROGRAM, COL_STUDENT_FEATURE]

    def __init__(self, resultsFileName, galaxyFN):
        '''
        Constructor
        '''
        self._examResults = ExamResultsReader.run(resultsFileName, 
                                                  requiredAttrs=self.REQUIRED_COLUMNS, 
                                                  optionalAttrs=self.OPTIONAL_COLUMNS)
        self._galaxyFN = galaxyFN
        self._plotUrls = []
        self._plotPaths = []
        self._tables = []
        
    def run(self, **kwargs):
        pass
    
    def getPlotUrls(self):
        return self._plotUrls
    
    def getPlotPaths(self):
        return self._plotPaths
    
    def getExamResults(self):
        return self._examResults
    
    def getTables(self):
        return self._tables
    
    def getTaskScoresPerGradeRawData(self, taskScoreData, studentsData):
        rawDataDict = OrderedDict()
        for grade in self.GRADES:
            rawDataDict[grade] = OrderedDict()
            for task in taskScoreData:
                rawDataDict[grade][task.getName()] = []
        
        for student in studentsData:
            grade = student.getAttribute(self.COL_GRADE)
            if grade is None:
                raise MissingColumnException('Missing column %r in the exam results data file (case sensitive)' % self.COL_GRADE)
            if grade not in self.GRADES:
                raise InvalidDataException('Invalid data for column %r. One of %r required.' % (self.COL_GRADE, str(self.GRADES)))
            for task in taskScoreData:
                rawDataDict[grade][task.getName()].append(task.getScore(student.getStudentNr()))
        
        return rawDataDict
    
    
class TaskScoreOverview(ExamResultsAnalysis):
    

    def addVioplot(self):
        taskScoreData = self._examResults.getTaskListSortedByPercentageScore()
        plotOutput = GalaxyRunSpecificFile(['TaskScoreOverview', 'vioplot.png'], self._galaxyFN)
        plotOutput.openRFigure()
        rawData = [x.getPercentScoresList() for x in taskScoreData]
        xlabels = [x.getName() for x in taskScoreData]
        mainTitle = 'Vioplot of task scores overview'
        xTitle = 'Task'
        yTitle = 'Percentage score (from max task score)'
        vioplotColor = 'magenta'
        xAxisAt = [x + 1 for x in range(len(xlabels))]
        xLimMin = 1
        xLimMax = len(xlabels) + 1
        xLas = 2
        yAxisAt = range(0, 100, 20)
        yLimMin = 0
        yLimMax = 100
        yLas = 1
    #plot is used to setup the chart for vioplot so we can control the x and y labels
        RPlotUtil.drawVioplot(rawData, xlabels, mainTitle, xTitle, yTitle, vioplotColor, xAxisAt, xLimMin, xLimMax, xLas, yAxisAt, yLimMin, yLimMax, yLas)
        RPlotUtil.rDevOff()
        self._plotUrls.append(plotOutput.getURL())
        self._plotPaths.append(plotOutput.getDiskPath())


    def addResultsTable(self):
        studentList = self._examResults.getStudentList()
        examMaxScore = self._examResults.getExamMaxScore()
        resultsTable = OrderedDict()
        studentSize = len(studentList)
        resultsTable['Number of students'] = studentSize
        tasks = self._examResults.getTaskList()
        taskSize = len(tasks)
        resultsTable['Number of tasks'] = taskSize
        resultsTable['Maximum exam score'] = examMaxScore
        taskMaxScores = []
        for t in tasks:
            taskMaxScores.append(t.getName() + ' (' + str(t.getMaxScore()) + ')')
        
        resultsTable['Task name (maximum score)'] = ','.join(taskMaxScores)
        self._tables.append(resultsTable)


    def addGradesHistogram(self):
        plotOutput = GalaxyRunSpecificFile(['TaskScoreOverview', 'histogram2.png'], self._galaxyFN)
        plotOutput.openRFigure()
        dataDict = OrderedDict([(x, 0) for x in ExamResultsAnalysis.GRADES])
        studentList = self._examResults.getStudentList()
        for student in studentList:
            grade = student.getAttribute(ExamResultsAnalysis.COL_GRADE)
            dataDict[grade] += 1
        
        mainTitle = 'Histogram of grades'
        xTitle = ''
        yTitle = ''
        names = ExamResultsAnalysis.GRADES
        RPlotUtil.drawBarplot(dataDict.values(), mainTitle, xTitle, yTitle, names, col='blue')
        RPlotUtil.rDevOff()
        self._plotUrls.append(plotOutput.getURL())
        self._plotPaths.append(plotOutput.getDiskPath())


    def addExamScoresHistogram(self):
        studentList = self._examResults.getStudentList()
        examMaxScore = self._examResults.getExamMaxScore()
        data = [self._examResults.getExamScoreForStudent(x.getStudentNr()) for x in studentList]
        plotOutput = GalaxyRunSpecificFile(['TaskScoreOverview', 'histogram1.png'], self._galaxyFN)
        plotOutput.openRFigure()
        mainTitle = 'Histogram of total scores per student'
        xTitle = ''
        yTitle = ''
        xLim = [0, examMaxScore]
        RPlotUtil.drawHistogram(data, mainTitle, xTitle, yTitle, xLim)
        RPlotUtil.rDevOff()
        self._plotUrls.append(plotOutput.getURL())
        self._plotPaths.append(plotOutput.getDiskPath())

    def run(self):
        
        self.addResultsTable()
        
        self.addExamScoresHistogram()
        
        self.addGradesHistogram()
        
        self.addVioplot()
        
    
        


class IndividualTaskAnalysis(ExamResultsAnalysis):
    '''
    1. Show smoothed plot of average score percentage of selected task as a function of total    
    exam score (task score as y-axis and total exam score in points as x-axis, with smoothed         
    line, one color per selected task) 
    2. For each selected task in separate plot: Show vioplots of task score distribution per final    
    grade, i.e. one vioplot per grade from F to A on x-axis   
    '''
    
    ANALYSIS_BIN_AVG_SMOOTHED_PLOT = 'Smoothed line plot of tasks vs exam scores (bins avg)'
    ANALYSIS_MOVING_AVG_SMOOTHED_PLOT = 'Smoothed line plot of tasks vs exam scores (moving avg)'
    ANALYSIS_SCORE_DISTRIBUTION_PER_GRADE = 'Vioplot of score distribution per grade'
    ANALYSIS_AVG_SCORE_PER_GRADE_LINE_PLOT = 'Line plot of average task scores per grade'
    ANALYSIS_HISTOGRAM_PLOT = 'Histogram of task score distribution'
    SUBTASK_LIST = [
                    ANALYSIS_BIN_AVG_SMOOTHED_PLOT,
                    ANALYSIS_MOVING_AVG_SMOOTHED_PLOT,
                    ANALYSIS_SCORE_DISTRIBUTION_PER_GRADE,
                    ANALYSIS_AVG_SCORE_PER_GRADE_LINE_PLOT,
                    ANALYSIS_HISTOGRAM_PLOT
                    ]





    def run(self, analysis, selectedTasks, **kwargs):
        
        taskScoreData = self._examResults.getTaskList()
        studentsData = self._examResults.getStudentList()
        
        if len(taskScoreData) == 0 or len(studentsData) == 0:
            print 'Empty data'
            return None
        
        examMaxScore = 0.0
        for task in taskScoreData:
            examMaxScore += task.getMaxScore()
            
        rawDataDict = self.getTaskScoresPerGradeRawData(taskScoreData, studentsData)
        if analysis == self.ANALYSIS_AVG_SCORE_PER_GRADE_LINE_PLOT:
            plotDataDict = self.getPlotDataFromRawData(rawDataDict, selectedTasks, examMaxScore)
            maxPercentage = 10
            for taskScores in plotDataDict.values():
                if max(taskScores) > maxPercentage:
                    maxPercentage = max(taskScores)
            plotOutput = GalaxyRunSpecificFile(['IndividualTaskAnalysis', 'lineplot.png'], self._galaxyFN)
            plotOutput.openRFigure(h=600, w=720)  
            xTitle = 'Task'
            yTitle = 'Avg score per grade in percentage from total exam score'
            RPlotUtil.drawLineplot(plotDataDict, analysis, selectedTasks, maxPercentage, xTitle, yTitle)
            RPlotUtil.rDevOff()
            self._plotUrls.append(plotOutput.getURL())
            self._plotPaths.append(plotOutput.getDiskPath())    
            
        elif analysis == self.ANALYSIS_SCORE_DISTRIBUTION_PER_GRADE:
            for taskName in selectedTasks:
                plotOutput = GalaxyRunSpecificFile(['IndividualTaskAnalysis', taskName + '_vioplot.png'], self._galaxyFN)
                plotOutput.openRFigure(h=600, w=720)  
                task = self._examResults.getTask(taskName)
                maxScore = task.getMaxScore()
                plotDataMatrix = []
                for grade in self.GRADES:
                    plotDataMatrix.append(rawDataDict[grade][taskName])
                    
                mainTitle = 'Task: ' + taskName + ' - Vioplot of task scores per grade'
                xTitle = 'Grade'
                yTitle = 'Percentage score (from max task score)'
                vioplotColor = 'magenta'
                xAxisAt = [x + 1 for x in range(len(self.GRADES))]
                xLimMin = 0
                xLimMax = len(self.GRADES) + 1
                xLas = 1
                from math import ceil
                yAxisAt = range(0, int(ceil(maxScore)))
                yLimMin = 0
                yLimMax = maxScore
                yLas = 1
                
                #plot is used to setup the chart for vioplot so we can control the x and y labels
                RPlotUtil.drawVioplot(plotDataMatrix, self.GRADES, mainTitle, xTitle, yTitle, vioplotColor, 
                                 xAxisAt, xLimMin, xLimMax, xLas, yAxisAt, yLimMin, yLimMax, yLas)
                
                RPlotUtil.rDevOff()
                self._plotUrls.append(plotOutput.getURL())
                self._plotPaths.append(plotOutput.getDiskPath())
        elif analysis == self.ANALYSIS_HISTOGRAM_PLOT:
            data = []
            for taskName in selectedTasks:
                task = self._examResults.getTask(taskName)
                data.append(task.getPercentScoresList())
            
            plotOutput = GalaxyRunSpecificFile(['IndividualTaskAnalysis', 'histogram.png'], self._galaxyFN)
            plotOutput.openRFigure(h=600, w=720)  
            
            mainTitle = 'Task scores distribution'
            xTitle = 'Task scores 0%-100%'
            yTitle = 'Score count (per bin)'
            colors = RPlotUtil.getRainbowColors(len(selectedTasks))
            RPlotUtil.drawMultiHistogram(data, mainTitle, xTitle, yTitle, names=selectedTasks, colors=colors, hasLegend=True)
            
            RPlotUtil.rDevOff()
            self._plotUrls.append(plotOutput.getURL())
            self._plotPaths.append(plotOutput.getDiskPath())
            
                
        else:
#         elif analysis == self.ANALYSIS_BIN_AVG_SMOOTHED_PLOT:
            #sanity check
            examMaxScore = self._examResults.getExamMaxScore()
            if examMaxScore == 0:
                raise InvalidDataException('Exam max score must be larger than 0. Most probably no task were defined in the results input file.')
            
            bins = int(kwargs['bins'])
            displayPoints = bool(kwargs['displayPoints'])
            spar = float(kwargs['spar'])
            verticalLines = kwargs['verticalLines']
            
            colors = RPlotUtil.getRainbowColors(len(selectedTasks))
            plotOutput = GalaxyRunSpecificFile(['IndividualTaskAnalysis', 'smoothed_line_plot.png'], self._galaxyFN)
            plotOutput.openRFigure(h=600, w=720)
            xData = []
            students = self._examResults.getStudentList()
            for student in students:
                xData.append(self._examResults.getExamScorePercentageForStudent(student.getStudentNr()))
                
            mainTitle = 'Smoothed line plot - task score vs exam score'
            if analysis == self.ANALYSIS_BIN_AVG_SMOOTHED_PLOT:
                mainTitle += ' (Bin average)'
            else:
                mainTitle += ' (Moving average)'
            xTitle = 'Exam score (%)'
            yTitle = 'Task score (%)'
            xLim = [0,100]
            yLim = [0,100]
            RPlotUtil.drawEmptyPlot(xTitle, yTitle, mainTitle, xLim, yLim)
            RPlotUtil.drawLegend('topleft', selectedTasks, colors)
              
            for taskName, col in zip(selectedTasks, colors):
                task = self._examResults.getTask(taskName)
                yData = []
                for student in students:
                    yData.append(task.getPercentageScore(student.getStudentNr()))
                    
                if analysis == self.ANALYSIS_BIN_AVG_SMOOTHED_PLOT:
                    RPlotUtil.drawBinnedSmoothedLinePlot(xData, yData, col=col, bins=bins, displayPoints=displayPoints, spar=spar)
                else: #analysis == self.ANALYSIS_AVG_SCORE_PER_GRADE_LINE_PLOT
                    RPlotUtil.drawMovingAvgSmoothedLinePlot(xData, yData, col, displayPoints=displayPoints, spar=spar)
            
            if verticalLines:
                for verticalLine in verticalLines:
                    RPlotUtil.drawVerticalLine(verticalLine)
            
            RPlotUtil.rDevOff()
            self._plotUrls.append(plotOutput.getURL())
            self._plotPaths.append(plotOutput.getDiskPath()) 
        
    
    def getPlotDataFromRawData(self, rawDataDict, selectedTasks, examMaxScore):
        from numpy import mean
        plotData = OrderedDict() #Grade -> task scores list (order same as selectedTasks)
        for grade in self.GRADES:
            plotData[grade] = []
        for grade in rawDataDict:
            for taskName in selectedTasks:
                plotData[grade].append(100.0*mean(rawDataDict[grade][taskName], dtype=float64)/examMaxScore)
        return plotData
    



class TaskScatterPlotAnalysis(ExamResultsAnalysis):

    def run(self, selectedTasks, **kwargs):
        
        taskScoreData = self._examResults.getTaskList()
        studentsData = self._examResults.getStudentList()
        
        if len(taskScoreData) == 0 or len(studentsData) == 0:
            print 'Empty data'
            return None
        
        from itertools import combinations
        for t1, t2 in combinations(selectedTasks, 2):
            
            plotOutput = GalaxyRunSpecificFile(['TaskScatterPlotAnalysis', t1 + '_vs_' + t2 + '.png'], self._galaxyFN)
            plotOutput.openRFigure(h=600, w=720)
            
            task1 = self._examResults.getTask(t1)
            task2 = self._examResults.getTask(t2)
            self.drawTaskScatterPlot(task1, task2, noise=0.5)
            
            RPlotUtil.rDevOff()
            self._plotUrls.append(plotOutput.getURL())
            self._plotPaths.append(plotOutput.getDiskPath()) 

    
    
    def drawTaskScatterPlot(self, task1, task2, noise=0.0):
        xData = task1.getPercentScoresList()
        yData = task2.getPercentScoresList()
        if noise > 0.0:
            RPlotUtil.addNoiseUniform(xData, noise)
            RPlotUtil.addNoiseUniform(yData, noise)
        mainTitle = 'Scatter plot for tasks ' + task1.getName() + ' and ' + task2.getName()
        xTitle = task1.getName() + ' score (%)'
        yTitle = task2.getName() + ' score (%)'
        RPlotUtil.drawXYPlot(xData, yData, plotType='p', xLim=[0,100], yLim=[0,100], mainTitle=mainTitle, xTitle=xTitle, yTitle=yTitle)
        
        
class TaskCorrelationAnalysis(ExamResultsAnalysis):
    '''
    Possible to select tasks through checkbox, 
    but usually with all tasks - 
    show a heatmap of pairwise correlations between every task against every other
    '''
    
    
    def run(self, selectedTasks):
        from numpy import corrcoef
        plotOutput = GalaxyRunSpecificFile(['TaskScoreHeatmap', 'heatmap.png'], self._galaxyFN)
        plotOutput.openRFigure(h=600, w=720)
        
        heatmapPlotData = []
        for taskName1 in selectedTasks:
            taskCorrelations = []
            t1 = self._examResults.getTask(taskName1)
            for taskName2 in selectedTasks:
                t2 = self._examResults.getTask(taskName2)
                taskCorrelations.append(corrcoef(t1.getPercentScoresList(), t2.getPercentScoresList())[0][1])
            heatmapPlotData.append(taskCorrelations)
        RPlotUtil.drawHeatmap(heatmapPlotData, selectedTasks, selectedTasks, 'Task correlation heatmap')
        
        RPlotUtil.rDevOff()
        self._plotUrls.append(plotOutput.getURL())
        self._plotPaths.append(plotOutput.getDiskPath())
        
class ExamScoresOverview(ExamResultsAnalysis):
    
    def run(self):
        students = self._examResults.getStudentList()
        examTotalScores = []
        examTotalPercentageScores = []
        for student in students:
            examTotalScores.append(self._examResults.getExamScoreForStudent(student.getStudentNr()))
            examTotalPercentageScores.append(self._examResults.getExamScorePercentageForStudent(student.getStudentNr()))
            
        plotOutput = GalaxyRunSpecificFile(['ExamScoresOverview', 'histogram1.png'], self._galaxyFN)
        plotOutput.openRFigure(h=600, w=720)
        
        examMaxScore = self._examResults.getExamMaxScore()
        mainTitle = 'Exam total scores histogram'
        xTitle = 'Total exam score = %r points' % examMaxScore
        yTitle = 'Students exam score' 
        RPlotUtil.drawHistogram(examTotalScores, mainTitle, xTitle, yTitle, [0,examMaxScore])
        
        RPlotUtil.rDevOff()
        self._plotUrls.append(plotOutput.getURL())
        self._plotPaths.append(plotOutput.getDiskPath())

        
class Task(object):
    def __init__(self, name, maxScore):
        self._name = name
        self._maxScore = maxScore
        self._scores = OrderedDict()
        
    def addScore(self, studentNr, score):
        self._scores[studentNr] = score
        
    def getScore(self, studentNr):
        if studentNr not in self._scores:
            return None
        return self._scores[studentNr]
    
    def getPercentageScore(self, studentNr):
        score = self.getScore(studentNr)
        if score is not None:
            return 100.0*score/self.getMaxScore()
            
        
    def getScores(self):
        return self._scores
    
    def getName(self):
        return self._name
    
    def getMaxScore(self):
        return self._maxScore
    
    def getScoresList(self):
        return self._scores.values()
    
    def getPercentScores(self):
        return OrderedDict([(x,100.0*y/self._maxScore) for x,y in self._scores.iteritems()])
    
    def getPercentScoresList(self):
        return self.getPercentScores().values()
    
    def getAverageScore(self):
        if len(self.getScoresList()) == 0:
            return 0.0
        from numpy import mean
        return mean(self.getScoresList(), dtype=float64)

    def getAveragePercentScore(self):
        if len(self.getPercentScoresList()) == 0:
            return 0.0
        from numpy import mean
        return mean(self.getPercentScoresList(), dtype=float64)
    
class Student(object):
    def __init__(self, studentNr,):
        self._studentNr = studentNr
        self._attributes = dict()
        
    def getStudentNr(self):
        return self._studentNr
    
    def getAttributes(self):
        return self._attributes
    
    def getAttribute(self, attrName):
        if attrName in self._attributes:
            return self._attributes[attrName]
        else:
            return None
    
    def addAttribute(self, attrName, attrVal):
        self._attributes[attrName] = attrVal
        
class ExamResultsReader(object):
    
    @staticmethod
    def run(examResultsFN, requiredAttrs=[], optionalAttrs=[]):
        '''
        Read in the exam results file into a ExamResults object.
        '''
        import csv
        examResults = ExamResults()
        with open(examResultsFN, 'rb') as fin:
            reader = csv.reader(fin)
            attributes = reader.next()
            missingReqAttrs = []
            for reqAttr in requiredAttrs:
                if reqAttr not in attributes:
                    missingReqAttrs.append(reqAttr)
            if missingReqAttrs:
                raise MissingColumnException('There are missing required columns in the results file: %r. NB: Column names are case sensitive.' % missingReqAttrs)
            maxScores = reader.next()
            i=0
            taskCols = []
            nonTaskCols = []
            studentNrCol = -1
            for attrName,maxScore in zip(attributes, maxScores):
                if attrName not in requiredAttrs+optionalAttrs:
                    if maxScore <=0:
                        raise InvalidDataException('Max score for task must be larger than 0.0')
                    if examResults.getTask(attrName) is not None:
                        raise DuplicateColumnException('Duplicate task with name: %r.Task name must be unique' % attrName)
                    task = Task(attrName, float(maxScore))
                    examResults.addTask(attrName, task)
                    taskCols.append(i)
                elif attrName == ExamResultsAnalysis.COL_STUDENT_NR:
                    studentNrCol = i
                else:
                    nonTaskCols.append(i)
                i+=1
                
            if studentNrCol == -1:
                raise MissingColumnException('Required column missing. Input file must contain %r column' % ExamResultsAnalysis.COL_STUDENT_NR)
            for dataRow in reader:
#                 print dataRow
                studentNr = dataRow[studentNrCol]
                student = Student(studentNr)
                for nonTaskCol in nonTaskCols:
                    if attributes[nonTaskCol] is not ExamResultsAnalysis.COL_STUDENT_NR:
                        student.addAttribute(attributes[nonTaskCol], dataRow[nonTaskCol])
                examResults.addStudent(studentNr, student)
                
                for taskCol in taskCols:
                    val = float(dataRow[taskCol])
                    task = examResults.getTask(attributes[taskCol])
                    task.addScore(studentNr, val)
            fin.close()
        return examResults
    
    @staticmethod
    def readTaskNames(examResultsFN, requiredAttrs=[], optionalAttrs=[]):
        import csv
        taskNames = []
        with open(examResultsFN, 'rb') as fin:
            reader = csv.reader(fin)
            attributes = reader.next()
            for attrName in attributes:
                if attrName not in requiredAttrs+optionalAttrs:
                    taskNames.append(attrName)
        return taskNames
    
    @staticmethod
    def readColumnNames(examResultsFN):
        return ExamResultsReader.readTaskNames(examResultsFN, [], [])
    
class ExamResultsValidator(object):
    MISSING_OR_INVALID_MAXIMUM_SCORE_ERROR = '''
    Task score for student must not be larger than the maximum possible score for that task.
    Either the score for the student is erroneous or the exam results data file is missing the required row of maximum score per taks (second row of the file).
    '''
    
    @staticmethod
    def validateExamResultsDataFile(examResultsFN, requiredAttrs=[], optionalAttrs=[]):
        errors = []
        try:
            reader = ExamResultsReader()
            examResults = reader.run(examResultsFN, requiredAttrs, optionalAttrs)
            students = examResults.getStudentList()
            tasks = examResults.getTaskList()
            for student in students:
                totalScore = 0.0
                studentNr = student.getStudentNr()
                for task in tasks:
                    score = task.getScore(studentNr)
                    totalScore += score
                    if task.getMaxScore() < score:
                        descr = ExamResultsValidator.MISSING_OR_INVALID_MAXIMUM_SCORE_ERROR
                        error = ExamResultsDataError(studentNr, task.getName(), score, descr)
                        errors.append(error)
                if ExamResultsAnalysis.COL_TOTAL_SCORE in student.getAttributes():
                    totalScoreActual = float(student.getAttribute(ExamResultsAnalysis.COL_TOTAL_SCORE))
                    if totalScoreActual != totalScore:
                        errors.append('Total score value %r  for student with nr %r in file is wrong, or there are missing tasks. Please repair file to continue with analysis.' % (totalScoreActual, studentNr))
        except Exception as exc:
            errors.insert(0, str(exc))
            return errors
        return errors
        
class ExamResultsDataError(object):
    
    def __init__(self, studentNr, colName, value, description):
        self._studentNr = studentNr
        self._colName = colName
        self._value = value
        self._description = description
        
    def __str__(self):
        errStr = '''
        Error in exam results data:
        \nStudent nr: %r
        \nColumn name: %r
        \nValue: %r
        \n%s
        ''' % (self._studentNr, self._colName, self._value, self._description)
        
        return errStr
            
class ExamResults(object):
    
    def __init__(self):
        self._tasks = OrderedDict()
        self._students = OrderedDict()
        self._examMaxScore = 0.0
        
    def addTask(self, taskName, task):
        self._tasks[taskName] = task
        
    def addStudent(self, studentNr, student):
        if studentNr in self._students:
            raise InvalidDataException('Student with student nr. %r is already present in the student list.\
             Possible duplicate (multiple) rows in the results data file.' % studentNr)
        self._students[studentNr] = student
        
    def getTask(self, taskName):
        if taskName not in self._tasks:
            return None
        return self._tasks[taskName]
    
    def getStudent(self, studentNr):
        if studentNr not in self._students:
            return None
        return self._students[studentNr]
    
    def getStudentList(self):
        return self._students.values()
    
    def getTaskList(self):
        return self._tasks.values()
                
    def getTaskListSorted(self, descending=False):
        taskList = self.getTaskList()
        return sorted(taskList, key = lambda x: x.getAverageScore(), reverse = descending)

    def getTaskListSortedByPercentageScore(self, descending=False):
        taskList = self.getTaskList()
        return sorted(taskList, key = lambda x: x.getAveragePercentScore(), reverse = descending)
    
    def getExamMaxScore(self):
        if len(self._tasks) == 0:
            return 0.0
        if self._examMaxScore == 0:
            self._examMaxScore = sum([x.getMaxScore() for x in self.getTaskList()]) 
        return self._examMaxScore
    
    def getExamScoreForStudent(self, studentNr):
        score = 0.0
        for task in self.getTaskList():
            score += task.getScore(studentNr)
        return score

    
    def getExamScorePercentageForStudent(self, studentNr):
        return 100.0*self.getExamScoreForStudent(studentNr)/self.getExamMaxScore()
    

class InvalidDataException(Exception):
    pass

class MissingColumnException(Exception):
    pass      

class DuplicateColumnException(Exception):
    pass
        
