import os
import re
from logging import WARNING

from gold.application.LogSetup import logException, logMessage, logging
from gold.description.AnalysisDefHandler import AnalysisDefHandler
from gold.result.BedGraphPresenter import BedGraphPresenter
from gold.result.GlobalValuePresenter import GlobalValuePresenter, ForgivingGlobalValuePresenter
from gold.result.GlobalVectorPresenter import GlobalMeanSdVectorPresenter
from gold.result.GwPlotPresenter import GwPlotPresenter
from gold.result.HeatmapPresenter import HeatmapFromNumpyPresenter, HeatmapFromDictOfDictsPresenter
from gold.result.HistogramPresenter import HistogramPresenter, HistogramGlobalListPresenter, LogHistogramGlobalListPresenter
from gold.result.LinePlotPresenter import LinePlotPresenter
from gold.result.MatrixGlobalValuePresenter import MatrixGlobalValueFromNumpyPresenter, MatrixGlobalCountsPresenter, \
     MatrixGlobalPvalPresenter, MatrixGlobalSignificancePresenter, MatrixGlobalValueFromDictOfDictsPresenter
from gold.result.ScatterPresenter import ScatterPresenter
from gold.result.TableFromDictOfDictsPresenter import TableFromDictOfDictsPresenter
from gold.result.TablePresenter import TablePresenter, DistributionTablePresenter
from gold.util.CommonFunctions import getClassName, strWithStdFormatting
from gold.util.CustomExceptions import InvalidRunSpecException, ShouldNotOccurError, AbstractClassError, SilentError
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.presenter.PixelBasedLocalResultsPresenter import PixelBasedLocalResultsPresenter
from quick.presenter.ProcessedScatterPresenter import MeanLinePresenter,BinHistPresenter
from quick.presenter.RawVisualizationPresenter import RawVisualizationPresenter
from quick.presenter.TrackDataPresenter import TrackDataPresenter
from quick.presenter.VennDataPresenter import VennDataPresenter
from quick.presenter.VisualizationPresenter import VisualizationPlotPresenter, VisualizationScatterPresenter, VisualizationScaledScatterPresenter

'''
ResultsViewerCollection is responsible for returning the html-string that represents the result-web page.
ResultsViewerCollection can iterate through a collection of ResultViewers to produce one result web-page
Noticable instance vars:
    _viewers: list of different resultviewers
    _resultsList: a list of Results object (subclass of dict)
    _galaxyFn: path to galaxy history item
Noticable methods:
    __str__: overrides str function and returns a html representation of a collection of *ResultViewer objects
'''
class ResultsViewerCollection(object):
    def __init__(self, resultsList, galaxyFn):
        self._viewers = []
        self._resultsList = resultsList
        self._galaxyFn = galaxyFn
        baseDir = GalaxyRunSpecificFile([], galaxyFn).getDiskPath()
        
        if len(resultsList) > 1:
            self._viewers.append(MultiBatchResultsViewer(resultsList, baseDir))
        for i,results in enumerate(resultsList):
            self._viewers.append(ResultsViewer(results, os.sep.join([baseDir, str(i)]) ))

    def __str__(self):
        core = HtmlCore()
        
        #core.begin()
        for i,viewer in enumerate(self._viewers):
            core.paragraph(str(viewer))
            if i < len(self._viewers)-1:
                core.divider(withSpacing=True)
        #core.end()

        return str(core)

    def storePickledResults(self):
        try:
            from cPickle import dump
            pickleStaticFile = GalaxyRunSpecificFile(['results.pickle'], self._galaxyFn)
            from copy import copy
            pickleList = [copy(res) for res in self._resultsList]
            #for res in pickleList:
            #    res._analysis=None
            dump(pickleList, pickleStaticFile.getFile())
            #dump(self._resultsList, pickleStaticFile.getFile())
        except Exception, e:
            logException(e, message='Not able to pickle results object')
        except:
            logMessage('Exception object not subclassing Exception encountered',level=logging.ERROR)


