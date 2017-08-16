import datetime
import os
import re
from urllib import quote, unquote

from config.Config import DebugConfig,STATIC_REL_PATH, URL_PREFIX
from gold.util.CommonConstants import BATCH_COL_SEPARATOR
from gold.application.LogSetup import logException
from gold.application.LogSetup import logMessage, logging
from gold.description.Analysis import Analysis
from gold.description.TrackInfo import TrackInfo
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.util.GenomeInfo import GenomeInfo


class RunDescription(object):
    @staticmethod
    def getRunDescription(trackName1, trackName2, trackNameIntensity, analysisDef, ubSource, revEngBatchLine, \
                          urlForTrackAutoSelection, manualSeed, **kwArgs):
        genome = ubSource.genome
        core = HtmlCore()

        analysis = Analysis(analysisDef, genome, trackName1, trackName2, **kwArgs)
        
        core.header('GENOME')
        core.append(GenomeInfo(genome).mainInfo(printEmpty=False))
        core.divider()
                
        formatChoices = analysis.getFormatConverterChoicesAsText().items()
        tr1FormatChoice, tr2FormatChoice = formatChoices if len(formatChoices) == 2 else (None, None) 
        
        first = True
        for tn,label,formatChoice in zip([trackName1,trackName2,trackNameIntensity], \
                                         ['TRACK 1','TRACK 2','INTENSITY TRACK'], \
                                         [tr1FormatChoice,tr2FormatChoice,None]):
            if tn in [None, []]:
                continue
            
            if not first:
                core.divider()

            core.header(label)
            trackInfo = TrackInfo(genome, tn)
            trackText = ''
            if ExternalTrackManager.isHistoryTrack(tn):
                assert len(tn)>=4, 'Length of external track name < 4: %s' % str(tn)
                core.descriptionLine('Name', ExternalTrackManager.extractNameFromHistoryTN(tn) + ' (from history)' + os.linesep)
            else:
                core.descriptionLine('Name', ':'.join(tn) + os.linesep)
            core.append(trackInfo.mainInfo(printEmpty=False))

            if formatChoice is not None:
                core.descriptionLine('Treated as', formatChoice[1])
            
            first = False
        
        core.divider()
        core.header('ANALYSIS')
        core.paragraph( ''.join(str(analysis).split(':')[1:]) )

        first = True
        for label,choice in analysis.getInterfaceChoicesAsText().items():
            if first:
                core.divider()
                core.header('OPTIONS')
            
            if manualSeed is not None and label == 'Random seed' and choice == 'Random':
                choice = str(manualSeed)
                
            core.descriptionLine(label, choice)
            first = False
            
        h0 = analysis.getH0()
        if h0 is not None:
            core.divider()
            core.header('NULL HYPOTHESIS')
            core.paragraph(h0)
            
        h1 = analysis.getH1()
        if h1 is not None:
            core.divider()
            core.header('ALTERNATIVE HYPOTHESIS')
            core.paragraph(h1)
            
        core.divider()
        core.header('ANALYSIS REGIONS')
        if hasattr(ubSource, 'description'):
            core.paragraph(ubSource.description)
            
        core.divider()
        core.header('SOLUTION')

        statClass = analysis.getStat()
        #One alternative is to put getDescription in MagicStatFactory-hierarchy as class-method, and get real class behind partial-object.
        #if isinstance(statClass, functools.partial):
            #statClass = statClass.func
        #core.paragraph( statClass.getDescription() )

        #Chosen alternative is to Instantiate an object, which will automatically give object of real class..
        #and then use the following two lines, which will get class in Statistic-hierarchy instead of MagicStatFactory-hierarchy ..
        try:
            reg = ubSource.__iter__().next()
        except:
            core.paragraph('Solution not relevant, as there are no specified analysis regions..')
        else:
            track1, track2 = analysis.getTracks()
            if statClass is None:
                core.paragraph('Solution not available, due to currently invalid analysis')
                logMessage('Solution not available, with params: ' + str([trackName1, trackName2, analysisDef]), level=logging.WARN )
            else:
                statObj = statClass(reg,track1, track2)
                statDescr = statObj.getDescription()
                replPat = '<a href=' + os.sep.join([STATIC_REL_PATH,'notes','stats','']) + r'\1>note</a>'
                statDescr = re.sub('<note>(.*)</note>', replPat, statDescr)
        
                core.paragraph( statDescr )

        core.divider()
        core.header('TIME OF ANALYSIS')
        core.paragraph('Analysis initiated at time: ' + str( datetime.datetime.now() ) )
        
        if urlForTrackAutoSelection not in [None, '']:
            core.divider()
            core.header('URL FOR TRACK AUTOSELECTION')
            #urlOptions = '&'.join(['track1=' + quote(':'.join(trackName1)), 'track2=' + quote(':'.join(trackName2))])
            #core.paragraph(URL_PREFIX + '/hyper?' + urlOptions)
            core.styleInfoBegin(styleClass='break-word')
            core.paragraph(urlForTrackAutoSelection)
            core.styleInfoEnd()
            
        if revEngBatchLine not in [None, '']:
            core.divider()
            core.header('CORRESPONDING BATCH COMMAND LINE')
            #if any(ExternalTrackManager.isRedirectOrExternalTrack(tn) for tn in [trackName1, trackName2]):
                #core.paragraph('Batch-run line not available with tracks from history')
            #else:
            core.styleInfoBegin(styleClass='break-word')
            core.paragraph(revEngBatchLine)
            core.styleInfoEnd()

        core.divider()
        core.header('REFERENCES')
        core.paragraph('The HyperBrowser system is described in:<br>"Sandve et al., <a href="http://genomebiology.com/2010/11/12/R121/">The Genomic HyperBrowser: inferential genomics at the sequence level</a>, Genome Biol. 2010;11(12):R121')
        from gold.statistic.RandomizationManagerStat import RandomizationManagerStat
        if statClass is not None and RandomizationManagerStat.getMcSamplingScheme(statClass.keywords) == 'MCFDR':
            core.paragraph('The p-values of this analysis were computed using the MCFDR scheme for Monte Carlo based p-value computation'+\
                           ', described in:<br>Sandve et al., <a href="http://bioinformatics.oxfordjournals.org/content/early/2011/10/13/bioinformatics.btr568.long">Sequential Monte Carlo multiple testing</a>, Bioinformatics 2011')
        
