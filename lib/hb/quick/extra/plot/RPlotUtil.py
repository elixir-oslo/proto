from numpy import float64
'''
Created on Feb 12, 2015

@author: boris
'''

def drawLineplot(plotDataDict, mainTitle, xLabels, maxPercentage, xTitle, yTitle):
    from proto.RSetup import robjects

    matplot = robjects.r.matplot
    cbind = robjects.r.cbind
    matplot(cbind(*plotDataDict.values()), type='b', axes=False, ann=False)
    axis = robjects.r.axis
    axis(1, at=[x + 1 for x in range(len(xLabels))], labels=xLabels, las=2)
    axis(2, at=range(int(maxPercentage) + 2), las=1)
    title = robjects.r.title
    title(main=mainTitle)
    title(xlab=xTitle)
    title(ylab=yTitle)

def drawVioplot(plotDataMatrix, xlabels, mainTitle, 
                xTitle, yTitle, vioplotColor, 
                xAxisAt, xLimMin, xLimMax, xLas, 
                yAxisAt, yLimMin, yLimMax, yLas):
    from proto.RSetup import robjects
    
    convertedData = [robjects.FloatVector(x) for x in plotDataMatrix]
    rplot = robjects.r.plot 
    axis = robjects.r.axis
    from rpy2.robjects.packages import importr
    vioplot = importr("vioplot")
    rplot([1], [1], type='n', xlim=robjects.FloatVector([xLimMin, xLimMax]), ylim=robjects.FloatVector([yLimMin, yLimMax]), 
          axes=False, ann=False)
    vioplot.vioplot(col=vioplotColor, add=True, *convertedData)
    axis(1, at=xAxisAt, labels=xlabels, las=xLas)
    axis(2, at=yAxisAt, las=yLas)
    title = robjects.r.title
    title(main=mainTitle)
    title(xlab=xTitle)
    title(ylab=yTitle)

    

def dataIntoBins(xData, yData, xLimMax, bins):
    from numpy import ceil
    dataBinnedDict = dict()
    binSize = xLimMax / bins
    for x, y in zip(xData, yData):
        binVal = ceil(x / binSize) * binSize
        if not binVal in dataBinnedDict:
            dataBinnedDict[binVal] = []
        dataBinnedDict[binVal].append(y)
    
    return dataBinnedDict


def drawSmoothedLinePlot(xData, yData, colors, smoothingParameter, displayPoints):
    from proto.RSetup import robjects

    smoothSpline = robjects.r['smooth.spline']
    lines = robjects.r.lines
    sl = smoothSpline(xData, yData, spar=smoothingParameter)
    lines(sl, col=colors)
    if displayPoints:
        points = robjects.r.points
        points(xData, yData, col=colors)

def drawBinnedSmoothedLinePlot(xData, yData, col, bins=20, xLimMax = 100, displayPoints=False, spar=0.6):
    from numpy import mean
    dataBinnedDict = dataIntoBins(xData, yData, xLimMax, bins)
    
    xBinnedData = []
    yBinnedData = []
    for x in sorted(dataBinnedDict.keys()):
        xBinnedData.append(x)
        yBinnedData.append(mean(dataBinnedDict[x], dtype=float64))
    drawSmoothedLinePlot(xBinnedData, yBinnedData, col, spar, displayPoints)
     


def sortDataByX(xData, yData, descending=False):
    dataDict = dict(zip(xData, yData))
    xSorted = sorted(dataDict.keys(), reverse=descending)
    ySorted = [dataDict[x] for x in xSorted]
    return xSorted, ySorted

def drawMovingAvgSmoothedLinePlot(xData, yData, col, displayPoints=False, spar=0.6):
    from numpy import mean
    xSorted, ySorted = sortDataByX(xData, yData)
     
    xSmoothed = []
    ySmoothed = []
    for i in range(len(xSorted)):
        if i+4 < len(xSorted):
            newX = mean(xSorted[i:i+5], dtype=float64)
             
            newY = mean(ySorted[i:i+5], dtype=float64)
        else: 
            newX = mean(xSorted[i:], dtype=float64)
            newY = mean(ySorted[i:], dtype=float64)
        xSmoothed.append(newX)
        ySmoothed.append(newY)
        
    drawSmoothedLinePlot(xSmoothed, ySmoothed, col, spar, displayPoints)


def drawHeatmap(heatmapPlotData, rowLabels, colLabels, mainTitle, symm=True):
    """heatmapPlotData is a matrix represented by a list of lists"""
    from proto.RSetup import robjects

    from numpy import matrix
    heatmap = robjects.r.heatmap
    rmatrix = robjects.r.matrix
    flatData = matrix(heatmapPlotData).flatten().tolist()[0]
    data = robjects.FloatVector(flatData)
    heatmap(rmatrix(data, nrow=len(rowLabels)), labRow=rowLabels, labCol=colLabels, main=mainTitle, symm=symm)
    
def getRainbowColors(nrColors):
    from proto.RSetup import robjects

    rainbow = robjects.r.rainbow
    colors = rainbow(nrColors)
    return colors

def drawHistogram(data, mainTitle, xTitle, yTitle, xLim, yLim=None, color='cadetblue2'):
    from proto.RSetup import robjects

    hist = robjects.r.hist
    if yLim:
        hist(robjects.FloatVector(data), main=mainTitle, xlab=xTitle, ylab=yTitle, 
             xlim=robjects.FloatVector(xLim), ylim = robjects.FloatVector(yLim), col=color)
    else:
        hist(robjects.FloatVector(data), main=mainTitle, xlab=xTitle, ylab=yTitle, 
             xlim=robjects.FloatVector(xLim), col=color)

def drawMultiHistogram(data, mainTitle, xTitle, yTitle, names=None, colors=None, hasLegend = False):
    from proto.RSetup import robjects

    from rpy2.robjects.packages import importr
    plotrix = importr('plotrix')
    multhist = plotrix.multhist
    
    legend = robjects.r.legend

    plotData = [robjects.FloatVector(x) for x in data]
    multhist(plotData, col=colors, main=mainTitle, beside=True, xlab=xTitle, ylab=yTitle)   
    if hasLegend:
        legend('topleft', legend=names, pch=15, col=colors, bty='n')


def drawVerticalLine(verticalLine):
    from proto.RSetup import robjects

    abline = robjects.r.abline
    abline(v=verticalLine)


def drawBarplot(data, mainTitle, xTitle, yTitle, names, col):
    from proto.RSetup import robjects

    barplot = robjects.r.barplot
    barplot(robjects.FloatVector(data), main=mainTitle, xlab=xTitle, ylab=yTitle,
             names = names, col=col)

def drawXYPlot(xData, yData, plotType, xLim, yLim, mainTitle, xTitle, yTitle):
    from proto.RSetup import robjects

    rPlot = robjects.r.plot
    rPlot(xData, yData, type=plotType, xlim=robjects.FloatVector(xLim), ylim=robjects.FloatVector(yLim), 
          main = mainTitle, xlab=xTitle, ylab=yTitle)
    
def addNoiseUniform(data, noise):
    from random import uniform
    for i in range(len(data)):
        data[i] = data[i] + uniform(-noise, noise)
        
def drawEmptyPlot(xTitle, yTitle, mainTitle, xLim, yLim):
    drawXYPlot([1], [1], 'n', xLim, yLim, mainTitle, xTitle, yTitle)

def drawLegend(position, names, colors):
    from proto.RSetup import robjects

    legend = robjects.r.legend
    legend(position, legend=names, lty=1, col=colors, bty='n', cex=0.75)

def rDevOff():
    from proto.RSetup import r
    r('dev.off()')