'''
ResultsViewer is the superclass root for all the different ResultsViewer classes whose sole responsibility is to return the right
kind of subclass ResultsViewer object. It does so by inspecting the results-object to find the right presCollectionType and maps
this type to a corresponding resultsViewer class
'''
class ResultsViewer(object):
    def __new__(self, results, baseDir):
        presCollectionType = results.getPresCollectionType()
        #print 'presCollectionType: ',presCollectionType 
        if presCollectionType == 'standard':
            return StandardResultsViewer.__new__(StandardResultsViewer, results, baseDir)
        elif presCollectionType == 'venndata':
            return VennResultsViewer.__new__(VennResultsViewer, results, baseDir)
        elif presCollectionType == 'global':
            return GlobalResultsViewer.__new__(GlobalResultsViewer, results, baseDir)
        elif presCollectionType == 'distribution':
            return DistributionResultsViewer.__new__(DistributionResultsViewer, results, baseDir)
        elif presCollectionType == 'dictofdicts':
            return DictOfDictsResultsViewer.__new__(DictOfDictsResultsViewer, results, baseDir)
        elif presCollectionType == 'matrix':
            return MatrixResultsViewer.__new__(MatrixResultsViewer, results, baseDir)
        elif presCollectionType == 'scatter':
            return ScatterResultsViewer.__new__(ScatterResultsViewer, results, baseDir)
        elif presCollectionType == 'lineplot':
            return LinePlotResultsViewer.__new__(LinePlotResultsViewer, results, baseDir)
        elif presCollectionType == 'binscaled':
            return BinscaledResultsViewer.__new__(BinscaledResultsViewer, results, baseDir)
        elif presCollectionType == 'visualization':
            return VisualizationResultsViewer.__new__(VisualizationResultsViewer, results, baseDir)
        elif presCollectionType == 'rawDataVisualization':
            return VisualizationResultsViewer.__new__(RawDataVisualizationResultsViewer, results, baseDir)
        elif presCollectionType == 'trackdata':
            return TrackDataResultsViewer.__new__(TrackDataResultsViewer, results, baseDir)