#        description = \
#'''
#Run descriptions will be introduced in the next version of HB. <br>
#Below is an example run description, which is a static text unconnected to your choices. The purpose is to get feedback from you on what this should look like:<br>
#Track1 (refseg:genes): Unmarked points (converted from unmarked segments, taking midpoints)<br>
#Track2 (DNA melting:meltmap): Function<br>
#Bins: Chr1, divided into bins of 10 megabases<br>
#Question: Are track1-points occurring with different frequency inside track2-segment than outside?<br>
#Analysis:<br>
#The main result is a p-value resulting from a statistical test connected to the question.<br>
#The null-hypothesis assumes that the track1-points are randomly distributed according to a poisson-distribution, with the same number of points as in the original data. Track2-segment are assumed fixed as they are in the original data. This can be answered by a binomial test. The alternative hypothesis is then that the count of points inside segments has resulted from a different distribution of points, where the points are then either distributed more or less inside segments versus outside. See the note on this question in the user guide for further info.<br>
#'''
        return str(core)
    
    @staticmethod
    def getRevEngBatchLine(trackName1, trackName2, cleanedTrackName1, cleanedTrackName2, analysisDef, \
                           regSpec, binSpec, genome, manualSeed, **kwArgs):
        #analysisDef is assumed to be unquoted
        
        #if this is to work, must check explicitly against special keywords  in regSpec (or check that regSpec is a valid region that is to have region..)...
        #if not genome in regSpec:
        #    regSpec = genome+':'+regSpec
        try:
            if DebugConfig.VERBOSE:
                logMessage('getting RevEngBatchLine:')
            #analysisDef =analysisDef.replace('%20PointCountInSegsPvalStat%2C','') #REMOVE
            #print 'NOWAG: ',analysisDef
            
            analysis = Analysis(analysisDef, genome, cleanedTrackName1, cleanedTrackName2, **kwArgs)
            stat = analysis.getStat()
            if stat is None:
                return 'No corr batch line, as no valid statistic was found.. '
            #print 'CAME HERE'
            statClassName = stat.__name__
            #fixme: Add space, but this is not checked in batchrunner...
            params = ','.join(['='.join([choicePair[0], str(manualSeed)]) \
                                 if (manualSeed is not None and choicePair[0] == 'randomSeed' and choicePair[1] == 'Random')
                                    else '='.join(choicePair) \
                                for choicePair in analysis.getChoices(filterByActivation=True).items() \
                                 if choicePair[0] not in ['H0','H1_more','H1_less','H1_different','H1_ha1','H1_ha2','H1_ha3','H1_ha4','H1_ha5'] ])
            statText = statClassName + '(' + params + ')'
            #return BATCH_COL_SEPARATOR.join([regSpec, binSpec, \
            #                 (':'.join(trackName1)).replace(' ','_'),\
            #                 (':'.join(trackName2)).replace(' ','_') if trackName2 is not None else 'None',\
            #                 statText])
            #assert unquote(regSpec) == regSpec
            assert unquote(binSpec) == binSpec #To assure that unquote can be safely applied to binSpec without any consequences (we don't want to always quote, but still want the possibility to use quoted history track names)
            batchElements = [genome, regSpec, binSpec, \
                             (':'.join([quote(x, safe='') for x in trackName1])),\
                             (':'.join([quote(x, safe='') for x in trackName2])) if trackName2 is not None else 'None',\
                             statText]
            #batchElements = [el.replace(BATCH_COL_SEPARATOR, '\\' + BATCH_COL_SEPARATOR) for el in batchElements]
            #batchElements = [quote(el, safe='') for el in batchElements]
            oneLineBatch = BATCH_COL_SEPARATOR.join(batchElements)
            
            
            #return oneLineBatch
            #Under construction...:
            tn1=(':'.join([quote(x, safe='') for x in trackName1]))
            tn2=(':'.join([quote(x, safe='') for x in trackName2])) if trackName2 is not None else 'None'
            from collections import OrderedDict
            #batchVariables = OrderedDict([('@GENOME',genome), ('@REGION',regSpec), ('@BINNING',binSpec), ('@TN1',tn1), ('@TN2',tn2), ('@ANALYSIS',statText)])
            batchVariables = OrderedDict([('@REGION',regSpec), ('@BINNING',binSpec), ('@TN1',tn1), ('@TN2',tn2), ('@ANALYSIS',statText)])
            batchComposition = BATCH_COL_SEPARATOR.join([genome]+batchVariables.keys() )
            fullBatchList = ['='.join(assignment) for assignment in batchVariables.items()] + [batchComposition]
            fullBatch = '<br>'.join(fullBatchList)

            batchLinkDef = '<a href="%s/hyper?mako=generictool&tool_id=hb_batch_run_tool&command=%s&dbkey=%s">%s</a>'
            oneLineBatchLink = batchLinkDef % (URL_PREFIX, quote(oneLineBatch), genome, 'single line version')
            fullBatchLink = batchLinkDef % (URL_PREFIX, quote('\n'.join(fullBatchList)), genome, 'variable based version')

            #return oneLineBatch + '<br><br>or corresponding spec using variable assignment:<br><br>' + fullBatch + '<br><br>Execute batchline in ' \
                #+ oneLineBatchLink + ' / ' + fullBatchLink
            return oneLineBatch + '<br><br>Execute batchline in ' + oneLineBatchLink + ' / ' + fullBatchLink
            
        except Exception,e:
            #raise
            logException(e,logging.WARNING,'Could not generate corresponding batch line: ')
            #if DebugConfig.VERBOSE:
            logMessage('analysisDef, genome, trackName1, trackName2: \n' +
                       str([analysisDef, genome, trackName1, trackName2]) )
            return 'Warning: Could not generate corresponding batch line.' 
