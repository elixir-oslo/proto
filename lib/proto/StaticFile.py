from proto.config.Config import GALAXY_BASE_DIR, STATIC_DIR, STATIC_PATH, STATIC_REL_PATH
from proto.CommonFunctions import ensurePathExists, getLoadToGalaxyHistoryURL, \
    extractNameFromDatasetInfo, extractIdFromGalaxyFn, getGalaxyFilesFilename
from proto.HtmlCore import HtmlCore
import os


class StaticFile(object):
    STATIC_DIR = STATIC_DIR
    STATIC_PATH = STATIC_PATH
    STATIC_REL_PATH = STATIC_REL_PATH

    def __init__(self, id):
        #assert id[0] in ['files','images','run_specific'], 'Only a restricted set of first elements of id is supported, in order to have control of phyical storage locations. ID: '+str(id)
        assert id[0] in ['files','images'], 'Only a restricted set of first elements of id is supported, in order to have control of phyical storage locations. ID: '+str(id)
        self._id = id

    def getDiskPath(self, ensurePath=False, relativeToBase=False):
        path = self.STATIC_DIR if relativeToBase else self.STATIC_PATH
        fn = os.sep.join([path] + self._id)
        if ensurePath:
            ensurePathExists(fn)
        return fn

    def getFile(self, mode='w'):
        fn = self.getDiskPath(True)
        return open(fn,mode)

    def fileExists(self):
        return os.path.exists(self.getDiskPath())

    def writeTextToFile(self, text, mode='w'):
        f = self.getFile(mode)
        f.write(text)
        f.close()

    def getURL(self):
        return os.sep.join([self.STATIC_REL_PATH] + self._id)

    def getLink(self, linkText):
        return str(HtmlCore().link(linkText, self.getURL()))
        #return '<a href=%s>%s</a>' % (self.getURL(), linkText)

    def getEmbeddedImage(self):
        return str(HtmlCore().image(self.getURL()))

    def getLoadToHistoryLink(self, linkText, galaxyDataType='bed'):
        return str(HtmlCore().link(linkText,
                                   getLoadToGalaxyHistoryURL
                                   (self.getDiskPath(relativeToBase=True),
                                    galaxyDataType=galaxyDataType)))

    def openRFigure(self, h=600, w=800):
        from proto.RSetup import r
        r.png(filename=self.getDiskPath(True), height=h, width=w, units='px', pointsize=12, res=72)

    def plotRHist(self, vals, breaks, main, saveRawData=True, alsoOpenAndClose=True, **kwArgs):
        from proto.RSetup import r, robjects
        rvals = robjects.FloatVector(vals)
        if type(breaks) in [list,tuple]:
            rbreaks = robjects.FloatVector(breaks)
        else:
            rbreaks = breaks
        if not 'xlab' in kwArgs:
            kwArgs['xlab'] = 'Values'

        if alsoOpenAndClose:
            self.openRFigure()

        histRes = r.hist(rvals, breaks=rbreaks, main=main, **kwArgs )

        if saveRawData:
            rawFn = self.getDiskPath() + '.raw.txt'
            f = open(rawFn,'w')
            f.write('vals <- c(%s)' % ','.join(str(val) for val in vals) + '\n')
            if type(breaks) in [list,tuple]:
                f.write('breaks <- c(%s)' % ','.join(str(b) for b in breaks) + '\n')
            else:
                f.write('breaks <- %s' % breaks)
            f.write('hist(vals, breaks=breaks) \n')
            #r('prn=print')
            intensities = r('function(r){r$intensities}')(histRes)
            f.write('intensities = c(%s)' % ','.join([str(x) for x in intensities]) + '\n')
            f.close()

        if alsoOpenAndClose:
            self.closeRFigure()

    def plotRLines(self, xVals, yLines, saveRawData=True, alsoOpenAndClose=True, colors=None, legend=None, lty=None, **kwArgs):
        '''
        xVals: one list containing x-values
        yLines: list of lists containing y-values
        colors: list of colors to use for each line
        legend: list of legend text per line (color)
        lty: line types for r.legend
        any extra params in kwArgs is sent to r.plot. Use to send for example xlab,ylab
        '''
        from proto.RSetup import r
        numLines = range(len(yLines))

        if alsoOpenAndClose:
            self.openRFigure()

        yMax = max( max(yVals) for yVals in yLines)

        assert len(yLines)<5 or colors is not None
        if colors is None:
            colors = ['black','red','green','blue','grey'][0:len(yLines)]

        if lty is None:
            lty = [1 for i in numLines]
        #if legend == None:
            #legend = ['' for i in range(len(yLines))]

        r.plot(r.unlist(xVals), r.unlist(xVals), ylim=r.unlist([0,yMax]), type='n', **kwArgs)#,col='black' )
        for i,yVals in enumerate(yLines):
            r.lines(r.unlist(xVals), r.unlist(yVals), col=colors[i] )
        if legend is not None:
            r.legend('topleft',legend,col=colors,lty=lty)

        if saveRawData:
            rawFn = self.getDiskPath() + '.raw.txt'
            f = open(rawFn,'w')
            f.write('x <- c(%s)' % ','.join(str(val) for val in xVals) + '\n')
            for i,yVals in enumerate(yLines):
                f.write('y%i <- c(%s)' % ( i, ','.join(str(val) for val in yVals)) +'\n')
            f.close()

        if alsoOpenAndClose:
            self.closeRFigure()

    def closeRFigure(self):
        from proto.RSetup import r
        r('dev.off()')


class StaticImage(StaticFile):
    def __init__(self, id):
        StaticFile.__init__(self, ['images']+id)


class GalaxyRunSpecificFile(StaticFile):
    '''
    Handles file path and URL of static (web-accessible) files which are specific
    to a particular history element (run).
    '''
    #def __init__(self, id, fileEnding, galaxyFn, straightOnStaticPath=False):
    #    galaxyId = extractIdFromGalaxyFn(galaxyFn)
    #    RunSpecificFile.__init__(self, id, fileEnding, galaxyId, straightOnStaticPath)
    def __init__(self, id, galaxyFn):
        self._galaxyFn = galaxyFn
        self._relativeId = id
        #StaticFile.__init__(self, ['run_specific'] + id)
        #galaxyId = galaxyFn if type(galaxyFn) in (list,tuple) else extractIdFromGalaxyFn(galaxyFn)
        #StaticFile.__init__(self, getUniqueRunSpecificId(galaxyId + id))

    def getDiskPath(self, ensurePath=False, relativeToBase=False):
        path = self._galaxyFn
        if relativeToBase:
            if path.startswith(GALAXY_BASE_DIR):
                path = path[len(GALAXY_BASE_DIR):]

        fn = getGalaxyFilesFilename(path, self._relativeId)
        #fn = os.sep.join([GALAXY_FILE_PATH] + [self._id[1], 'dataset_'+self._id[2]+'_files'] + self._id[3:])
        if ensurePath:
            ensurePathExists(fn)
        return fn

    def getURL(self):
        return '/'.join(self._relativeId)
        #return '/'.join( self._id[3:])

    def getId(self):
        return extractIdFromGalaxyFn(self._galaxyFn) + self._relativeId


class PickleStaticFile(StaticFile):
    def storePickledObject(self, obj):
        from cPickle import dump
        dump(obj, self.getFile())

    def loadPickledObject(self):
        from cPickle import load
        return load( self.getFile('r') )


class RunSpecificPickleFile(GalaxyRunSpecificFile, PickleStaticFile):
    def __init__(self, galaxyFn):
        GalaxyRunSpecificFile.__init__(self, ['results.pickle'], galaxyFn)