'''
ResultsViewerBase is a subclass of ResultsViewer and the direct superclass of all the different ResultsViewer classes.
Noticable instance vars:
    _results: the Result object (subclass of dict) containing all result-data from this analysis run
    _baseDir: path to directory where this history element is stored
    _str: contains the html-representation of this analysis run
    _presenters: contains a list of presenter-objects
Noticable methods:
    __str__: overrides str function and returns a html representation of a collection of *ResultViewer objects
    _addPresenter: adds presenters
'''
class ResultsViewerBase(ResultsViewer):
    def __new__(cls, results, baseDir):
        return object.__new__(cls)
    
    def __init__(self, results, baseDir):
        self._results = results
        self._baseDir = baseDir
        self._str = None
        
    def __str__(self):
        if self._str is not None:
            return self._str

        if self._results.isEmpty():
            if len(self._results.getAllErrors() ) > 0:
                return str(self._generateErrorText(HtmlCore))
            else:
                return str(HtmlCore().line('This analysis gave no results (might be due to too limited data). '))
                
        self._results.inferAdjustedPvalues()
        self._presenters = []
        if len(self._results.getAllRegionKeys()) > 0:
            self._addAllPresenters()        
        #print self._generateHeader()
        #print self._generateErrorText()
        #print self._generateTable(presenters)
        
        hideTable = False
        coreCls = HtmlCore
        
        try:
            if self._results.isSignificanceTesting():
                startText = self._generateAnswerText(coreCls)
                hideTable = True
            else:
                startText = self._generateHeader(coreCls)
        except Exception,e:
            startText = self._generateHeader(coreCls)
            logException(e, message='Error producing autogenerated result')
            logException(e,message='Error in auto-generated answer')
        
        return startText + self._generateRunDescription() + self._generateErrorText(coreCls) + \
               self._generateTable(coreCls, hideTable)

    def _getH0andH1Text(self, coreCls):
        h0 = self._results._h0
        h1 = self._results._h1
        if not None in (h0,h1):
            core = coreCls()
            core.descriptionLine('H0', h0, indent=True)
            core.line('vs')
            core.descriptionLine('H1', h1, indent=True)
            return str(core)
        else:
            logMessage('Did not find H0 or H1. Their values: ' + str(h0) +' and ' + str(h1))
            return None

    def _getTestStatisticAndExpectedValues(self):
        globalRes = self._results.getGlobalResult()
        if globalRes is not None:
            tsValue = globalRes.get(self._results.getTestStatisticKey() )
            expTsValue = globalRes.get(self._results.getExpectedValueOfTsKey() )
            return tsValue,expTsValue
        else:
            return None, None

    def _generateAnswerText(self, coreCls):
        onlyLocalPvals = self._results.hasOnlyLocalPvals()
        globalPval = self._results.getGlobalResult().get(self._results.getPvalKey()) if not onlyLocalPvals else None

        tableFile = GalaxyRunSpecificFile(['table.html'], galaxyFn='')
        localPvalsUrl = tableFile.getURL() #problematic dependency towards fn in tablePresenter..
        
        core = coreCls()
        core.styleInfoBegin(styleClass="infomessagesmall answerbox question")
        core.header('You asked:')
        core.line(str(coreCls().highlight(self._getHeader())))
        core.styleInfoEnd()
        
        #Simplistic answer
        core.styleInfoBegin(styleClass="infomessagesmall answerbox simplisticanswer")
        core.header(str(coreCls().link('Simplistic answer:', '#', \
                                        args='''onclick="return toggle('simplistic_answer_expl')"''')))
        
        core.styleInfoBegin(styleId="simplistic_answer_expl", styleClass="infomessagesmall explanation")
        if onlyLocalPvals :
            core.line('''
Under "simplistic answer" you will find a simple statement on whether there were any findings for the local analysis. The number of significant bins at 10% false discovery rate (FDR) is provided.<br>
<br>
It is not possible to draw a decisive conclusion based on a p-value, so the statements are only meant as simple indications.<br>
                  ''')
        else:
            core.line('''
Under "simplistic answer" you will find a yes/maybe/no-conclusion answer to the question asked, based on a simple thresholding scheme on the p-value:<br>
"yes" if p-value < 0.01<br>
"maybe" if  0.01 < p-value < 0.1<br>
"no conclusion" if p-value > 0.1<br>
<br>
It is not possible to draw a decisive conclusion based on a p-value, so the statements are only meant as simple indications.<br>                  
                  ''')
            
        core.styleInfoEnd()
        
        if onlyLocalPvals:
            numSign, numTested, numIgnored = self._results.getFdrSignBins()
            if numSign == numTested and numSign != 0:
                simplisticPhrase = 'Yes - the data suggests this for all bins'
            elif numSign>0:
                simplisticPhrase = 'Yes - the data suggests this at least in some bins'
                numSign, numTested, numIgnored = self._results.getFdrSignBins()
                simplisticPhrase += ' (%i significant bins out of %i, at %i%% FDR)' % (numSign, numTested, self._results.FDR_THRESHOLD*100)
            else:
                simplisticPhrase = 'No support from data for this conclusion in any bin'
            
                
            core.line(str(coreCls().highlight(simplisticPhrase)))
        else:
            assert globalPval is not None
            
            directionality = ''
            if self._results._isTwoSidedTest:
                tsValue, expTsValue = self._getTestStatisticAndExpectedValues()
                if tsValue is not None and expTsValue is not None and tsValue!=expTsValue:
                    directionality = '(higher) ' if tsValue > expTsValue else '(lower) '
                    
            if globalPval < 0.01:
                simplisticPhrase = 'Yes %s- the data suggests this' % directionality
            elif globalPval < 0.1:
                simplisticPhrase = 'Maybe %s- weak evidence' % directionality
            else:
                simplisticPhrase = 'No support from data for this conclusion'
                
            core.line(str(coreCls().highlight(simplisticPhrase + ' (p-value: ' + strWithStdFormatting(globalPval) + ')' )))
        core.styleInfoEnd()
        
        #Precise answer
        core.styleInfoBegin(styleClass="infomessagesmall answerbox preciseanswer")
        core.header(str(coreCls().link('Precise answer:', '#', \
                                       args='''onclick="return toggle('precise_answer_expl')"''')))
        
        core.styleInfoBegin(styleId="precise_answer_expl", styleClass="infomessagesmall explanation")
        if onlyLocalPvals :
            core.line('''
Significance testing evaluates a <b>null hypothesis (H0)</b> versus an <b>alternative hypothesis (H1)</b>. Low <b>p-values</b> are evidence against H0. The testing involves comparing the observed value of a  <b>test statistic</b> to the distribution of the test statistic under a <b>null model</b>. The testing was performed in each local bin, with a list of FDR-corrected p-values per bin provided.                  
                  ''')
        else:
            core.line('''
Significance testing evaluates a <b>null hypothesis (H0)</b> versus an <b>alternative hypothesis (H1)</b>. Low <b>p-values</b> are evidence against H0. The testing involves comparing the observed value of a  <b>test statistic</b> to the distribution of the test statistic under a <b>null model</b>. 
                  ''')

        core.styleInfoEnd()
        
        EffectSizeText = 'Please note that both the effect size and the p-value should be considered in order to assess the practical significance of a result.'
        
        FDR_text = '* False Discovery Rate: The expected proportion of false positive results among the significant bins is no more than %i%%.' \
                    % (self._results.FDR_THRESHOLD*100)
        
        if onlyLocalPvals:
            numSign, numTested, numIgnored = self._results.getFdrSignBins()
            
            core.line(str(coreCls().highlight('%i significant bins out of %i, at %i' \
                                              % (numSign, numTested, self._results.FDR_THRESHOLD*100) + '% FDR*')))
            core.line('')
            localPvalsLink = str(coreCls().link('collection of FDR-corrected p-values per bin', localPvalsUrl))
            notComputeLink = str(coreCls().link('Not able to compute', '#', \
                                               args='''onclick="return toggle('no_global_pval_expl')"'''))
            core.line('A ' + localPvalsLink + ' was computed. ' + notComputeLink + ' a global p-value for this analysis.')
            core.styleInfoBegin(styleId="no_global_pval_expl", styleClass="infomessagesmall explanation")
            core.line('(Explanation to appear in box)')
            core.styleInfoEnd()
            
            if numIgnored > 0:
                core.line('')
                core.line('%s bin%s excluded due to lack of data.' % (numIgnored, 's' if numIgnored > 1 else ''))
                
            core.line('')
            core.line(EffectSizeText)
            core.line('')
            core.line(FDR_text)

            h0h1Text = self._getH0andH1Text(coreCls)
            if h0h1Text is not None:
                core.divider(withSpacing=True)
                core.line('In each bin, the test of')
                core.append(h0h1Text)
                core.line('was performed.')
        else:
            h0h1Text = self._getH0andH1Text(coreCls)
            if h0h1Text is not None:
                core.line('The p-value is %s for the test' % strWithStdFormatting(globalPval) )
                core.append(h0h1Text)
            else:
                core.line('The p-value is %s.' % strWithStdFormatting(globalPval) )
                core.line('')
            core.line('Low p-values are evidence against H0.')

            numSign, numTested, numIgnored = self._results.getFdrSignBins()
            if numTested+numIgnored > 1:                
                localPvalsLink = str(coreCls().link('each bin separately', localPvalsUrl))
                excludeText = ' (%i bin%s excluded from FDR-analysis due to lacking p-values).' \
                              % (numIgnored, 's' if numIgnored>1 else '.') if numIgnored>0 else ''
                core.line('')
                core.line('The test was also performed for ' + localPvalsLink + \
                          ', resulting in %i significant bins out of %i, at %i%% FDR*' % (numSign, numTested, self._results.FDR_THRESHOLD*100) +\
                          excludeText)

            core.line('')
            core.line(EffectSizeText)
            core.line('')
            core.line(FDR_text)
        
        nullModel = self._results._nullModel
        if nullModel is not None:
            core.divider(withSpacing=True)
            core.line('P-values were computed under the %s defined by the following preservation and randomization rules:' \
                      % str(coreCls().highlight('null model')))
            core.paragraph(nullModel, indent=True)

        testStatistic = self._results.getTestStatisticText()
        if testStatistic != None:
            #pick out relevant part:
            mo = re.search('^[tT]est.[sS]tatistic ?:? ?',testStatistic)
            if mo!= None:
                testStatistic = testStatistic[mo.end():]            
                #if len(testStatistic)>0 and testStatistic[0]=='(':
                    #testStatistic = testStatistic[1:]
                #if len(testStatistic)>0 and testStatistic[-1]==')':
                    #testStatistic = testStatistic[:-1]
            
            tsValue, expTsValue = self._getTestStatisticAndExpectedValues()
            core.divider(withSpacing=True)
            core.line('The %s used is:' % str(coreCls().highlight('test statistic')))
            core.paragraph(testStatistic, indent=True)
            
            if tsValue is not None:
                if expTsValue is not None:
                    core.line('The value of the test statistic is %s, which is %s the expected value: %s.' \
                                % (strWithStdFormatting(tsValue), \
                                   (str(coreCls().emphasize('higher')) + ' than' if tsValue > expTsValue else \
                                    (str(coreCls().emphasize('lower')) + ' than' if tsValue < expTsValue else \
                                     str(coreCls().emphasize('equal')) + ' to')), \
                                   strWithStdFormatting(expTsValue)))
                else:
                    core.line('The value of the test statistic is %s.' % (strWithStdFormatting(tsValue)))
            
        #temporary solution, as lacking objects needed to construct note-link directly..
        noteText = ''
        if self._results._runDescription is not None:
            #mo = re.search('<note.*note>', self._results._runDescription)
            mo = re.search('<a href[^>]*/notes/[^>]*>[^<]*</a>', self._results._runDescription)
            if mo is not None:
                noteLink = mo.string[mo.start():mo.end()]
                noteText = ' See ' + noteLink + ' for a more complete description of the test.'
        
        if noteText == '':
            logMessage('Note-link not found in runDescription, and thus omitted from results')
            
        core.divider(withSpacing=True)
        
        runDescLink = str(coreCls().link('run description', '#', \
                                         args='''onclick="return toggle('run_description')"'''))
        core.line('The p-values may be subject to further parameter choices, which are listed in the %s.' %\
                  (runDescLink) + noteText)
        core.divider(withSpacing=True)
        #resultsLink = str(coreCls().link('See full details', '#', \
                                         #args='''onclick="return toggle('results_box')"'''))
        resultsLink = str(coreCls().link('See full details', '#', \
                                         args='''onclick="$('.resultsbox').toggle()"'''))
        core.line(resultsLink + ' of the results in table form.')
        core.styleInfoEnd()
        
        return str(core)
        
    def _addAllPresenters(self):
        raise AbstractClassError
       
    def _addPresenter(self, presenterClass, sendHeader=False, **kwArgs):
        #print 'Generating figure: ',presenterClass.__name__,'<br>'
        try:
            pres = presenterClass(self._results, self._baseDir, *([self._getHeader()] if sendHeader else []), **kwArgs ) 
            self._presenters.append( pres)
            return pres
        except SilentError:
            return None
        except Exception,e:
            logException(e, WARNING, 'Error generating figure with ' + str(presenterClass.__name__))
            print 'Error generating figure with ', presenterClass.__name__, '(',Exception,' - ',e,')'
            return None
            
    def _generateHeader(self, coreCls):
        coreCls = HtmlCore
        core = coreCls()
        
        headerLine = self._getHeader()

        core.styleInfoBegin(styleClass="infomessagesmall answerbox question")
        core.header('Global results table for:')
        core.line(str(coreCls().highlight(headerLine)))
        core.styleInfoEnd()
        
        #core.bigHeader(headerLine)
        #core.line('')
        return str(core)

    def _generateRunDescription(self):
        return self._results._runDescription if self._results._runDescription is not None else ''

    def _getHeader(self):
        #analysisDef = self._results._analysisDef 
        #if analysisDef is not None:
        #    return str(analysisDef)
        #else:
        if self._results._analysisText is not None:
            try:
                return AnalysisDefHandler.splitAnalysisText(self._results._analysisText)[1].strip()
            except AssertionError:
                pass
        
        trackName1, trackName2 = self._results.getTrackNames()        
        return self._results.getStatClassName() + \
                (' between ' if not trackName2 in [None,[]] else ' on ') + ':'.join(trackName1) + \
                ((' and ' + ':'.join(trackName2)) if not trackName2 in [None,[]] else '')
    
    def _generateErrorText(self, coreCls):
        allErrors = self._results.getAllErrors()
        if len(allErrors) == 0:
            return ''

        core = coreCls()
        for exception in self._results.getAllErrors():
            if isinstance(exception, InvalidRunSpecException):
                self._errorBox(core, 'No results are available for this job, as the specification of the run was invalid: ', exception)
            else:
                self._errorBox(core, 'No results are available for this job, as an error of type %s occured: ' % getClassName(exception), exception)
        
        return str(core)
        
    def _errorBox(self, core, message, exception=None, helpMessage=None):
        core.styleInfoBegin(styleClass='errormessagelarge')
        core.header(message)
        if exception:
            core.paragraph(str(exception), indent=True)
        if helpMessage:
            core.paragraph(str(core.__class__().emphasize(helpMessage)))
        core.styleInfoEnd()
        return core

    def _writetableHeader(self, core):
        if self._presCollectionType in ['standard']:
            core.tableHeader(*zip(*[['Results','rowspan=2']] +\
                               ([['Global analysis', 'rowspan=2']] if self._results.getGlobalResult() not in [None,{}] else []) +\
                               [['Local analysis', 'colspan='+ str(len(self._presenters)-1)]]))
            core.tableHeader([pres.getDescription() for pres in self._presenters \
                              if not isinstance(pres, GlobalValuePresenter)], firstRow=False)
        elif self._presCollectionType in ['global', 'venndata']:
            core.tableHeader(*zip(*[['Results']] +\
                               ([['Global analysis']] if self._results.getGlobalResult() not in [None,{}] else [])))
            core.tableHeader([pres.getDescription() for pres in self._presenters \
                              if not isinstance(pres, GlobalValuePresenter)], firstRow=False)
        elif self._presCollectionType in ['dictofdicts']:
            core.tableHeader(*zip(*[['Results','rowspan=2']] +\
                               ([['Global analysis', 'colspan=2']] if self._results.getGlobalResult() not in [None,{}] else []) +\
                               [['Local analysis', 'colspan='+ str(len(self._presenters)-1)]]))
            core.tableHeader([pres.getDescription() for pres in self._presenters], firstRow=False)
        elif self._presCollectionType in ['matrix']:
            core.tableHeader(*zip(*[['Results','rowspan=2']] +\
                               ([['Global analysis', 'colspan=5']] if self._results.getGlobalResult() not in [None,{}] else [])))
            core.tableHeader([pres.getDescription() for pres in self._presenters], firstRow=False)
        elif self._presCollectionType in ['distribution','scatter','binscaled','lineplot', 'visualization','rawDataVisualization', 'trackdata']:
            core.tableHeader(['Results'] + [pres.getDescription() for pres in self._presenters])
        #elif self._presCollectionType == 'distribution':
        #    core.tableHeader(['Results'] + [pres.getDescription() for pres in self._presenters \
        #                      if not isinstance(pres, GlobalValuePresenter)], firstRow=False)
        #elif self._presCollectionType == 'scatter':
        #elif self._presCollectionType == 'binscaled':
        else:
            raise ShouldNotOccurError
        #core.tableHeader(*zip(*[['Results','rowspan=2']] +\
        #                       ([['Global analysis', 'rowspan=2']] if self._results.getGlobalResult() not in [None,{}] else []) +\
        #                       [['Local analysis', 'colspan='+ str(len(self._presenters)-1)]]))
        
    def _generateTable(self, coreCls, hideTable=False):
        core = coreCls()
        
        if len(self._presenters) == 0:            
            self._errorBox(core, 'There are no result presenters defined for this analysis (the results table has no columns).')
            return str(core)
        if len(self._results.getResDictKeys()) == 0:
            assert not self._results.isEmpty() #should have been catched earlier..
            self._errorBox(core, "There are no results available for this analysis.", \
                           helpMessage="This may happen if there is no or too " \
                                       "little data in the analysis regions, " \
                                       "or if the analysis regions are empty. " \
                                       "The analysis regions may be empty for two reasons: " \
                                       "1) If 'bounding regions' was selected as analysis regions, " \
                                          "the bounding regions (i.e. the defined regions) " \
                                          "of the track(s) do not overlap. " \
                                       "2) If specific analysis regions were selected, " \
                                           "the analysis regions are outside the bounding regions " \
                                           "of the track(s).")
            return str(core)

#        core.styleInfoBegin(styleId='results_box', styleClass='infomessagesmall answerbox resultsbox')
        core.styleInfoBegin(styleId='results_box', styleClass='answerbox resultsbox')
        #core.tableHeader(['', 'Global results', 'Local results'],\
        #    [ 'rowspan=2', 'rowspan=2', 'colspan='+ str(len(self._presenters)-1) ])
        
        self._writetableHeader(core)
        
#        if self._presCollectionType in ['matrix']:
#            core.tableLine([str( pres.getReference() ) for pres in self._presenters])
#        else:

        resDictKeys = self._results.getResDictKeys()
        isAllResDictKeysPresenter = [hasattr(pres, 'getSingleReference') for pres in self._presenters]

        
        for rowNum,resDictKey in enumerate(resDictKeys):
            #temp = HtmlCore().link(*self._results.getLabelHelpPair(resDictKey))
            row = [ str( coreCls().textWithHelp(*self._results.getLabelHelpPair(resDictKey)) ) ]
            rowSpanList = [1]
            for i,pres in enumerate(self._presenters):
                
                if isAllResDictKeysPresenter[i]:
                    if rowNum == 0:
                        row.append( str(pres.getSingleReference()) )
                        rowSpanList.append(len(resDictKeys))
                else:
                    row.append( str(pres.getReference(resDictKey)) )
                    rowSpanList.append(1)
            core.tableLine(row, rowSpanList)
        core.tableFooter()
        
        core.styleInfoEnd()
        
        if hideTable:
            core.script(' $(".resultsbox").hide();')
        
        return str(core) 

'''
StandardResultsViewer is a subclass of ResultsViewerBase and ResultsViewer.
Noticable methods:
    _addAllPresenters: adds presenter-objects to ResultsViewerBase variable _presenters
'''
class StandardResultsViewer(ResultsViewerBase):
    def _addAllPresenters(self):
#        self._results.inferAdjustedPvalues()

        self._presCollectionType = 'standard'                
        self._addPresenter(GlobalValuePresenter)
        self._addPresenter(TablePresenter, True)
        #self._addPresenter(RawTextTablePresenter, True)
        bedGraphPresenter = self._addPresenter(BedGraphPresenter)
        self._addPresenter(HistogramPresenter, True)
        #self._addPresenter(DensityPresenter, True)                
        if bedGraphPresenter is not None:                    
            self._addPresenter(GwPlotPresenter, True, historyFilePresenter=bedGraphPresenter)

        from config.Config import IS_EXPERIMENTAL_INSTALLATION
        if IS_EXPERIMENTAL_INSTALLATION:
            self._addPresenter(PixelBasedLocalResultsPresenter, True)
        #self._addPresenter(FDRSummaryPresenter)
        #self._addPresenter(WigPresenter)


class VennResultsViewer(ResultsViewerBase):
    def _addAllPresenters(self):
        self._presCollectionType = 'venndata'                
        self._addPresenter(VennDataPresenter)


'''
GlobalResultsViewer is a subclass of ResultsViewerBase and ResultsViewer.
Noticable methods:
    _addAllPresenters: adds presenter-objects to ResultsViewerBase variable _presenters
'''        
class GlobalResultsViewer(ResultsViewerBase):
    def _addAllPresenters(self):
        self._presCollectionType = 'global'                
        self._addPresenter(GlobalValuePresenter)

'''
MatrixResultsViewer is a subclass of ResultsViewerBase and ResultsViewer.
Noticable methods:
    _addAllPresenters: adds presenter-objects to ResultsViewerBase variable _presenters
''' 
class MatrixResultsViewer(ResultsViewerBase):
    def _addAllPresenters(self):
        self._presCollectionType = 'matrix'
        self._addPresenter(MatrixGlobalCountsPresenter, True)
        self._addPresenter(MatrixGlobalValueFromNumpyPresenter, True)
        self._addPresenter(MatrixGlobalPvalPresenter, True)
        self._addPresenter(MatrixGlobalSignificancePresenter, True)
        self._addPresenter(HeatmapFromNumpyPresenter, True)

'''
DictOfDictsResultsViewer is a subclass of ResultsViewerBase and ResultsViewer.
Noticable methods:
    _addAllPresenters: adds presenter-objects to ResultsViewerBase variable _presenters
''' 
class DictOfDictsResultsViewer(ResultsViewerBase):
    def _addAllPresenters(self):
        self._presCollectionType = 'dictofdicts'
        self._addPresenter(MatrixGlobalValueFromDictOfDictsPresenter, True)
        self._addPresenter(HeatmapFromDictOfDictsPresenter, True)
        self._addPresenter(TableFromDictOfDictsPresenter, True)


'''
DistributionResultsViewer is a subclass of ResultsViewerBase and ResultsViewer.
Noticable methods:
    _addAllPresenters: adds presenter-objects to ResultsViewerBase variable _presenters
''' 
class DistributionResultsViewer(ResultsViewerBase):
    def _addAllPresenters(self):
        self._presCollectionType = 'distribution'
        #brk(host='localhost', port=9000, idekey='galaxy')
        #self._addPresenter(GlobalValuePresenter(self._results, self._baseDir))
        self._addPresenter(DistributionTablePresenter, True)
        self._addPresenter(HistogramGlobalListPresenter, True)
        self._addPresenter(LogHistogramGlobalListPresenter, True)
        #self._addPresenter(DensityGlobalListPresenter, True)                

'''
ScatterResultsViewer is a subclass of ResultsViewerBase and ResultsViewer.
Noticable methods:
    _addAllPresenters: adds presenter-objects to ResultsViewerBase variable _presenters
''' 
class ScatterResultsViewer(ResultsViewerBase):
    def _addAllPresenters(self):
        self._presCollectionType = 'scatter'
        self._addPresenter(ScatterPresenter, True)
        self._addPresenter(MeanLinePresenter, True)
        self._addPresenter(BinHistPresenter, True)

'''
LinePlotResultsViewer is a subclass of ResultsViewerBase and ResultsViewer.
Noticable methods:
    _addAllPresenters: adds presenter-objects to ResultsViewerBase variable _presenters
'''         
class LinePlotResultsViewer(ResultsViewerBase):
    def _addAllPresenters(self):
        self._presCollectionType = 'lineplot'
        self._addPresenter(LinePlotPresenter, True)

'''
BinscaledResultsViewer is a subclass of ResultsViewerBase and ResultsViewer.
Noticable methods:
    _addAllPresenters: adds presenter-objects to ResultsViewerBase variable _presenters
''' 
class BinscaledResultsViewer(ResultsViewerBase):
    def _addAllPresenters(self):
        self._presCollectionType = 'binscaled'
        self._addPresenter(GlobalMeanSdVectorPresenter, True)

'''
VisualizationResultsViewer is a subclass of ResultsViewerBase and ResultsViewer.
Noticable methods:
    _addAllPresenters: adds presenter-objects to ResultsViewerBase variable _presenters
''' 
class VisualizationResultsViewer(ResultsViewerBase):
    def _addAllPresenters(self):
        self._presCollectionType = 'visualization'
        self._addPresenter(VisualizationPlotPresenter, True)
        self._addPresenter(VisualizationScatterPresenter, True)
        self._addPresenter(VisualizationScaledScatterPresenter, True)

'''
RawDataVisualizationResultsViewer is a subclass of ResultsViewerBase and ResultsViewer.
Noticable methods:
    _addAllPresenters: adds presenter-objects to ResultsViewerBase variable _presenters
'''         
class RawDataVisualizationResultsViewer(ResultsViewerBase):
    def _addAllPresenters(self):
        self._presCollectionType = 'rawDataVisualization'
        self._addPresenter(RawVisualizationPresenter, True)

'''
MultiBatchResultsViewer is a subclass of ResultsViewerBase and ResultsViewer.
Noticable methods:
    _addAllPresenters: adds presenter-objects to ResultsViewerBase variable _presenters
'''     
class MultiBatchResultsViewer(ResultsViewerBase):
    def __init__(self, resultsList, parentBaseDir):
        self._resultsList = resultsList
        self._parentBaseDir = parentBaseDir
        self._str = None
 
    def __str__(self):
        if self._str is not None:
            return self._str
                
        self._presenters = []
        
        for i,res in enumerate(self._resultsList):
            self._baseDir = os.sep.join([self._parentBaseDir,'multibatch'+str(i)])
            self._results = res
            self._addPresenter(ForgivingGlobalValuePresenter)
        #return self._generateHeader() + self._generateErrorText() + self._generateTable()
        return self._generateTable()

    def _generateTable(self):

        #core.tableHeader(['', 'Global results', 'Local results'],\
        #    [ 'rowspan=2', 'rowspan=2', 'colspan='+ str(len(self._presenters)-1) ])
        #core.tableHeader([pres.getDescription() for pres in self._presenters \
                          #if not isinstance(pres, GlobalValuePresenter)], firstRow=False)
        coreCls = HtmlCore

        columns = []
        columns.append( ['']+[str(i) for i in range(len(self._resultsList))])
            #[ 'rowspan=2', 'rowspan=2', 'colspan='+ str(len(self._presenters)-1) ])
        
        #allResDictKeys = reduce(lambda x,y:x.union(y), [set(x.getResDictKeys()) for x in self._resultsList] )
        allResDictKeys = []
        for res in self._resultsList:
            for k in res.getResDictKeys():
                if not k in allResDictKeys:
                    allResDictKeys.append(k)
        #Print tracknames
        for trackIndex in [0,1]:
            columns.append([ 'Track %i (last term):'%trackIndex] +\
                [str( pres.getTrackName(trackIndex)[-1]) if len(pres.getTrackName(trackIndex))>0 else '' for pres in self._presenters])

        for pres in self._presenters:
            pres._results.inferAdjustedPvalues()            
        #signBins = [(pres._results.getFdrSignBinsText() if pres._results.hasOnlyLocalPvals() else '') for pres in self._presenters]
        signBins = [(pres._results.getFdrSignBinsText() if pres._results.isSignificanceTesting() else '') for pres in self._presenters]
        if any( signBin != '' for signBin in signBins ):
            columns.append(['Local significance: '] + signBins)
                            
        for resDictKey in allResDictKeys:
            #temp = HtmlCore().link(*self._results.getLabelHelpPair(resDictKey))
            columns.append([ str( coreCls().textWithHelp(*self._results.getLabelHelpPair(resDictKey)) ) ] +\
                [str( pres.getReference(resDictKey) ) for pres in self._presenters])

        numColumns = len(columns)
        numRows = len(columns[0])

        core = coreCls()
        core.tableHeader([columns[colIndex][0] for colIndex in range(numColumns)], sortable=True)
        for rowIndex in range(1,numRows):
            core.tableLine([columns[colIndex][rowIndex] for colIndex in range(numColumns)])
        core.tableFooter()
                    
        return str(core)     

    #def _generateTable(self):
    #    coreCls = HtmlCore
    #    core = coreCls()
    #
    #    #core.tableHeader(['', 'Global results', 'Local results'],\
    #    #    [ 'rowspan=2', 'rowspan=2', 'colspan='+ str(len(self._presenters)-1) ])
    #    #core.tableHeader([pres.getDescription() for pres in self._presenters \
    #                      #if not isinstance(pres, GlobalValuePresenter)], firstRow=False)
    #    core.tableHeader(['']+[str(i) for i in range(len(self._resultsList))])
    #        #[ 'rowspan=2', 'rowspan=2', 'colspan='+ str(len(self._presenters)-1) ])
    #    
    #    #allResDictKeys = reduce(lambda x,y:x.union(y), [set(x.getResDictKeys()) for x in self._resultsList] )
    #    allResDictKeys = []
    #    for res in self._resultsList:
    #        for k in res.getResDictKeys():
    #            if not k in allResDictKeys:
    #                allResDictKeys.append(k)
    #    #Print tracknames
    #    for trackIndex in [0,1]:
    #        core.tableLine([ 'Track %i (last term):'%trackIndex] +\
    #            [str( pres.getTrackName(trackIndex)[-1]) if len(pres.getTrackName(trackIndex))>0 else '' for pres in self._presenters])
    #
    #    for pres in self._presenters:
    #        pres._results.inferAdjustedPvalues()            
    #    #signBins = [(pres._results.getFdrSignBinsText() if pres._results.hasOnlyLocalPvals() else '') for pres in self._presenters]
    #    signBins = [(pres._results.getFdrSignBinsText() if pres._results.isSignificanceTesting() else '') for pres in self._presenters]
    #    if any( signBin != '' for signBin in signBins ):
    #        core.tableLine(['Local significance: '] + signBins)
    #                        
    #    for resDictKey in allResDictKeys:
    #        #temp = HtmlCore().link(*self._results.getLabelHelpPair(resDictKey))
    #        core.tableLine([ str( coreCls().textWithHelp(*self._results.getLabelHelpPair(resDictKey)) ) ] +\
    #            [str( pres.getReference(resDictKey) ) for pres in self._presenters])
    #
    #    core.tableFooter()
    #                
    #    return str(core)     
    
class TrackDataResultsViewer(ResultsViewerBase):
    def _addAllPresenters(self):
        self._presCollectionType = 'trackdata'
        self._addPresenter(TrackDataPresenter)
