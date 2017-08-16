#import pkg_resources
#
#pkg_resources.require( "sqlalchemy" )

import ast
import glob
import os
import re
import shelve
import urllib
import urllib2
from collections import Counter, defaultdict, OrderedDict
from shutil import copytree
from time import time

import numpy as np

import third_party.safeshelve as safeshelve
from config.Config import DATA_FILES_PATH
from config.Config import PROCESSED_DATA_PATH
from gold.origdata.GESourceWrapper import GEGenericFilter
from gold.origdata.GenomeElementSource import GenomeElementSource
from gold.origdata.GtrackComposer import StdGtrackComposer
from gold.track.GenomeRegion import GenomeRegion
from gold.track.Track import PlainTrack
from gold.util.CommonFunctions import createOrigPath
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.ProcTrackOptions import ProcTrackOptions
from quick.util.CommonFunctions import changedWorkingDir, getGeSource
from quick.util.GenomeInfo import GenomeInfo
from quick.webtools.GeneralGuiTool import GeneralGuiTool, MultiGeneralGuiTool


class Tool3(MultiGeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Kai's tools"
    
    @staticmethod
    def getSubToolClasses():
        return [QueryDatabase,
                TestDbConnection,
                ExtractIndividualTracksFromCategoryTrack,
                MakeMutationFastaFile,
                FindSignificantPwmRegions,
                JoinToNonOverlappingRegions,
                FilterCategoryonVals,
                AddToolsToCollection,
                UserTools,
                ModifyHistItems,
                UploadFromInvitro,
                ShowParams,
                ShowScreencast,
                MakeVennDiagram,
                PlotStockPrices,
                CalculateWeekdayProfits,
                TranslateNumbersInFile,
                DownloadStockPrices,
                BastianFirst,
                BastianLast,
                SubTool,
                TrackSearch,
                ConcatenateHistItems,
                FilterHistElOnMatchingColumns,
                CreateGCFunction,
                Make3dGtrackFiles,
                ExtractColumnsFromTrack]

        #return [MakeMutationFastaFile, FindSignificantPwmRegions, JoinToNonOverlappingRegions, filterCategoryonVals, RunToolTests, AddToolsToCollection, UserTools, ModifyHistItems, UploadFromInvitro, ShowParams, ShowScreencast, MakeVennDiagram, PlotStockPrices, CalculateWeekdayProfits, TranslateNumbersInFile, DownloadStockPrices, BastianFirst, BastianLast, SubTool, TrackSearch, ConcatenateHistItems, FilterHistElOnMatchingColumns, CreateGCFunction, Make3dGtrackFiles, ExtractColumnsFromTrack]



class QueryDatabase(GeneralGuiTool):

    db_url = None
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Query database"

    @staticmethod
    def getInputBoxNames():

        return ['select table','Table definition', 'query the database', 'query result' ] #Alternatively: [ ('box1','1'), ('box2','2') ]

    @classmethod
    def getOptionsBox1(cls):
        from sqlalchemy import create_engine
        from config.LocalOSConfig import GALAXY_BASE_DIR
        from ConfigParser import SafeConfigParser

        cp = SafeConfigParser()
        cp.read( GALAXY_BASE_DIR+'/universe_wsgi.ini' )
        if cp.has_option( "app:main", "database_connection" ):
            cls.db_url = cp.get( "app:main", "database_connection" )
            engine = create_engine(cls.db_url)
            connection = engine.connect()
            result = connection.execute("select table_name from information_schema.tables where table_schema = 'public'")
            connection.close()
            return [v[0] for v in result]#), 5, True





    @classmethod
    def getOptionsBox2(cls, prevChoices):

        if prevChoices[0]:
            from sqlalchemy import create_engine
            engine = create_engine(cls.db_url)
            connection = engine.connect()
            result = connection.execute("select column_name from information_schema.columns where table_name = '%s'" % prevChoices[0])
            connection.close()
            res = [v[0] for v in result]
            return '\n'.join(res), len(res), True


    @classmethod
    def getOptionsBox3(cls, prevChoices):
        return ''

    @classmethod
    def getOptionsBox4(cls, prevChoices):

        if prevChoices[-2]:
            from sqlalchemy import create_engine
            query = prevChoices[-2].lower()
            if re.match('select ', query):
                heading = query.split('from ')[0].split()[1:]
                if heading[0] =='*':
                    heading = prevChoices[-3].split('\n')
                resTab = [heading]
                query += ' limit 150' if query.find(' limit ')<0 else ''

                engine = create_engine(cls.db_url)
                connection = engine.connect()
                result = connection.execute(query)
                connection.close()
                resTab += [[str(i)for i in v] for v in result]
                return resTab





    @staticmethod
    def isHistoryTool():
        '''
        Specifies if a History item should be created when the Execute button is
        clicked.
        '''
        return False





class TestDbConnection(GeneralGuiTool):

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Test connecting to the database"

    @staticmethod
    def getInputBoxNames():

        return ['Select start date (YYYY-MM-DD)','Select end date (YYYYMMDD)', '','Select items', 'select visualization', '.'] #Alternatively: [ ('box1','1'), ('box2','2') ]


    @classmethod
    def makeJsonFiles(cls, resultDict, sDate):

        htmlTemplate = '''
        \n\n<link href="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/themes/base/jquery-ui.css" rel="stylesheet" type="text/css"/>\n  <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.5/jquery.min.js"></script>\n  <script src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/jquery-ui.min.js"></script>\n
        <script type='text/javascript' src='https://www.google.com/jsapi'></script>
        <script type='text/javascript'>
          google.load("visualization", "1", {packages:["corechart", "controls"]});

      </script>

        <script type="text/javascript">
        function point_it(event) {

        entryNo = 0;
        var data = %s;
        makeGooglePlot(data);
        };

      function makeGooglePlot(data){
        var dEntry = google.visualization.arrayToDataTable(data);

        var dashboard = new google.visualization.Dashboard(
             document.getElementById('dashboard'));

         var control = new google.visualization.ControlWrapper({
           'controlType': 'ChartRangeFilter',
           'containerId': 'control',
           'options': {
             // Filter by the date axis.
             'filterColumnIndex': 0,
             'ui': {
               'chartType': 'LineChart',
               'chartOptions': {
                 'chartArea': {'width': '80%%'},

               },
               'chartView': {
                 'columns': %s
               }
             }
           }
         });

         var chart = new google.visualization.ChartWrapper({
           'chartType': 'LineChart',
           'containerId': 'chart',
           'options': {
             // Use the same chart area width as the control for axis alignment.
             'chartArea': {'height': '80%%', 'width': '80%%'},
             'legend': {'position': 'right'},
             'title': 'Detailed bp coverage',
             'hAxis': {'title': 'Days between %s'},
             'vAxis': {'title': 'Runs'}
           }
         });

         dashboard.bind(control, chart);
         dashboard.draw(dEntry);
      }

      //google.setOnLoadCallback(drawVisualization);
    </script>
         <h3 class="plotRegion" align="center">Region</h3>
         <br/><div id="dashboard" style="width: 1000px; height: 700px;">
         <div id="chart" style="width: 100%%; height: 500px;"></div>
         <div id="control" style="width: 100%%; height: 50px;"></div> </div>
         <script type="text/javascript">
         point_it();
         </script>'''

        namesL = sorted(resultDict.keys())#[unicode(v, errors='ignore') for v in ]
        #print namesL
        valuesLL = [[k[-1] for k in resultDict[v]] for v in namesL]
        yearL = sorted([v[0] for v in resultDict.values()[-1]])
        namesL.insert(0, "x")
        #print valuesLL
        #print yearL
        dataList = [ [v.encode('ascii','ignore') for v in namesL] ] +  [[yearL[i]] + list(v) for i, v in enumerate(zip(*valuesLL))]
        #print dataList

        return htmlTemplate % (repr(dataList), repr(range(len(namesL))), sDate)


    @classmethod
    def makeColumnChartText(cls, dataList):

        htmlTemplate = '''<script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load("visualization", "1", {packages:["corechart"]});

      function drawChart() {
        var data = google.visualization.arrayToDataTable( %s);

        var options = {
          title: 'Total Usage for time period',
          hAxis: {title: 'Tool/statistic', titleTextStyle: {color: 'red'}}
        };

        var chart = new google.visualization.ColumnChart(document.getElementById('chart_div'));
        chart.draw(data, options);
      }
    </script>
    <h3 class="plotRegion" align="center">Region</h3>
         <br/><div id="chart_div" style="width: 1000px; height: 700px;">
         <script type="text/javascript">
         drawChart();
         </script>'''


        namesL = ['tools', 'usage'] #sorted(resultDict.keys())#[unicode(v, errors='ignore') for v in ]
        dataList.insert(0, namesL)
        #print dataList,   , repr(range(len(namesL))

        return htmlTemplate % repr(dataList)

    @staticmethod
    def getOptionsBox1():

        return  ''

    @staticmethod
    def getOptionsBox2(prevChoices):

        return  ''

    @staticmethod
    def getOptionsBox3(prevChoices):
        if prevChoices[0] and prevChoices[1]:
            # Poor man's optparse
            from sqlalchemy import create_engine
            from config.LocalOSConfig import GALAXY_BASE_DIR
            from ConfigParser import SafeConfigParser
            if prevChoices[-1]:
                return ('__hidden__', prevChoices[-1])

            cp = SafeConfigParser()
            cp.read( GALAXY_BASE_DIR+'/universe_wsgi.ini' )
            if cp.has_option( "app:main", "database_connection" ):
                db_url = cp.get( "app:main", "database_connection" )
                engine = create_engine(db_url)
                connection = engine.connect()
                #and jp.name = 'stats'
                analysisTool = 'hb_test_1'
                genericTools = '''select tool_id, date_trunc('day', create_time) as create_tid, count(*) as num from job where command_line ~ 'hyperbrowser' and tool_id != '%s' and create_time>'%s'  and create_time<'%s' group by tool_id, date_trunc('day', create_time)'''

                resDict = dict()
                #genericTools = '''select tool_id, create_time from job where command_line ~ 'hyperbrowser' and tool_id != '%s' order by create_time''' % analysisTool
                for i, v in enumerate( connection.execute(genericTools%(analysisTool ,prevChoices[0], prevChoices[1])) ):
                    if resDict.has_key(urllib.unquote(v['tool_id'])):
                        resDict[urllib.unquote(v['tool_id'])][v['create_tid'].toordinal()] = int(v['num'])
                    else:
                        resDict[urllib.unquote(v['tool_id'])] = {v['create_tid'].toordinal():int(v['num'])}

                whereClause = "jp.name='stats' and jp.job_id = j.id and j.create_time > '%s'  and create_time < '%s'" % (prevChoices[0], prevChoices[1])
                result = connection.execute("select jp.value, j.create_time from job_parameter jp, job j where %s order by j.create_time" % whereClause)
                connection.close()
                #data = [v['value'].split(urllib.quote('-> '))[1].strip()[:-1] for i, v in enumerate(result) if  v['value'].find(urllib.quote('-> '))>0]
                for i, v in enumerate(result):
                    if  v['value'].find(urllib.quote('-> '))>0:
                        day = v['create_time'].toordinal()
                        stat = urllib.unquote(v['value'].split(urllib.quote(':'))[0][1:].strip())
                        if resDict.has_key(stat):
                            if resDict[stat].has_key(day):
                                resDict[stat][day]+=1
                            else:
                                resDict[stat][day] = 1
                        else:
                            resDict[stat]={day:1}
                return ('__hidden__', urllib.quote(repr(resDict)))


    @staticmethod
    def getOptionsBox4(prevChoices):

        if prevChoices[-2]:
            #return prevChoices[-2], 5, True
            data = ast.literal_eval(urllib.unquote(prevChoices[-2]))
            sortedList = sorted([(urllib.unquote(k), sum(v.values())) for k ,v in data.items()], key=lambda i: i[1], reverse=True )

            return OrderedDict([(k, False) for k, v in sortedList])#,30, True

    @staticmethod
    def getOptionsBox5(prevChoices):

        if prevChoices[-2]:
            return ['-----  Select  -----', 'Show aggregated result', 'show time series']



    @classmethod
    def getOptionsBox6(cls, prevChoices):
        #return None

        def fillOutList(start, end, dates):
            res = []
            index = 0
            dateLen = len(dates)
            for i in range(start, end+1):
                count = 0
                while index<dateLen and i == dates[index]:
                   count+=1
                   index+=1
                res.append((i-start, count))
            return res

        if prevChoices[-3] and any(prevChoices[-3].values()) and prevChoices[-2] != '-----  Select  -----':
            from datetime import datetime
            a, b, c = prevChoices[0].split('-')
            startDate = datetime(int(a),int(b),int(c)).toordinal()
            a, b, c = prevChoices[1].split('-')
            lastDate = datetime(int(a),int(b),int(c)).toordinal()
            data = ast.literal_eval(urllib.unquote(prevChoices[-4]))

            candidateStats = [k for k, v in prevChoices[-3].items() if v]
            if prevChoices[-2] == 'show time series':
                resDict = defaultdict(list)
                for k, d in data.items():
                    if urllib.unquote(k) in candidateStats:

                        missingDates = set(range(startDate, lastDate)) - set(d.keys())
                        for i in missingDates:
                            d[i] = 0

                        resDict[urllib.unquote(k).replace(',','_')] = [(i-startDate, d[i]) for i in sorted(d.keys())]

                htmlCode = cls.makeJsonFiles(resDict, prevChoices[0]+' and '+prevChoices[1])
                return '__rawstr__', htmlCode, False
            else:
                resList = []
                for k, d in data.items():
                    if urllib.unquote(k) in candidateStats:
                        resList.append( [urllib.unquote(k).replace(',','_'), sum(d.values())] )

                htmlCode = cls.makeColumnChartText(resList)
                return '__rawstr__', htmlCode, False



    @staticmethod
    def getResetBoxes():
        '''
        Specifies a list of input boxes which resets the subsequent stored
        choices previously made. The input boxes are specified by index
        (starting with 1) or by key.
        '''
        return [2]


    @staticmethod
    def isHistoryTool():
        '''
        Specifies if a History item should be created when the Execute button is
        clicked.
        '''
        return False

class ConstructEncodeBasedTfMappingsAsGtrackSuite(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Construct Encode Based Tf Mappings As Gtrack-Suite"

    @staticmethod
    def getInputBoxNames():

        return ['set start date', 'set end date'] #Alternatively: [ ('box1','1'), ('box2','2') ]

    @staticmethod
    def getOptionsBox1():
        return  ''

    @staticmethod
    def getOptionsBox1():
        return  ''

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        pass


class ConstructEncodeBasedTfMappingsAsGtrackSuite(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Construct Encode Based Tf Mappings As Gtrack-Suite"

    @staticmethod
    def getInputBoxNames():

        return ['select genome','Select history element' ] #Alternatively: [ ('box1','1'), ('box2','2') ]

    @staticmethod
    def getOptionsBox1():
        return  '__genome__'

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        pass


class AnalyzeTfsVersusSnvCore(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Analyze tfs versus snv core tool"

    @staticmethod
    def getInputBoxNames():

        return ['select genome','Select history element' ] #Alternatively: [ ('box1','1'), ('box2','2') ]

    @staticmethod
    def getOptionsBox1():
        return  '__genome__'


    @staticmethod
    def getOptionsBox2(prevChoices):
        return  '__history__', 'bed', 'category.bed', 'gtrack'

    @classmethod
    def getSequence(cls, genome, geSource):
        chrLength = GenomeInfo.getStdChrLengthDict(genome)
        fastaTrack = PlainTrack( ['Sequence', 'DNA'] )
        count = 0
        chrom = None
        for ge in geSource:
            if ge.chr!=chrom:
                chrom = ge.chr
                sequence = fastaTrack.getTrackView(GenomeRegion(genome, chrom, 0, chrLength[chrom])).valsAsNumpyArray()

            yield chrom, ge.start, list(sequence[ge.start:ge.end])
            count += ge.end-ge.start
            if count >= 330000:
                break

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        from gold.origdata.BedGenomeElementSource import BedGenomeElementSource, BedCategoryGenomeElementSource
        from gold.origdata.GtrackGenomeElementSource import GtrackGenomeElementSource

        startTime = time()

        genome = choices[0]
        track = choices[1].split(':')

        fileType = ExternalTrackManager.extractFileSuffixFromGalaxyTN(track)
        fn = ExternalTrackManager.extractFnFromGalaxyTN(track)

        if fileType == 'bed':
            geSource = BedGenomeElementSource(fn)
        else:
            geSource = BedCategoryGenomeElementSource(fn) if fileType == 'category.bed' else GtrackGenomeElementSource(fn)
        lineTemplate = '%s\t%i\t%i\t%s>%s'
        bpValues = ['a','c','g','t']
        with open(galaxyFn,'w') as bedObj:
            mutationStrList = []
            for chrom, start, sequence in cls.getSequence(genome, geSource):

                for indx, bp in enumerate(sequence):
                    position = start+indx
                    bp = bp.lower()
                    mutations = [v for v in bpValues if v!=bp]
                    mutationStrList += [lineTemplate % (chrom, position, position+1, bp, mut) for mut in mutations]
                if len(mutationStrList)>10000:
                    print>>bedObj, '\n'.join(mutationStrList)
                    mutationStrList = []




        print 'finished writing output file: ', time()-startTime
    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'category.bed'




class AnalyzeTfsVersusSnvTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Analyze Tfs Versus Snv Tool"

    @staticmethod
    def getInputBoxNames():

        return ['select genome','Select history element' ] #Alternatively: [ ('box1','1'), ('box2','2') ]

    @staticmethod
    def getOptionsBox1():
        return  '__genome__'

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        pass



class ExtractIndividualTracksFromCategoryTrack(GeneralGuiTool):

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Extracti ndividual tracks from category-track"
    histChoice = 'From history'
    trackChoice = 'From track repository'

    @staticmethod
    def getInputBoxNames():

        return ['select genome','Select source for category-track', 'select history dataset', 'select track', 'hidden', 'use all or select categories?', 'select categories' ,'make seperate file for each category?'] #Alternatively: [ ('box1','1'), ('box2','2') ]

    @staticmethod
    def getOptionsBox1():
        return  '__genome__'

    @classmethod
    def getOptionsBox2(cls, prevChoices):
        return  ['-----  Select  -----', cls.histChoice, cls.trackChoice]

    @classmethod
    def getOptionsBox3(cls, prevChoices):
        if prevChoices[1] == cls.histChoice:
            return  '__history__', 'bed', 'category.bed', 'gtrack'

    @classmethod
    def getOptionsBox4(cls, prevChoices):
        if prevChoices[1] == cls.trackChoice:
            return  '__track__'

    @classmethod
    def getOptionsBox5(cls, prevChoices):
        if prevChoices[1] in [cls.trackChoice, cls.histChoice]:
            genome = prevChoices[0]
            if prevChoices[-1]:
                return  ('__hidden__', prevChoices[-1])
            if prevChoices[2] and prevChoices[2].split(':')[1] in ['category.bed','bed','gtrack']:
                track = prevChoices[2].split()
                geSource = getGeSource(prevChoices[2])
                tmp = set()
                for ge in geSource:
                    tmp.add(ge.val)
                return ('__hidden__', urllib.quote(repr(tmp)))

    @classmethod
    def getOptionsBox6(cls, prevChoices):
        if prevChoices[1] in [cls.trackChoice, cls.histChoice]:
            return  ['-----  Select  -----','get all categories','select categories']


    @classmethod
    def getOptionsBox7(cls, prevChoices):
        if prevChoices[-2] == 'select categories':
            return OrderedDict([(v,False) for v in ast.literal_eval(urllib.unquote(prevChoices[4]))])

    @classmethod
    def getOptionsBox8(cls, prevChoices):
        if prevChoices[5] == 'select categories':
            return ['Yes', 'No']


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        utFil = open(galaxyFn, 'w')
        genome = choices[0]
        track = choices[2].split(':') if choices[1] == cls.histChoice else choices[3].split(':')
        categories = sorted(ast.literal_eval(urllib.unquote(choices[4]))) if choices[5] == 'get all categories' else sorted([k for k,v  in choices[6].items() if v])
        categoryFileDict = dict()
        if choices[5] == 'select categories' and choices[7] == 'Yes':
            for cat in categories:
                categoryFileDict[cat] = open(cls.makeHistElement(galaxyExt='bed', title=cat.replace('_','#')), 'w')
            singleCatFiles = True
        else:
            categoryFileDict = dict([(v,utFil)for v in categories])
            singleCatFiles = False



        geSource = getGeSource(track, genome)
        bedTemplate = '%s\t%i\t%i'
        catBedTemplate = '%s\t%i\t%i\t%s'
        for ge in geSource:
            if ge.val in categories:
                if singleCatFiles:
                     print>>categoryFileDict[ge.val], bedTemplate % (ge.chr, ge.start, ge.end)
                else:
                    print>>categoryFileDict[ge.val], catBedTemplate % (ge.chr, ge.start, ge.end, ge.val)

        for fileObj in set(categoryFileDict.values()):
            fileObj.close()



    @classmethod
    def validateAndReturnErrors(cls, choices):
        if choices[1] not in [cls.histChoice, cls.trackChoice]:
            return ''

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'category.bed'





class MakeMutationFastaFile(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "make mutation fasta file based on regions"

    @staticmethod
    def getInputBoxNames():

        return ['select genome','Select history element' ] #Alternatively: [ ('box1','1'), ('box2','2') ]

    @staticmethod
    def getOptionsBox1():
        return  '__genome__'


    @staticmethod
    def getOptionsBox2(prevChoices):
        return  '__history__', 'bed', 'category.bed', 'gtrack'

    @classmethod
    def getSequence(cls, genome, geSource):
        chrLength = GenomeInfo.getStdChrLengthDict(genome)
        fastaTrack = PlainTrack( ['Sequence', 'DNA'] )
        count = 0
        chrom = None
        for ge in geSource:
            if ge.chr!=chrom:
                chrom = ge.chr
                sequence = fastaTrack.getTrackView(GenomeRegion(genome, chrom, 0, chrLength[chrom])).valsAsNumpyArray()

            yield chrom, ge.start, list(sequence[ge.start:ge.end])
            count += ge.end-ge.start
            if count >= 330000:
                break

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        from gold.origdata.BedGenomeElementSource import BedGenomeElementSource, BedCategoryGenomeElementSource
        from gold.origdata.GtrackGenomeElementSource import GtrackGenomeElementSource

        startTime = time()

        genome = choices[0]
        track = choices[1].split(':')

        fileType = ExternalTrackManager.extractFileSuffixFromGalaxyTN(track)
        fn = ExternalTrackManager.extractFnFromGalaxyTN(track)

        if fileType == 'bed':
            geSource = BedGenomeElementSource(fn)
        else:
            geSource = BedCategoryGenomeElementSource(fn) if fileType == 'category.bed' else GtrackGenomeElementSource(fn)
        lineTemplate = '%s\t%i\t%i\t%s>%s'
        bpValues = ['a','c','g','t']
        with open(galaxyFn,'w') as bedObj:
            mutationStrList = []
            for chrom, start, sequence in cls.getSequence(genome, geSource):

                for indx, bp in enumerate(sequence):
                    position = start+indx
                    bp = bp.lower()
                    mutations = [v for v in bpValues if v!=bp]
                    mutationStrList += [lineTemplate % (chrom, position, position+1, bp, mut) for mut in mutations]
                if len(mutationStrList)>10000:
                    print>>bedObj, '\n'.join(mutationStrList)
                    mutationStrList = []




        print 'finished writing output file: ', time()-startTime
    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'category.bed'






class FindSignificantPwmRegions(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "find regions with significant pwm score"

    @staticmethod
    def getInputBoxNames():

        return ['select genome','Select history element' ] #Alternatively: [ ('box1','1'), ('box2','2') ]

    @staticmethod
    def getOptionsBox1():
        return  '__genome__'


    @staticmethod
    def getOptionsBox2(prevChoices):
        return  '__history__', 'bed', 'category.bed', 'gtrack'



    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        from gold.origdata.BedGenomeElementSource import BedGenomeElementSource, BedCategoryGenomeElementSource
        from gold.origdata.GtrackGenomeElementSource import GtrackGenomeElementSource
        genome = choices[0]
        resultDict = defaultdict(list)

        startTime = time()

        track = choices[1].split(':')
        fileType = ExternalTrackManager.extractFileSuffixFromGalaxyTN(track)
        fn = ExternalTrackManager.extractFnFromGalaxyTN(track)


        if fileType == 'bed':
            geSource = BedGenomeElementSource(fn)
        else:
            geSource = BedCategoryGenomeElementSource(fn) if fileType == 'category.bed' else GtrackGenomeElementSource(fn)

        for ge in geSource:
            resultDict[ge.chr].append((ge.start,  ge.end))

        print 'finished with: ', fn, time()-startTime

        return True


        utfil = open(galaxyFn,'w')
        lineTemplate = '%s\t%i\t%i'
        for chrom in resultDict:
            sortedStarts = sorted(resultDict[chrom].keys())
            prevStart, prevEnd = sortedStarts[0], resultDict[chrom][sortedStarts[0]]

            for start in sortedStarts:
                if start>prevEnd:
                    print>>utfil, lineTemplate % (chrom, prevStart, prevEnd)
                    prevStart, prevEnd = start, resultDict[chrom][start]
                else:
                    prevEnd = max(resultDict[chrom][start], prevEnd)
        print 'finished writing output file: ', time()-startTime
    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'bed'





class JoinToNonOverlappingRegions(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Join regions to non-overlapping regions"

    @staticmethod
    def getInputBoxNames():

        return ['select genome','Select history elements' ] #Alternatively: [ ('box1','1'), ('box2','2') ]

    @staticmethod
    def getOptionsBox1():
        return  '__genome__'


    @staticmethod
    def getOptionsBox2(prevChoices):
        return  '__multihistory__', 'bed', 'category.bed', 'gtrack'



    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        from gold.origdata.BedGenomeElementSource import BedGenomeElementSource, BedCategoryGenomeElementSource
        from gold.origdata.GtrackGenomeElementSource import GtrackGenomeElementSource
        genome = choices[0]
        resultDict = defaultdict(dict)

        startTime = time()
        for indx, track in enumerate(choices[1].values()):
            track = track.split(':')
            fileType = ExternalTrackManager.extractFileSuffixFromGalaxyTN(track)
            fn = ExternalTrackManager.extractFnFromGalaxyTN(track)


            if fileType == 'bed':
                geSource = BedGenomeElementSource(fn)
            else:
                geSource = BedCategoryGenomeElementSource(fn) if fileType == 'category.bed' else GtrackGenomeElementSource(fn)

            for ge in geSource:

                if resultDict[ge.chr].has_key(ge.start):
                    resultDict[ge.chr][ge.start] = max(resultDict[ge.chr][ge.start], ge.end)
                else:
                    resultDict[ge.chr][ge.start] = ge.end

            print 'finished with: ', fn, time()-startTime
        utfil = open(galaxyFn,'w')
        lineTemplate = '%s\t%i\t%i'
        for chrom in resultDict:
            sortedStarts = sorted(resultDict[chrom].keys())
            prevStart, prevEnd = sortedStarts[0], resultDict[chrom][sortedStarts[0]]

            for start in sortedStarts:
                if start>prevEnd:
                    print>>utfil, lineTemplate % (chrom, prevStart, prevEnd)
                    prevStart, prevEnd = start, resultDict[chrom][start]
                else:
                    prevEnd = max(resultDict[chrom][start], prevEnd)
        print 'finished writing output file: ', time()-startTime
    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'bed'




class FilterCategoryonVals(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Filter category on values"

    @staticmethod
    def getInputBoxNames():

        return ['Select history element', 'select values' ] #Alternatively: [ ('box1','1'), ('box2','2') ]


    @staticmethod
    def getOptionsBox1():
        return '__history__', 'category.bed', 'gtrack'


    @staticmethod
    def getOptionsBox2(prevChoices):
        if prevChoices[0]:
            fn = ExternalTrackManager.extractFnFromGalaxyTN(prevChoices[0])
            cats = OrderedDict()
            for v in GenomeElementSource(fn):
                if not v.val in cats:
                    cats[v.val] = False
            return cats

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        def filterFunc(x, cats):
            return x in cats

        geSource = GenomeElementSource('infile.category.bed')
        geFilter = GEGenericFilter(geSource, genome, 'val', lambda x:x in ['a','b'])
        composer = StdGtrackComposer(geFilter)
        composer.composeToFile('outfile.gtrack')



#
# class EditToolTests(GeneralGuiTool):
#     @staticmethod
#     def getToolName():
#         '''
#         Specifies a header of the tool, which is displayed at the top of the
#         page.
#         '''
#         return "Edit tests on a Tool"
#
#     @staticmethod
#     def getInputBoxNames():
#
#         return ['Select tool', 'Select tool'] #Alternatively: [ ('box1','1'), ('box2','2') ]
#
#     @classmethod
#     def getSourceCode(cls):
#          path = os.getcwd()
#          if path.find('database')>=0:
#              path = path.split('database')[0] + '/hyperbrowser/src/quick/webtools/GeneralGuiToolsFactory.py'
#          else:
#              path = path.split('hyperbrowser')[0] + '/hyperbrowser/src/quick/webtools/GeneralGuiToolsFactory.py'
#          try:
#              streng = open(path).read()
#          except:
#              path = path.split('hyperbrowser')[0] + '/data/hyperbrowser/hb_core_developer/trunk/quick/webtools/GeneralGuiToolsFactory.py'
#              streng = open(path).read()
#          return streng
#
#     @classmethod
#     def getOptionsBox1(cls):
#         streng = cls.getSourceCode()
#         importList = [streng[i.start()+5:i.end()].split(' import ') for i in re.finditer('from [a-zA-Z0-9.]+ import [a-zA-Z0-9]+', streng)]
#         toolIdDict = dict([(streng.split(v[0])[0].split("'")[-2], v[-1].strip()) for v in importList])
#         keys = [v.split('.')[0] for v in os.listdir(DATA_FILES_PATH + os.sep + 'tests' + os.sep)]
#         return OrderedDict([(toolIdDict[v], False) for v in keys])
#         #return  OrderedDict([(streng[i.start():i.end()].split(' import ')[1], False) for i in re.finditer('from [a-zA-Z0-9.]+ import [a-zA-Z0-9]+', streng)])
#
#
#     @classmethod
#     def getOptionsBox2(cls, prevChoices):
#         if prevChoices[0]:
#
#             import importlib
#             streng = cls.getSourceCode()
#             candidateTools = [k for k,v in prevChoices[0].items() if v]
#             importList = [streng[i.start()+5:i.end()].split(' import ') for i in re.finditer('from [a-zA-Z0-9.]+ import [a-zA-Z0-9]+', streng) if streng[i.start():i.end()].split(' import ')[1] in candidateTools]
#             hiddenDict = dict()
#             toolIdDict = dict([(v[-1].strip(), streng.split(v[0])[0].split("'")[-2]) for v in importList])
#             for toolRow in importList:
#                 module = importlib.import_module(toolRow[0])
#                 className = toolRow[-1].strip()
#                 toolId = toolIdDict[className]
#                 toolClass = getattr(module, className)(toolId)
#                 testDict = getattr(toolClass, 'getTests')()
#                 if testDict:
#                     logMessage('testDict: '+ repr(testDict))
#                     hiddenDict.update(testDict)
#
#             jCode = '''<script type="text/javascript">$( "form" ).bind( "submit", function( event ) {
#             var testCollection = %s;
#
#             for (var key in testCollection) {
#                     $.post("/dev2/tool_runner",  testCollection[key]);
#             }
#         event.preventDefault();} );</script>'''
#             return '__rawstr__',jCode % json.dumps(hiddenDict), False
#         return None
#
#     @classmethod
#     def parseTest(cls, test, typeList, toolClass, toolId):
#
#         resultDict = dict()
#         textMal= 'box%i%s'
#
#         eChoices = [eval(v) for v in test.split('(',1)[1].rsplit(')',1)[0].split('|')]
#         dType = getattr(toolClass, 'getOutputFormat')(eChoices)
#         resultDict['datatype'] = dType
#         resultDict['tool_id'] = toolId
#         resultDict['URL'] = 'http://dummy'
#         resultDict['tool_name'] = toolId
#         choices = [repr(v).replace("'",'') for v in eChoices]
#         #logMessage('my test choices table: ' + repr(choices))
#
#         for i,v in enumerate(choices):
#             if not v in ['','None']:
#                 bName, bType = typeList[i]
#                 if bType == 'genome':
#                     resultDict['dbkey'] = v.replace("'",'')
#                 elif bType == 'multiHistory':
#                     for s,t in eval(v).items():
#                         resultDict[bName+'|%i'%s] = t.replace("'",'')
#                 elif bType == 'track':
#                     resultDict[bName] = v
#                     #for s,t in enumerate(v.split(':')):
#                     #    resultDict[bName+'_%i'%s] = t
#                     #resultDict[bName+'_state'] = ''
#
#                 elif bType == 'dict':
#                     for s,t in eval(v).items():
#                         resultDict[bName+'|%i'%s] = t.replace("'",'')
#                 else:
#                     resultDict[bName] = v.replace("'",'')
#
#
#         return resultDict
#
#     #@classmethod
#     #def getOptionsBox3(cls, prevChoices):
#     #    jCode = '''<script type="text/javascript">$( "form" ).bind( "submit", function( event ) {
#     #
#     #    alert( unescape($("#box2").val()) );
#     #    event.preventDefault();} );</script>'''
#     #    return 'rawStr', jCode, False
#     @classmethod
#     def execute(cls, choices, galaxyFn=None, username=''):
#         pass


# class RunToolTests(GeneralGuiTool):
#     @staticmethod
#     def getToolName():
#         '''
#         Specifies a header of the tool, which is displayed at the top of the
#         page.
#         '''
#         return "Run tests on all Tools"
#
#     @staticmethod
#     def getInputBoxNames():
#
#         return ['Select tools', 'select users', 'select tests', '.'] #Alternatively: [ ('box1','1'), ('box2','2') ]
#
#     @classmethod
#     def getSourceCode(cls):
#          path = os.getcwd()
#          if path.find('database')>=0:
#              path = path.split('database')[0] + '/hyperbrowser/src/quick/webtools/GeneralGuiToolsFactory.py'
#          else:
#              path = path.split('hyperbrowser')[0] + '/hyperbrowser/src/quick/webtools/GeneralGuiToolsFactory.py'
#          try:
#              streng = open(path).read()
#          except:
#              path = path.split('hyperbrowser')[0] + '/data/hyperbrowser/hb_core_developer/trunk/quick/webtools/GeneralGuiToolsFactory.py'
#              streng = open(path).read()
#          return streng
#
#     @classmethod
#     def getOptionsBox1(cls):
#         streng = cls.getSourceCode()
#         importList = [streng[i.start()+5:i.end()].split(' import ') for i in re.finditer('from [a-zA-Z0-9.]+ import [a-zA-Z0-9]+', streng)]
#         toolIdDict = dict([(streng.split(v[0])[0].split("'")[-2], v[-1].strip()) for v in importList])
#         keys = [v.split('.')[0] for v in os.listdir(DATA_FILES_PATH + os.sep + 'tests' + os.sep)]
#         return OrderedDict([(v, False) for v in keys])
#         #return OrderedDict([(toolIdDict[v], False) for v in keys])
#         #return  OrderedDict([(streng[i.start():i.end()].split(' import ')[1], False) for i in re.finditer('from [a-zA-Z0-9.]+ import [a-zA-Z0-9]+', streng)])
#
#     @classmethod
#     def getOptionsBox2(cls, prevChoices):
#         if prevChoices[0]:
#             resSet = set()
#             for fn in [k for k, v in prevChoices[0].items() if v]:
#                 SHELVE_FN = DATA_FILES_PATH + os.sep + 'tests' + os.sep + '%s.shelve'%fn
#                 tmpSet = set([k.split('::',1)[0] for k in shelve.open(SHELVE_FN).keys()])
#                 resSet.update(tmpSet)
#
#             return OrderedDict([(k,False) for k in resSet])
#
#
#     @classmethod
#     def getOptionsBox3(cls, prevChoices):
#         if prevChoices[0] and any(prevChoices[1].values()):
#             resSet = set()
#             userList = [k for k, v  in prevChoices[1].items() if v]
#             for fn in [k for k, v in prevChoices[0].items() if v]:
#                 SHELVE_FN = DATA_FILES_PATH + os.sep + 'tests' + os.sep + '%s.shelve'%fn
#                 key = fn+':  '
#
#                 tmpSet = set([key+k[:k.rfind('::')] for k in shelve.open(SHELVE_FN).keys() if k.split('::',1)[0] in userList])
#                 resSet.update(tmpSet)
#
#             return OrderedDict([(k,False) for k in resSet])
#
#     @classmethod
#     def getOptionsBox4(cls, prevChoices):
#
#         if prevChoices[2] and any(prevChoices[2].values()):
#             candidateDict = defaultdict(list)
#             for k, v in prevChoices[2].items():
#                 if v:
#                     key, value = k.split(': ',1)
#                     candidateDict[key].append(value.strip())
#             count = 0
#             resultDict = dict()
#             for fn in candidateDict.keys():
#                 SHELVE_FN = DATA_FILES_PATH + os.sep + 'tests' + os.sep + '%s.shelve'%fn
#                 for k, v in shelve.open(SHELVE_FN).items():
#                     if k.rsplit('::',1)[0] in candidateDict[fn]:
#                         resultDict[str(count)] = v
#                         count+=1
#
#             jCode = '''<script type="text/javascript">$( "form" ).bind( "submit", function( event ) {
#             var testCollection = %s;
#
#             for (var key in testCollection) {
#
#                     $.post("/dev2/tool_runner",  testCollection[key]);
#             }
#         event.preventDefault();} );</script>'''
#             return '__rawstr__',jCode % json.dumps(resultDict), False
#
#         #if False:#prevChoices[0]:
#         #
#         #    import importlib
#         #    streng = cls.getSourceCode()
#         #    candidateTools = [k for k,v in prevChoices[0].items() if v]
#         #    importList = [streng[i.start()+5:i.end()].split(' import ') for i in re.finditer('from [a-zA-Z0-9.]+ import [a-zA-Z0-9]+', streng) if streng[i.start():i.end()].split(' import ')[1] in candidateTools]
#         #    hiddenDict = dict()
#         #    toolIdDict = dict([(v[-1].strip(), streng.split(v[0])[0].split("'")[-2]) for v in importList])
#         #    for toolRow in importList:
#         #        module = importlib.import_module(toolRow[0])
#         #        className = toolRow[-1].strip()
#         #        toolId = toolIdDict[className]
#         #        toolClass = getattr(module, className)(toolId)
#         #        testDict = getattr(toolClass, 'getTests')()
#         #        if testDict:
#         #            logMessage('testDict: '+ repr(testDict))
#         #            hiddenDict.update(testDict)
#
#         return None
#
#     @classmethod
#     def parseTest(cls, test, typeList, toolClass, toolId):
#
#         resultDict = dict()
#         textMal= 'box%i%s'
#
#         eChoices = [eval(v) for v in test.split('(',1)[1].rsplit(')',1)[0].split('|')]
#         dType = getattr(toolClass, 'getOutputFormat')(eChoices)
#         resultDict['datatype'] = dType
#         resultDict['tool_id'] = toolId
#         resultDict['URL'] = 'http://dummy'
#         resultDict['tool_name'] = toolId
#         choices = [repr(v).replace("'",'') for v in eChoices]
#         #logMessage('my test choices table: ' + repr(choices))
#
#         for i,v in enumerate(choices):
#             if not v in ['','None']:
#                 bName, bType = typeList[i]
#                 if bType == 'genome':
#                     resultDict['dbkey'] = v.replace("'",'')
#                 elif bType == 'multiHistory':
#                     for s,t in eval(v).items():
#                         resultDict[bName+'|%i'%s] = t.replace("'",'')
#                 elif bType == 'track':
#                     resultDict[bName] = v
#                     #for s,t in enumerate(v.split(':')):
#                     #    resultDict[bName+'_%i'%s] = t
#                     #resultDict[bName+'_state'] = ''
#
#                 elif bType == 'dict':
#                     for s,t in eval(v).items():
#                         resultDict[bName+'|%i'%s] = t.replace("'",'')
#                 else:
#                     resultDict[bName] = v.replace("'",'')
#
#
#         return resultDict
#
#     #@classmethod
#     #def getOptionsBox3(cls, prevChoices):
#     #    jCode = '''<script type="text/javascript">$( "form" ).bind( "submit", function( event ) {
#     #
#     #    alert( unescape($("#box2").val()) );
#     #    event.preventDefault();} );</script>'''
#     #    return 'rawStr', jCode, False
#     @classmethod
#     def execute(cls, choices, galaxyFn=None, username=''):
#         pass


class AddToolsToCollection(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Bookmark tools to your collection"

    @staticmethod
    def getInputBoxNames():

        return ['Specify tool name', 'Specify tool URL', 'Specify tool name', 'Specify tool URL', 'Specify tool name', 'Specify tool URL',\
                'Specify tool name', 'Specify tool URL', 'Specify tool name', 'Specify tool URL', 'Specify tool name', 'Specify tool URL',\
                'Specify tool name', 'Specify tool URL', 'Specify tool name', 'Specify tool URL'] #Alternatively: [ ('box1','1'), ('box2','2') ]

    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey()

        return ''

    @staticmethod
    def getOptionsBox2(prevChoices):
        return ''


    @staticmethod
    def getOptionsBox3(prevChoices):
        if prevChoices[-2]:
            return ''
    @staticmethod
    def getOptionsBox4(prevChoices):
        if prevChoices[-3]:
            return ''


    @staticmethod
    def getOptionsBox5(prevChoices):
        if prevChoices[-2]:
            return ''
    @staticmethod
    def getOptionsBox6(prevChoices):
        if prevChoices[-3]:
            return ''

    @staticmethod
    def getOptionsBox7(prevChoices):
        if prevChoices[-2]:
            return ''
    @staticmethod
    def getOptionsBox8(prevChoices):
        if prevChoices[-3]:
            return ''


    @staticmethod
    def getOptionsBox9(prevChoices):
        if prevChoices[-2]:
            return ''
    @staticmethod
    def getOptionsBox10(prevChoices):
        if prevChoices[-3]:
            return ''

    @staticmethod
    def getOptionsBox11(prevChoices):
        if prevChoices[-2]:
            return ''
    @staticmethod
    def getOptionsBox12(prevChoices):
        if prevChoices[-3]:
            return ''

    @staticmethod
    def getOptionsBox13(prevChoices):
        if prevChoices[-2]:
            return ''
    @staticmethod
    def getOptionsBox14(prevChoices):
        if prevChoices[-3]:
            return ''


    @staticmethod
    def getOptionsBox15(prevChoices):
        if prevChoices[-2]:
            return ''
    @staticmethod
    def getOptionsBox16(prevChoices):
        if prevChoices[-3]:
            return ''

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        if username:
            SHELVE_FN = DATA_FILES_PATH + os.sep + 'UserToolsCollection.shelve'
            s = safeshelve.open(SHELVE_FN)
            valDict = s[username] if s.has_key(username) else {}
            for i in range(0, len(choices),2):
                if choices[i] and choices[i+1]:
                    valDict[choices[i]] = choices[i+1]

                else:
                    break
            if valDict:
                s[username] = valDict
            s.close()




class UserTools(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Bookmarked tools for user"

    @staticmethod
    def getInputBoxNames():

        return ['Select User', 'Select tool:'] #Alternatively: [ ('box1','1'), ('box2','2') ]

    @staticmethod
    def getOptionsBox1():

        SHELVE_FN = DATA_FILES_PATH + os.sep + 'UserToolsCollection.shelve'
        s = safeshelve.open(SHELVE_FN)
        users = s.keys()
        s.close()
        return ['-----  select  -----'] + users

    @staticmethod
    def getOptionsBox2(prevChoices): # Alternatively: getOptionsBoxKey()
        if prevChoices[0] not in [None, '', '-----  select  -----']:
            linkTemplate = '<a href="%s"> %s </a><br/><br/>'
            SHELVE_FN = DATA_FILES_PATH + os.sep + 'UserToolsCollection.shelve'
            s = safeshelve.open(SHELVE_FN)
            toolLinks = [linkTemplate % (v, k) for k, v in s[prevChoices[0]].items()]
            if toolLinks:
                return '__rawstr__', '<br/><br/>' + '\n'.join(toolLinks)

#        return 'rawstr',''' <a href="http://hyperbrowser.uio.no/dev2/hyper?GALAXY_URL=http%3A//hyperbrowser.uio.no/dev2/tool_runner&tool_id=hb_test_1"> Analyze genomic tracks </a><br/><br/>
#                            <a href="http://hyperbrowser.uio.no/dev2/tool_runner?tool_id=upload1">Upload file from computer </a><br/><br/>
#                            <a href="http://hyperbrowser.uio.no/dev2/tool_runner?tool_id=Cut1"> Cut columns from a table</a><br/><br/>
#                            <a href="http://hyperbrowser.uio.no/dev2/tool_runner?tool_id=Filter1">Filter data on column using simple expression </a><br/><br/>
#                            <a href="http://hyperbrowser.uio.no/dev2/hyper?mako=generictool&tool_id=hb_create_categorical_track_tool">Merge multiple BED files into single categorical track </a><br/><br/>
#                            <a href="http://hyperbrowser.uio.no/dev2/hyper?mako=generictool&tool_id=hb_expandbed">Expand BED segments </a><br/><br/>
#                            <a href="http://hyperbrowser.uio.no/dev2/hyper?mako=generictool&tool_id=hb_visualize_tracks_as_heatmap"> Create high-resolution map of multiple track distributions along genome</a><br/><br/> '''
    @staticmethod
    def isHistoryTool():
        return False

class ModifyHistItems(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Modify history items"

    @staticmethod
    def getInputBoxNames():

        return [('genome','Genome'), ('select history items','HistItems'), ('select operations for each dataset', 'Operations'), ('specify datatype', 'Datatype'),
        ('specify number of lines to remove from top','RmTopLines'), ('Add text to top','AddTopText'), ('Add column','AddColumn')] #Alternatively: [ ('box1','1'), ('box2','2') ]

    @staticmethod
    def getOptionsBoxGenome(): # Alternatively: getOptionsBoxKey()
        return '__genome__'

    @staticmethod
    def getOptionsBoxHistItems(prevChoices): # Alternatively: getOptionsBoxKey()

        return  '__multihistory__',

    @staticmethod
    def getOptionsBoxOperations(prevChoices): # Alternatively: getOptionsBoxKey()

        return  OrderedDict([('Change datatype', False), ('Remove n lines from the top', False),
                    ('Add text to top', False), ('Add column', False) ])


    @staticmethod
    def getOptionsBoxDatatype(prevChoices): # Alternatively: getOptionsBoxKey()
        if prevChoices.Operations.get('Change datatype', False): return ''


    @staticmethod
    def getOptionsBoxRmTopLines(prevChoices): # Alternatively: getOptionsBoxKey()
        if prevChoices.Operations.get('Remove n lines from the top', False): return ''




    @staticmethod
    def getOptionsBoxAddTopText(prevChoices): # Alternatively: getOptionsBoxKey()
        if prevChoices.Operations.get('Add text to top', False): return '', 10, False


    @staticmethod
    def getOptionsBoxAddColumn(prevChoices): # Alternatively: getOptionsBoxKey()
        if prevChoices.Operations.get('Add column', False): return ''



    @classmethod
    def makeModifiedLineFunc(cls, operations):
        removeFromTop, addToTop, addColumn = operations

        ind='    '
        codeTab = ['removeFromTop, addToTop, addColumn = operations']
        if removeFromTop:
            codeTab += ['for i in xrange(%s):'%removeFromTop, ind+'lines.readline()']
        if addToTop:
            codeTab += ['for i in  addToTop.splitlines():', ind+'yield i']
        codeTab.append('for line in lines:')
        if addColumn:
            addColumn = [v.strip() for v in addColumn.split(',')]if addColumn else ['','']
            index, colData = int(addColumn[0]), addColumn[1]
            codeTab.insert(-1, "colData = addColumn.split(',')[-1].strip()")
            codeTab += [ind+"lineTab = line.split('\\t')",   ind+"lineTab.insert(%i,colData)"%index,   ind+"'\\t'.join(lineTab)",ind+'yield line']
        else:
            codeTab.append(ind+'yield line')
        print 'def getModifiedLine(lines, operations):\n' + '\n'.join([ind+v for v in codeTab])
        return 'def getModifiedLine(lines, operations):\n' + '\n'.join([ind+v for v in codeTab])

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        genome, histItemDict, operationDict, setDatatype, removeFromTop, addToTop, addColumn = choices
        #utfil = open(galaxyFn, 'w')
        start = time()
        print 'started run at:', start
        for histItem in histItemDict.values():
            galaxyTN = histItem.split(':')
            label = ExternalTrackManager.extractNameFromHistoryTN(galaxyTN)
            dataType = setDatatype if setDatatype else galaxyTN[1]#ExternalTrackManager.extractFileSuffixFromGalaxyTN(galaxyTN)
            filename = galaxyTN[2]#ExternalTrackManager.extractFnFromGalaxyTN(galaxyTN)

            exec cls.makeModifiedLineFunc(choices[4:])

            output_filename = cls.makeHistElement(galaxyExt=dataType, title=str(label))
            with open(output_filename, 'wb') as utfil:
                for modLine in getModifiedLine(open(filename), choices[4:]):
                    utfil.write(modLine)

        print 'run finished running at time: ', time(), time() - start




        #from quick.util.CommonFunctions import changedWorkingDir
        #from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
        #import os
        #print cls.runParams
        #return True
        #filePaths = [v.strip() for v in choices[0].split('\n') if v]
        #for index, filePath in enumerate(filePaths):
        #    fileName = filePath.split('/')[-1] if filePath.find('/')>-1 else filePath
        #    if filePath.split('.')[-1]!='gz':
        #        output_filename = cls.makeHistElement(title=fileName) if index>0 else galaxyFn
        #        outputFile = open(output_filename, 'wb')
        #        for line in open(filePath, 'rb'):
        #            outputFile.write(line)
        #    else:
        #        runPath = GalaxyRunSpecificFile([fileName], galaxyFn).getDiskPath(ensurePath=True)
        #
        #        os.system('cp %s %s' % (filePath, runPath))
        #        fileDir = filePath.replace(fileName, '')
        #        with changedWorkingDir(fileDir):
        #            os.system('tar -zxvf %s'%fileName)
        #            output_filename = cls.makeHistElement(title=fileName) if index>0 else galaxyFn
        #            outputFile = open(output_filename, 'wb')
        #            for root, dirs, files in os.walk('.'): # Walk directory tree
        #                print>>outputFile,  str(root) +'\n\t' + str(dirs)+'\n\t' + str(files)
        #

    @staticmethod
    def validateAndReturnErrors(choices):
        pass

    @staticmethod
    def getOutputFormat(choices=None):
        return 'txt'

class UploadFromInvitro(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "uploat files to history elements form invitro"

    @staticmethod
    def getInputBoxNames():

        return ['specify invitro paths to files (one file pr line)'] #Alternatively: [ ('box1','1'), ('box2','2') ]

    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey()

        return '',10, False

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        from quick.util.CommonFunctions import changedWorkingDir
        from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
        import os
        filePaths = [v.strip() for v in choices[0].split('\n') if v]
        for index, filePath in enumerate(filePaths):
            fileName = filePath.split('/')[-1] if filePath.find('/')>-1 else filePath
            if filePath.split('.')[-1]!='gz':
                output_filename = cls.makeHistElement(title=fileName) if index>0 else galaxyFn
                outputFile = open(output_filename, 'wb')
                for line in open(filePath, 'rb'):
                    outputFile.write(line)
            else:
                runPath = GalaxyRunSpecificFile([fileName], galaxyFn).getDiskPath(ensurePath=True)

                os.system('cp %s %s' % (filePath, runPath))
                fileDir = filePath.replace(fileName, '')
                with changedWorkingDir(fileDir):
                    os.system('tar -zxvf %s'%fileName)
                    output_filename = cls.makeHistElement(title=fileName) if index>0 else galaxyFn
                    outputFile = open(output_filename, 'wb')
                    for root, dirs, files in os.walk('.'): # Walk directory tree
                        print>>outputFile,  str(root) +'\n\t' + str(dirs)+'\n\t' + str(files)



class ShowParams(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Test Show params"

    @staticmethod
    def getInputBoxNames():

        return ['Select genome', 'write something'] #Alternatively: [ ('box1','1'), ('box2','2') ]


    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey()

        return '__genome__'

    @staticmethod
    def getOptionsBox2(prevChoices): # Alternatively: getOptionsBoxKey()

        return ''

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        print '<h1>Hello World</h1>'

        label = 'Newly created dataset'
        title = 'My new dataset'
        galaxy_ext = 'html'
        for i in range(2):
            output_filename = cls.makeHistElement()
            open(output_filename, 'wb').write('<h1>'+choices[1]+' (loop number %i)'%i+'</h1>')



class ShowScreencast(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Show screencast for topic"

    @staticmethod
    def getInputBoxNames():

        return ['select genome', 'Select track source'] #Alternatively: [ ('box1','1'), ('box2','2') ]

    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey()

        return ['-----  Select  -----', 'Getting started: Galaxy 101', 'Upload File from your computer', 'Share and publish histories', 'Managing histories',\
                'Ftp upload', 'FASTQ Prep Illumina tutorial', 'Adding custom genomes', 'Tool integration']

    @staticmethod
    def getOptionsBox2(prevChoices):
        urlADict = {'Getting started: Galaxy 101':'http://screencast.g2.bx.psu.edu/galaxy101/movie.f4v',\
            'Upload File from your computer':'http://screencast.g2.bx.psu.edu/usinggalaxy_upload/upload.flv',\
                   'Share and publish histories':'http://screencast.g2.bx.psu.edu/usinggalaxy_share_publish/share_publish.flv',\
                   'Managing histories':'http://screencast.g2.bx.psu.edu/usinggalaxy_managing_histories/managing_histories.flv',\
                   'Ftp upload':'http://screencast.g2.bx.psu.edu/quickie_17_ftp_upload/qk17.flv',\
                   'FASTQ Prep Illumina tutorial': 'http://screencast.g2.bx.psu.edu/usinggalaxy_fastq_prep/fastq_prep.flv',\
                   'Adding custom genomes':'http://screencast.g2.bx.psu.edu/usinggalaxy_custom_genomes/custom_genomes.flv'}

        urlBDict = {'Tool integration':'http://screencast.g2.bx.psu.edu/toolIntegration/toolIntegration.mov'}

        if prevChoices[-2] and prevChoices[-2] not in [None, '', '-----  Select  -----']:
            a = """<!-- include flowplayer JavaScript file -->
<script src="http://screencast.g2.bx.psu.edu/flowplayer/flowplayer-3.1.4.min.js"></script>

<h1 align="center"><b>%s</b></h1>
<div id="player" style="width:640;height:480"></div>

<script>
$f("player", "http://screencast.g2.bx.psu.edu/flowplayer/flowplayer-3.1.5.swf", {
    clip: {
        url: '%s',
        scaling: 'org'
    }
});
</script>"""
            b = """<script src="http://www.apple.com/library/quicktime/scripts/ac_quicktime.js" language="JavaScript" type="text/javascript"></script>
<script src="http://www.apple.com/library/quicktime/scripts/qtp_library.js" language="JavaScript" type="text/javascript"></script>
<h1 align="center"><b>%s</b></h1>
<div class="screencastBox section" id="screencasts">
<table width="100%%" border="0" height="100%%">
<tr>
<td valign="middle" align="center">

<script type="text/javascript"><!--
        QT_WritePoster_XHTML('Click to Play', 'toolIntegration-poster.jpg',
                'toolIntegration.mov',
                '675', '496', '',
                'controller', 'true',
                'autoplay', 'true',
                'bgcolor', 'black',
                'scale', 'aspect');
//-->
</script>
<noscript>
<object width="675" height="496" classid="clsid:02BF25D5-8C17-4B23-BC80-D3488ABDDC6B" codebase="http://www.apple.com/qtactivex/qtplugin.cab">
        <param name="src" value="toolIntegration-poster.jpg" />
        <param name="href" value="%s" />
        <param name="target" value="myself" />
        <param name="controller" value="false" />
        <param name="autoplay" value="false" />
        <param name="scale" value="aspect" />
        <embed width="675" height="496" type="video/quicktime" pluginspage="http://www.apple.com/quicktime/download/"
                src="toolIntegration-poster.jpg"
                href="%s"
                target="myself"
                controller="false"
                autoplay="true"
                scale="aspect">
        </embed>
</object>
</noscript>"""
            name = prevChoices[-2]
            html = a % (name, urlADict[name]) if urlADict.has_key(name) else b % (name, urlBDict[name], urlBDict[name])
            return '__rawstr__', html, False

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        pass

    @staticmethod
    def isHistoryTool():
        return False

class MakeVennDiagram(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Make Venn diagram from bed files"

    @staticmethod
    def getInputBoxNames():

        return ['select genome', 'Select track source','select track', 'Select track source', 'select track', 'Select track source', 'select track', 'Select track source', 'select track', 'Select track source', 'select track'] #Alternatively: [ ('box1','1'), ('box2','2') ]

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None

    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey()

        return '__genome__'

    @staticmethod
    def getOptionsBox2(prevChoices):

        return '__multihistory__','bed','category.bed','valued.bed','bedgraph', 'gtrack'

    @staticmethod
    def getOptionsBox3(prevChoices): # Alternatively: getOptionsBoxKey()

        return ['no','yes']

    @staticmethod
    def getOptionsBox4(prevChoices):
        if prevChoices[-2] == 'yes':
            return '__track__'

    @staticmethod
    def getOptionsBox5(prevChoices): # Alternatively: getOptionsBoxKey()

        if prevChoices[-2] and prevChoices[-2] != '-----  Select  -----':
            return '__track__'

    @staticmethod
    def getOptionsBox6(prevChoices): # Alternatively: getOptionsBoxKey()
        if prevChoices[-2] and prevChoices[-2] != '-----  Select  -----':
            return '__track__'

    @staticmethod
    def getOptionsBox7(prevChoices):

        if prevChoices[-2] and prevChoices[-2] != '-----  Select  -----':
            return '__track__'

    @staticmethod
    def getOptionsBox8(prevChoices): # Alternatively: getOptionsBoxKey()

        if prevChoices[-2] and prevChoices[-2] != '-----  Select  -----':
            return '__track__'

    @staticmethod
    def getOptionsBox9(prevChoices):

        if prevChoices[-2] and prevChoices[-2] != '-----  Select  -----':
            return '__track__'

    @staticmethod
    def getOptionsBox10(prevChoices): # Alternatively: getOptionsBoxKey()
        if prevChoices[-2] and prevChoices[-2] != '-----  Select  -----':
            return '__track__'

    @staticmethod
    def getOptionsBox11(prevChoices): # Alternatively: getOptionsBoxKey()

        if prevChoices[-2] and prevChoices[-2] != '-----  Select  -----':
            return '__track__'



    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        from quick.application.ExternalTrackManager import ExternalTrackManager
        from collections import defaultdict
        from gold.origdata.BedGenomeElementSource import BedGenomeElementSource, BedCategoryGenomeElementSource
        from gold.origdata.GtrackGenomeElementSource import GtrackGenomeElementSource
        from gold.origdata.TrackGenomeElementSource import FullTrackGenomeElementSource
        import itertools
        from urllib import unquote
        print choices

        genome = choices[0]
        geSourceList, labelNames = [], []
        selectedHists = [unquote(val).split(':') for id,val in choices[1].iteritems() if val]
        selectedHists += [v.split(':')for v in choices[2:]if v not in ['-----  Select  -----', 'no', 'yes', None,'']]
        for track in selectedHists:
            try:
                fileType = ExternalTrackManager.extractFileSuffixFromGalaxyTN(track)
                fn = ExternalTrackManager.extractFnFromGalaxyTN(track)
                if fileType == 'category.bed':
                    geSourceList.append(BedCategoryGenomeElementSource(fn))
                elif fileType == 'gtrack':
                    geSourceList.append(GtrackGenomeElementSource(fn))
                else:
                    geSourceList.append(BedGenomeElementSource(fn))

                labelNames.append(ExternalTrackManager.extractNameFromHistoryTN(track))
            except:
                geSourceList.append(FullTrackGenomeElementSource(genome, track, allowOverlaps=False))
                #labelNames.append(track[-1])
                labelNames.append(':'.join(track))

        primeList = [2,3,5,7,11, 13,17,19,23,29,31,37,41,43,47,53,59]
        resultCounter = defaultdict(int)
        posDict    = defaultdict(list)
        catDict  = defaultdict(list)

        debugstring = 'debug out:'

        for index, geSource in enumerate(geSourceList):
            primeNum = primeList[index]
            #if isinstance(fn, basestring):
            #    for line in open(fn):
            #        row = line.split()
            #        posDict[row[0]] += [int(v) for v in row[1:3]]
            #        catDict[row[0]] += [primeNum, -primeNum]
            #else:
            #   geSource = FullTrackGenomeElementSource(genome, fn, allowOverlaps=False)
            prevEnd = -1
            prevChr = ''
            for ge in geSource:
                #if prevChr == ge.chr and prevEnd>=ge.start:
                #        prevEnd = max(prevEnd, ge.end)
                #        posDict[ge.chr][-1] = prevEnd
                #        continue

                posDict[ge.chr] += [ge.start, ge.end]
                catDict[ge.chr] += [primeNum, -primeNum]
                prevEnd = ge.end
                prevChr = ge.chr

        #if len(geSourceList)>5:
        #    sf = GalaxyRunSpecificFile(['all_tracks.category.bed'], galaxyFn)
        #    utfil = open(sf.getDiskPath(ensurePath=True),'w')
        #    for chrom in posDict.keys():
        #        for i in range(1, len(posDict[chrom]), 2):
        #            print>>utfil, '%s\t%i\t%i\t%i' % (chrom, posDict[chrom][i-1], posDict[chrom][i], catDict[chrom][i-1])
        #    utfil.close()
        #
        #    galaxyTN = ['galaxy', 'category.bed', sf.getDiskPath(), 'All%20selected%20tracks']
        #    externTrack = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, galaxyTN, printErrors=True, raiseIfAnyWarnings=False)
        #
        #    from quick.application.GalaxyInterface import GalaxyInterface
        #    import gold.application.StatRunner
        #    analysisDef = 'dummy -> VennDataStat'
        #    binSpec = '*'
        #    regSpec = '*'


            ##if ProcTrackOptions.isValidTrack(genome, tn.split(':'), fullAccess=True):
            #resultDict = GalaxyInterface.runManual([externTrack, None], analysisDef, regSpec, binSpec, genome, galaxyFn, printResults=False, printProgress=False)
            #results = resultDict.getGlobalResult()
            #print results
            #return
            ##for k, v in resultDict.items():
            ##    res = v['Result']
        debugstring += 'posDict elements/2: ' + str(sum(len(v) for v in posDict.itervalues())/2)+'\n'
        debugstring += 'catDict elements/2: ' + str(sum(len(v) for v in catDict.itervalues())/2)+'\n'

        for chrom in posDict.keys():
            indxSortedList = sorted(range(len(posDict[chrom])), key=posDict[chrom].__getitem__)

            #sortedPos =[posDict[chrom][v] for v in indxSortedList]
            posList = posDict[chrom]
            catList = catDict[chrom]
            catCoverageDepth = defaultdict(int)

            currentState = 1
            currentPos = 0
            #print posList
            #print catList
            for indx in indxSortedList:
                pos = posList[indx]
                primeVal = catList[indx]
                #print 'pos, primeVal: ', pos, primeVal
                #print 'resultCounter: ', resultCounter
                if currentPos != pos:
                    resultCounter[abs(currentState)] += pos-currentPos
                    #debugstring +='resultCounter='+str(resultCounter)+ ' currentPos='+ str(currentPos) + '    pos='+str(pos)+ '   chrom='+str(chrom)+  '   primeVal='+str(primeVal)+ '    catCoverageDepth='+str(catCoverageDepth) +'<br/>'
                    #print 'resultCounter,currentState,  pos and currentPos',abs(currentState),':',  pos, currentPos
                    currentPos=pos

                if primeVal<0:
                    catCoverageDepth[abs(primeVal)] -= 1
                    if catCoverageDepth[abs(primeVal)] == 0:
                        currentState/=primeVal
                else:
                    catCoverageDepth[primeVal] += 1
                    if catCoverageDepth[primeVal] == 1:
                        currentState*=primeVal

        debugstring += 'resultCounter: ' + str(resultCounter)+'\n'
        #print 'resultCounter: ', resultCounter
        htmlMal = '''
<html>
    <head>
<style>
body{ font-family:Arial, Helvetica, sans-serif;}
</style>

        <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>

        <!--script type="text/javascript" src="jquery.venny_hbmod.js"></script-->
        <!--script type="text/javascript" src="vennydict.js"></script-->
        <script type="text/javascript" src="http://hyperbrowser.uio.no/dev2/static/hyperbrowser/files/jsscripts/jquery.venny_hbmod.js"></script>
        <script language="Javascript">

        var series =
        { name: {%s}, data: {%s} };
        //testseries //included in vennydict.js
        //{"data": {"": 2, "A": 1, "AB": 0, "ABC": 0, "AC": 0, "B": 1, "BC": 2, "C": 1}, "name": {"A": "ve", "B": "vegarBBB", "C": "vegCCC"}}

        if ('' in series.data)
            delete series.data['']

        //remove common start of name.
        var catnames = new Array();
        for(key in series.name)catnames.push(series.name[key])
        var catprefix = sharedStart(catnames)
        for(key in series.name)
            series.name[key]=series.name[key].substring(catprefix.length)

        //found http://stackoverflow.com/questions/1916218/find-the-longest-common-starting-substring-in-a-set-of-strings
        function sharedStart(array)
        {
            var A= array.slice(0).sort();
            var word1= A[0];
            var word2= A[A.length-1];
            var i= 0;
            while(word1.charAt(i)== word2.charAt(i))++i;
            return word1.substring(0, i);
        }

        var selectedseries = series
        var lastignoredstring=''


     /*
         Make table with form elements based on the series.
         Update (i.e. draw venn if 5 or less categories.)
     */
     function makecontent()
     {

         var categorycoverage = calccategorycoverage(series)
         var catcount = Object.keys(series.name).length
         var ret =''
         for(var i=0;i<catcount;i++)
         {
             var thiskey = Object.keys(series.name)[i]
             var radiostring = ''
              radiostring  = '<td><input type="radio" name="' + thiskey + '" id="' + thiskey + 'in"     value="in"      onclick="updatecount()"   checked/></td>'
              radiostring += '<td><input type="radio" name="' + thiskey + '" id="' + thiskey + 'out"    value="out"    onclick="updatecount()"          /></td>'
              radiostring += '<td><input type="radio" name="' + thiskey + '" id="' + thiskey + 'ignore" value="ignore" onclick="updatecount()"          /></td>'
             ret += '<tr>'+radiostring+'</td>'
             ret += '<td><input type="text" size="125" id="name_'+thiskey+'" value="'+series.name[thiskey]+'" onchange="updatecount()"/>'
             ret += '<td>'+categorycoverage[thiskey]+'</td></tr>'
             //ret += '<td>'+33+'</td></tr>'
         }
         document.getElementById("selecttable").innerHTML = document.getElementById("selecttable").innerHTML+ret
         if(catprefix.length>0)
             document.getElementById("catprefix").innerHTML = ' ( from '+catprefix + ' ) '

         updatecount()
     }

     /*
         Count the base pairs in each category. Done once initially and presented in table.
     */
     function calccategorycoverage(thisseries)
     {
         var ret = {};
         for(var thisname in thisseries.name)
             ret[thisname]=0
         for(var key in thisseries.data)
         {
             for (var i = 0; i < key.length; i++)
                 ret[key[i]] += thisseries.data[key]
         }
         return(ret)
     }

     /*
         Main function run each time input user input changes.
         Counts the numer of base pairs that complies to the selected categories.
         Draw the venn diagram if 5 or less categories are used.
     */
     function updatecount()
     {
         var inarray = getselected('in')
         var outarray= getselected('out')
         var ignorearray = getselected('ignore')

         if(lastignoredstring != ignorearray.join(''))
         {
             selectedseries = createnewseries(ignorearray)
         }
         lastignoredstring = ignorearray.join('')

        document.getElementById("counttext").innerHTML = 'Base pairs covered by selection: <b style="font-size:xx-large;">' + selectedseries.data[inarray.join('')] + '</b>, ' +(inarray.length+outarray.length) + ' tracks used.'

         if( Object.keys(selectedseries.name).length < 6 && Object.keys(selectedseries.name).length >0)
         {
             var vennysafeseries = translatekeys(selectedseries, ignorearray)

            // The venny function call with an unfamiliar syntax, but seems to work.
                 $(document).ready(function(){
                  $('#vennplot').venny({
            series: [vennysafeseries]
              });
            });

        }
        else
        {
            document.getElementById("vennplot").innerHTML = 'Too many categories for drawing venn-diagram (max 5).'
        }

     }

     /*
         Workaround since venny needed a series without missing letters in the keys.(must have ABC and not ADE as it will be if BC are ignored.)
         Runs through all the keys and swap letters so they are A,B,C for name and data.
         This function can for sure be made quicker. Or not needed at all if venny was smarter.
     */
     function translatekeys(unsafeseries,ignore)
     {
         var matchstring = RegExp('['+ignore.join('')+']', 'g')
         var includedkeys = Object.keys(series.name).join('')
         includedkeys = includedkeys.replace(matchstring,'')
         var allowedkeys = Object.keys(series.name).join('').substring(0,includedkeys.length)

         var newseries = { name:{}, data:{}}
         for(var i=0;i< allowedkeys.length;i++)
        {
            var elmid = 'name_'+includedkeys[i]
            newseries.name[allowedkeys[i]] = document.getElementById(elmid).value
        }

        translatedict = {}
        for(var i=0;i<includedkeys.length;i++)
            translatedict[includedkeys[i]] = allowedkeys[i]

         for(var key in unsafeseries.data)
        {
            var safekey=''
                for(var i=0;i<key.length;i++)
                    safekey+=translatedict[key[i]]
            newseries.data[safekey] = unsafeseries.data[key]
        }
        return(newseries)
     }

     /*
         Creates a new series object where the ignored categories are taken out and all data with a ignored category in the key is added to the corresponding key without the ignored.
         Example: original set: ABC:50, AB:25    new set: AC:75 (50+25), if B is ignored.
     */
     function createnewseries(ignore)
     {
         var newseries = { name:{}, data:{}}
         for(var key in series.name)
        {
            if(ignore.indexOf(key)==-1)
                newseries.name[key] = series.name[key]
        }
         var matchstring = RegExp('['+ignore.join('')+']', 'g')
         for(var key in series.data)
        {
            var newkey = key.replace(matchstring,'')
            if(newkey != '')
            {
                if(!(newkey in newseries.data))
                    newseries.data[newkey] = 0
                newseries.data[newkey] += series.data[key]
            }

        }
         return(newseries)
     }
     /*
         Returns list with keys that have val selected (val ={'in','out','ignored'})
     */
     function getselected(val)
     {
         var ret = new Array();
         for(var catname in series.name)
         {
             if(document.querySelector('input[name="'+catname+'"]:checked').value==val)
                 ret.push(catname)
         }
        return(ret)
     }

     function setallcat(val)
     {
         for(var catname in series.name)
         {
             elmid = catname+val
             document.getElementById(elmid).checked=true
         }
         updatecount()
     }

    </script>
    </head>


    <body onload="makecontent()">
        <h2>Base pair overlap for tracks/categories</h2>
        <form name="catselectform">
            <table id="selecttable" border="1" cellpadding="4">
                <tr>
                    <td><a href="javascript:setallcat('in')">In</a></td><td><a href="javascript:setallcat('out')">Out</a></td><td><a href="javascript:setallcat('ignore')">Ignore</a></td>
                    <td>Category <i id="catprefix"></i></td>
                    <td>Base pairs in track</td>
                </tr>
            </table>
        </form>
        <p id="counttext"></p>
        <br/>
        <br/>
        <div class="container">
            <div id="vennplot"> . </div>
        </div>
        <!--img id="canvasImg" alt="Right click to save me!"/-->
        <p id="debug">%s</p>
    </body>
</html>



'''

        displaylabels = [str(v) for v in primeList]
        setResult = []
        numBedfiles = len(labelNames)
        labels = ['A','B','C','D','E', 'F','G','H','I','J','K','L','M','N','O','P','Q']
        labels = labels[:numBedfiles]
        #labelNames = [ExternalTrackManager.extractNameFromHistoryTN(v.split(':')) for v in choices[1:] if v]
        htmlLabels = ["%s:'%s'" % (v, labelNames[i]) for i, v in enumerate(labels)]
        labelToPrime = {'A':2,'B':3,'C':5,'D':7,'E':11, 'F':13,'G':17,'H':19,'I':23,'J':29,'K':31,'L':37,'M':41,'N':43,'O':47,'P':53,'Q':59}
        combList = []
        for v in range(1,len(geSourceList)+1):
            combList += list(itertools.combinations(labels, v))

        convertDict = dict([(v,reduce(lambda x, y: x*y,[labelToPrime[t] for t in v])) for v in combList])
        #convertDict = {('B',): 3, ('B', 'C'): 15, ('A', 'B', 'D', 'E'): 462, ('A', 'B'): 6, ('B', 'C', 'E'): 165, ('C', 'D'): 35, ('A', 'B', 'C', 'D', 'E'): 2310, ('A',): 2, ('A', 'B', 'E'): 66, ('C',): 5, ('A', 'B', 'D'): 42, ('E',): 11, ('B', 'C', 'D', 'E'): 1155, ('A', 'B', 'C', 'E'): 330, ('A', 'E'): 22, ('A', 'D', 'E'): 154, ('D', 'E'): 77, ('B', 'D', 'E'): 231, ('C', 'E'): 55, ('B', 'C', 'D'): 105, ('A', 'D'): 14, ('C', 'D', 'E'): 385, ('A', 'B', 'C', 'D'): 210, ('B', 'D'): 21, ('A', 'C', 'D', 'E'): 770, ('A', 'C', 'E'): 110, ('D',): 7, ('A', 'C', 'D'): 70, ('A', 'B', 'C'): 30, ('B', 'E'): 33, ('A', 'C'): 10}
        for item in combList:
            if all([v in labels for v in item]):
                primeVal = convertDict[item]

                strName = ''.join(list(item))
                setResult.append('%s: %i' % (strName, resultCounter[primeVal] if resultCounter.has_key(primeVal) else 0))

        utfil = open(galaxyFn, 'w')
        print>>utfil, htmlMal % (', '.join(htmlLabels), ', '.join(setResult), 'hei') # siste kan vere debugstring
        utfil.close()




    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'customhtml'



class PlotStockPrices(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Plot Stock Prices"

    @staticmethod
    def getInputBoxNames():

        return ['Select stocks'] #Alternatively: [ ('box1','1'), ('box2','2') ]

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None



    @staticmethod
    def getOptionsBox1():
        stockDict = None
        with changedWorkingDir('/hyperbrowser/standardizedTracks/days/Company stocks/Historical prices/OSE/'):
            stockDict = OrderedDict([(v, False) for v in glob.glob('*')])
        return stockDict


    #@classmethod
    #def getOptionsBox2(cls, prevChoices):
    #    return (cls.userName, 1, True)


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        #print 'username', username
        #return
        from quick.application.ProcTrackOptions import ProcTrackOptions

        from quick.application.GalaxyInterface import GalaxyInterface

        analysisDef = 'dummy [withOverlaps=no] -> MarksListStat'

        genome = 'days'
        binSpec = '*'
        regSpec = 'Days_1900_2036:36890-41423'
        tnRoot = 'Company stocks:Historical prices:OSE:'
        stockList = [k for k, v in choices[0].items() if v]


        numStocks = 0
        totalPercent = 0.0
        maxSize = 0
        resList = []
        for stock in stockList:
            tn = tnRoot + stock
            if ProcTrackOptions.isValidTrack(genome, tn.split(':'), fullAccess=True):
                resultDict = GalaxyInterface.runManual([tn.split(':')], analysisDef, regSpec, binSpec, genome, galaxyFn, printResults=False, printProgress=False)

                for k, v in resultDict.items():
                    #print stock, k, v['Result']
                    res = list(v['Result'])
                    resList.append([stock, res])
                    maxSize = max(len(res), maxSize)
            else:
                print 'this is not a valid track', tn
        resultDict = dict()
        for stockTuple in resList:

            resultDict[stockTuple[0]] = [ (index, v) for index ,v in enumerate([0]*(maxSize-len(stockTuple[-1])) + stockTuple[-1])]

        print maxSize
        print cls.makeJsonFiles(resultDict)


    @classmethod
    def makeJsonFiles(cls, resultDict):

        htmlTemplate = '''
        \n\n<link href="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/themes/base/jquery-ui.css" rel="stylesheet" type="text/css"/>\n  <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.5/jquery.min.js"></script>\n  <script src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/jquery-ui.min.js"></script>\n
        <script type='text/javascript' src='https://www.google.com/jsapi'></script>
        <script type='text/javascript'>
          google.load("visualization", "1", {packages:["corechart", "controls"]});

      </script>

        <script type="text/javascript">
        function point_it(event) {

        entryNo = 0;
        var data = %s;
        makeGooglePlot(data);
        };

      function makeGooglePlot(data){
        var dEntry = google.visualization.arrayToDataTable(data);

        var dashboard = new google.visualization.Dashboard(
             document.getElementById('dashboard'));

         var control = new google.visualization.ControlWrapper({
           'controlType': 'ChartRangeFilter',
           'containerId': 'control',
           'options': {
             // Filter by the date axis.
             'filterColumnIndex': 0,
             'ui': {
               'chartType': 'LineChart',
               'chartOptions': {
                 'chartArea': {'width': '80%%'},

               },
               'chartView': {
                 'columns': %s
               }
             }
           }
         });

         var chart = new google.visualization.ChartWrapper({
           'chartType': 'LineChart',
           'containerId': 'chart',
           'options': {
             // Use the same chart area width as the control for axis alignment.
             'chartArea': {'height': '80%%', 'width': '80%%'},
             'legend': {'position': 'right'},
             'title': 'Detailed bp coverage',
             'hAxis': {'title': 'Days since Jan 2001'},
             'vAxis': {'title': 'Price'}
           }
         });

         dashboard.bind(control, chart);
         dashboard.draw(dEntry);
      }

      //google.setOnLoadCallback(drawVisualization);
    </script>
         <h3 class="plotRegion" align="center">Region</h3>
         <br/><div id="dashboard" style="width: 1000px; height: 700px;">
         <div id="chart" style="width: 100%%; height: 500px;"></div>
         <div id="control" style="width: 100%%; height: 50px;"></div> </div>
         <script type="text/javascript">
         point_it();
         </script>'''

        namesL = sorted(resultDict.keys())#[unicode(v, errors='ignore') for v in ]
        print namesL
        valuesLL = [[k[-1] for k in resultDict[v]] for v in namesL]
        yearL = sorted([v[0] for v in resultDict.values()[-1]])
        namesL.insert(0, "x")
        print valuesLL
        print yearL
        dataList = [ [v.encode('ascii','ignore') for v in namesL] ] +  [[yearL[i]] + list(v) for i, v in enumerate(zip(*valuesLL))]
        print dataList

        return htmlTemplate % (repr(dataList), repr(range(len(namesL))))


class CalculateWeekdayProfits(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Calculate weekday profits"

    @staticmethod
    def getInputBoxNames():

        return ['select genome', 'Select stocks', 'select day'] #Alternatively: [ ('box1','1'), ('box2','2') ]

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None

    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey()

        return '__genome__'

    @staticmethod
    def getOptionsBox2(prevChoices):
        stockDict = None
        with changedWorkingDir('/hyperbrowser/standardizedTracks/days/Company stocks/Historical prices/OSE/'):
            stockDict = OrderedDict([(v, False) for v in glob.glob('*')])
        return stockDict

    @staticmethod
    def getOptionsBox3(prevChoices): # Alternatively: getOptionsBoxKey()

        return '__track__'



    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        from quick.application.ProcTrackOptions import ProcTrackOptions

        from quick.application.GalaxyInterface import GalaxyInterface
        analysisDef = 'dummy -> PercentageChangeStat'
        genome = choices[0]
        binSpec = '*'
        regSpec = 'Days_1900_2036:37000-40000'
        tnRoot = 'Company stocks:Historical prices:OSE:'
        stockList = [k for k, v in choices[1].items() if v]


        numStocks = 0
        totalPercent = 0.0
        for stock in stockList:
            tn = tnRoot + stock
            if ProcTrackOptions.isValidTrack(genome, tn.split(':'), fullAccess=True):
                resultDict = GalaxyInterface.runManual([tn.split(':'), choices[2].split(':')], analysisDef, regSpec, binSpec, 'days', galaxyFn, printResults=False, printProgress=False)

                for k, v in resultDict.items():
                    print stock, v
                    res = v['Result']
                    if res == 0.0 or res>10000:
                        continue
                    totalPercent+= v['Result']
                    numStocks += 1
            else:
                print 'this is not a valid track', tn
        print 'Average increase: ', numStocks, totalPercent, totalPercent/numStocks




        #if choices[3] == 'from history':
        #    regSpec = ExternalTrackManager.extractFileSuffixFromGalaxyTN(choices[4].split(':'))
        #    binSpec = ExternalTrackManager.extractFnFromGalaxyTN(choices[4].split(':'))
        #numBins = open(binSpec).read().count('\n')
        #if numBins>330000:
        #    gold.application.StatRunner.MAX_NUM_USER_BINS = numBins
        #
        #
        #percent = float(choices[5]) if float(choices[5])<=1.0 else float(choices[5])/100.0
        #GalaxyInterface.ALLOW_OVERLAPPING_USER_BINS = True
        #resultDict = GalaxyInterface.runManual([tn1], analysisDef, regSpec, binSpec, genome, galaxyFn, printResults=False, printProgress=True)
        #overlapRegions = [k for k, v in resultDict.items() if v['Result']>=percent]
        #with open(galaxyFn,'w') as utfil:
        #    for i in overlapRegions:
        #        print>>utfil, '\t'.join([i.chr, str(i.start), str(i.end)])



class TranslateNumbersInFile(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Translate numbers containing E-x syntax "

    @staticmethod
    def getInputBoxNames():

        return ['Select History item'] #Alternatively: [ ('box1','1'), ('box2','2') ]

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None

    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey()

        return '__history__',



    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        from quick.application.ExternalTrackManager import ExternalTrackManager
        histFn = ExternalTrackManager.extractFnFromGalaxyTN(choices[0])
        utfil = open(galaxyFn,'w')
        for line in open(histFn):
            lineTab = line.strip().split('\t')
            num = lineTab[-1]
            for ind, num in enumerate(lineTab):
                if num.find('E-')>0:
                    numTab = num.split('E-')
                    newNum = '0.' + ('0'* ( int(numTab[-1])-1 ) ) +numTab[0].split('.')[1]
                    lineTab[ind] = newNum
            print>>utfil, '\t'.join(lineTab)
        utfil.close()



    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'interval'


class CreateGCFunction(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Create GC-content function track "

    @staticmethod
    def getInputBoxNames():

        return ['Select genome','Write Output trackname'] #Alternatively: [ ('box1','1'), ('box2','2') ]

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None

    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey()

        return '__genome__'



    @staticmethod
    def getOptionsBox2(prevChoices):
        return ''


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        genome = choices[0]
        outTrackName = choices[1].split(':')

        analysisDef ='[dataStat=GcContentStat] [outTrackName=%s] -> CreateFunctionTrackStat' %  '^'.join(outTrackName)
        from quick.application.GalaxyInterface import GalaxyInterface
        #print GalaxyInterface.getHbFunctionOutputBegin(galaxyFn, withDebug=False)
        GalaxyInterface.runManual([['Sequence', 'DNA']], analysisDef, '*', '*', genome, username=username, printResults=False, printHtmlWarningMsgs=False)




    @staticmethod
    def validateAndReturnErrors(choices):

        return None


class DownloadStockPrices(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Download historical stock prices"

    @staticmethod
    def getInputBoxNames():

        return ['Select stocks to download'] #Alternatively: [ ('box1','1'), ('box2','2') ]


    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey()
        from collections import OrderedDict


        dataList = urllib2.urlopen('http://www.netfonds.no/quotes/kurs.php').read().split('<a href="ppaper.php?paper=')[1:]
        tickerList = [v.split('"left">')[1].split('<')[0] for v in dataList]
        return OrderedDict([(v, False) for v in tickerList])


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        from datetime import date
        import time
        from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
        headerMal = '##gtrack version: 1.0\n##track type: valued segments\n###genome\tseqid\tstart\tend\tvalue\tvolume'
        downloadMal = 'http://ichart.finance.yahoo.com/table.csv?s=%s.OL&a=00&b=3&c=1995&d=05&e=12&f=2013&g=d&ignore=.csv'
        stocksToDownload = [ k for k, v in choices[0].items() if v in [True, 'True']]
        start = date(1900, 1, 1)
        lineMal = 'days\tDays_1900_2036\t%i\t%i\t%s\t%s'
        for stock in stocksToDownload:
            time.sleep(1)
            print 'Downloading '+stock+' .....'
            fil = GalaxyRunSpecificFile(['Company stocks','Historical prices','OSE', stock,'download.gtrack'], galaxyFn)
            fPath = fil.getDiskPath(ensurePath=True)
            utfil = open(fPath, 'w')
            print>>utfil, headerMal
            try:
                for line in urllib2.urlopen(downloadMal % stock).read().split('\n')[1:-1]:
                    lineTab = line.split(',')
                    dateStr, volume, price = lineTab[0], lineTab[-2], lineTab[-1]
                    year, mon, day = [int(v) for v in dateStr.split('-')]
                    d1 = date(year, mon, day)
                    delta = d1 - start
                    delta.days
                    print>>utfil, lineMal % (delta.days, delta.days+1, price, volume)
            except:
                print 'Error processing stock: %s' % stock
            utfil.close()




    @staticmethod
    def validateAndReturnErrors(choices):

        return None





class BastianFirst(GeneralGuiTool):
    SHELVE_FN = DATA_FILES_PATH + os.sep + 'TrackInfo.shelve'
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Make Blast part of Bastians tool"

    @staticmethod
    def getInputBoxNames():

        return ['Select genomic reads','Select smallRNA reads'] #Alternatively: [ ('box1','1'), ('box2','2') ]

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None

    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey()

        return ('__history__',)



    @staticmethod
    def getOptionsBox2(prevChoices): # Alternatively: getOptionsBoxKey1()
        '''
        Selection box:          ['choice1','choice2']
        - Returns: string

        Text area:              'textbox' | ('textbox',1) | ('textbox',1,False)
        - Tuple syntax: (contents, height (#lines) = 1, read only flag = False)
        - Returns: string

        Password field:         '__password__'
        - Returns: string

        Genome selection box:   '__genome__'
        - Returns: string

        Track selection box:    '__track__'
        - Requires genome selection box.
        - Returns: colon-separated string denoting track name

        History selection box:  ('__history__',) | ('__history__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: colon-separated string denoting galaxy track name, as
                   specified in ExternalTrackManager.py.

        History check box list: ('__multihistory__', ) | ('__multihistory__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: OrderedDict with galaxy id as key and galaxy track name
                   as value if checked, else None.

        Hidden field:           ('__hidden__', 'Hidden value')
        - Returns: string

        Table:                  [['header1','header2'], ['cell1_1','cell1_2'], ['cell2_1','cell2_2']]
        - Returns: None

        Check box list:         OrderedDict([('key1', True), ('key2', False), ('key3', False)])
        - Returns: OrderedDict from key to selection status (bool).
        '''
        return ('__history__',)




    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        from quick.util.CommonFunctions import changedWorkingDir
        import os
        from quick.application.ExternalTrackManager import ExternalTrackManager
        from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile

        genomicReadsPath = ExternalTrackManager.extractFnFromGalaxyTN(choices[0])
        smallRNAReadsPath = ExternalTrackManager.extractFnFromGalaxyTN(choices[1])
        blastOutput = GalaxyRunSpecificFile(['blastOut.out'], galaxyFn)
        blastOutPath = blastOutput.getDiskPath(True)
        runResultFolder = blastOutPath[:blastOutPath.rfind('/')+1]


        makeDbCmd = ' makeblastdb -in %s -dbtype nucl' % genomicReadsPath
        blastCmd = 'blastn -num_threads 8 -outfmt 6 -db %s -query %s -out %s -task blastn-short' % (genomicReadsPath, smallRNAReadsPath, blastOutPath)
        with changedWorkingDir(runResultFolder):
            os.system(makeDbCmd)
            print 'running command:  ' + blastCmd
            os.system(blastCmd)




class BastianLast(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Make last part of Bastian tool "

    @staticmethod
    def getInputBoxNames():

        return ['Select genome','Path to Bastian Results'] #Alternatively: [ ('box1','1'), ('box2','2') ]

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None

    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey()

        return '__genome__'



    @staticmethod
    def getOptionsBox2(prevChoices):
        return ('__history__',)


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        from quick.util.CommonFunctions import changedWorkingDir
        import os
        from shutil import copy
        from quick.application.ExternalTrackManager import ExternalTrackManager
        from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
        import glob

        galaxyTN = choices[1].split(':')
        fn = ExternalTrackManager.extractFnFromGalaxyTN(galaxyTN)
        allContigs = GalaxyRunSpecificFile(['allcontigs.fas'], fn)
        allContigsPath = allContigs.getDiskPath(True)
        runResultFolder = allContigsPath[:allContigsPath.rfind('/')+1]

        copy('/hyperbrowser/staticFiles/bastian/atcgn_only.pl', runResultFolder)
        with changedWorkingDir(runResultFolder):
            folders = glob.glob('Velvetoutput_*')
            for folder in folders:
               allContigs.writeTextToFile(open(folder+'/contigs.fa').read(), mode='a')

            os.system('fasta_formatter -i allcontigs.fas -o allcontigs_nolinebreaks.fas')
            #"removing non-actgn-sites"
            os.system('perl atcgn_only.pl allcontigs_nolinebreaks.fas > allcontigs_nolinebreaks_actgnonly.fas')
            os.system("cat allcontigs_nolinebreaks.fas|perl -ne '$h=$_;$s=<>;chomp($h);@p=split(/_/,$h);if ($p[3]>=40){print \"$h\n$s\";}' > allcontigs_nolinebreaks.fas_plus40.fa")
            os.system("cat allcontigs_nolinebreaks.fas_plus40.fa|perl -e 'while (<>){$h=$_;chomp($h); $h =~ s/u/T/g; $h =~ s/a/A/g;$h =~ s/g/G/g;$h =~ s/c/C/g; print \"$h\n\";}'> allcontigs_nolinebreaks.fas_plus40_capital.fa")
            os.system("cd-hit-est -i allcontigs_nolinebreaks.fas_plus40.fa -o allcontigs_nolinebreaks.fas_plus40.fa_cd-hit100_EST.fa -c 1.00 -n 10 -r 1 -g 1 -T 0 -M 10000")
            os.system("fastx_renamer -n SEQ -i allcontigs_nolinebreaks.fas_plus40_capital.fa -o allcontigs_nolinebreaks.fas_plus40_capital_newname.fa")


    @staticmethod
    def validateAndReturnErrors(choices):

        return None




class TrackSearch(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Search for track in repository"

    @staticmethod
    def getInputBoxNames():

        return ['Write search string','Search Result'] #Alternatively: [ ('box1','key1'), ('box2','key2') ]



    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey1()
        '''
        Defines the type and contents of the input box. User selections are
        returned to the tools in the prevChoices and choices attributes to other
        methods. These are lists of results, one for each input box (in the
        order specified by getInputBoxOrder()).

        The input box is defined according to the following syntax:

        Selection box:          ['choice1','choice2']
        - Returns: string

        Text area:              'textbox' | ('textbox',1) | ('textbox',1,False)
        - Tuple syntax: (contents, height (#lines) = 1, read only flag = False)
        - Returns: string

        Password field:         '__password__'
        - Returns: string

        Genome selection box:   '__genome__'
        - Returns: string

        Track selection box:    '__track__'
        - Requires genome selection box.
        - Returns: colon-separated string denoting track name

        History selection box:  ('__history__',) | ('__history__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: colon-separated string denoting galaxy track name, as
                   specified in ExternalTrackManager.py.

        History check box list: ('__multihistory__', ) | ('__multihistory__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: OrderedDict with galaxy id as key and galaxy track name
                   as value if checked, else None.

        Hidden field:           ('__hidden__', 'Hidden value')
        - Returns: string

        Table:                  [['header1','header2'], ['cell1_1','cell1_2'], ['cell2_1','cell2_2']]
        - Returns: None

        Check box list:         OrderedDict([('key1', True), ('key2', False), ('key3', False)])
        - Returns: OrderedDict from key to selection status (bool).
        '''
        return ''

    @staticmethod
    def getOptionsBox2(prevChoices): # Alternatively: getOptionsBoxKey2()
        '''
        See getOptionsBox1().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''

        hg18root = '/hyperbrowser/standardizedTracks/hg18/'

        res = dict()
        #if prevChoices[-1] not in [None, '']:
        #    return repr(prevChoices[1])
        #    res = dict([(k, v) for k, v in prevChoices[-1].items() if v == True])

        if len(prevChoices[0])>2:
            wordDict = shelve.open('/hyperbrowser/standardizedTracks/cache', flag = 'c')
            if len(wordDict)<10:
                tempDict = dict()
                for root, folder, files in os.walk(hg18root):
                    value = ':'.join(root.split('/')[6])
                    if folder == []:
                        words = [i.lower() for i in value.split(':') if i!='']
                        for word in words:
                            if tempDict.has_key(word):
                                tempDict[word].append(value)
                            else:
                                wordDict[word] = [value]
                wordDict.update(tempDict)
                tempDict = None
                wordDict.sync()

            keyStr = '#'+'##'.join(wordDict.keys())+'#'


            result = set()

            matches = []


            searchStr = re.compile('#[a-z0-9\-_:;]*'+prevChoices[0].lower()+'[a-z0-9\-_:;]*#')
            for match in re.findall(searchStr, keyStr):
                matches.append(match)
                values = wordDict[match[1:-1]]
                result = result.union(values)

            wordDict.close()
            #return ('\n'.join(matches), len(matches), True)
            resList = list(result)
            falseList = [False]*len(resList)
            resDict = dict(zip(result, falseList))
            resDict.update(res)
            return resDict


    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''
        print 'Executing...'

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        return None


class SubTool(GeneralGuiTool):
    @staticmethod
    def getToolName():

        return "Test tulle items to one item"

    @staticmethod
    def getInputBoxNames():

        return ['Select history item','Select history item', 'Select history item','Select history item'] #Alternatively: [ ('box1','key1'), ('box2','key2') ]


    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey1()

        return '__genome__',

    @staticmethod
    def getOptionsBox2(prevChoices): # Alternatively: getOptionsBoxKey2()
        return '__track__'


    @staticmethod
    def getOptionsBox3(prevChoices): # Alternatively: getOptionsBoxKey1()

        return '__genome__',

    @staticmethod
    def getOptionsBox4(prevChoices): # Alternatively: getOptionsBoxKey2()
        return '__track__'


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        print 'Executing..'



    @staticmethod
    def validateAndReturnErrors(choices):
        return None





class ConcatenateHistItems(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Concatenate history items to one item"

    @staticmethod
    def getInputBoxNames():
        '''
        Specifies a list of headers for the input boxes, and implicitly also the
        number of input boxes to display on the page. The returned list can have
        two syntaxes:

            1) A list of strings denoting the headers for the input boxes in
               numerical order.
            2) A list of tuples of strings, where each tuple has
               two items: a header and a key.

        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is either a number in the range of 1 to the
        number of boxes (case 1), or the specified key (case 2).
        '''
        return ['Select history items to Concatenate', 'Specify number of lines to remove from trailing datasets'] #Alternatively: [ ('box1','key1'), ('box2','key2') ]


    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey1()
        '''
        Defines the type and contents of the input box. User selections are
        returned to the tools in the prevChoices and choices attributes to other
        methods. These are lists of results, one for each input box (in the
        order specified by getInputBoxOrder()).

        The input box is defined according to the following syntax:

        Selection box:          ['choice1','choice2']
        - Returns: string

        Text area:              'textbox' | ('textbox',1) | ('textbox',1,False)
        - Tuple syntax: (contents, height (#lines) = 1, read only flag = False)
        - Returns: string

        Password field:         '__password__'
        - Returns: string

        Genome selection box:   '__genome__'
        - Returns: string

        Track selection box:    '__track__'
        - Requires genome selection box.
        - Returns: colon-separated string denoting track name

        History selection box:  ('__history__',) | ('__history__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: colon-separated string denoting galaxy track name, as
                   specified in ExternalTrackManager.py.

        History check box list: ('__multihistory__', ) | ('__multihistory__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: OrderedDict with galaxy id as key and galaxy track name
                   as value if checked, else None.

        Hidden field:           ('__hidden__', 'Hidden value')
        - Returns: string

        Table:                  [['header1','header2'], ['cell1_1','cell1_2'], ['cell2_1','cell2_2']]
        - Returns: None

        Check box list:         OrderedDict([('key1', True), ('key2', False), ('key3', False)])
        - Returns: OrderedDict from key to selection status (bool).
        '''
        return '__multihistory__',

    @staticmethod
    def getOptionsBox2(prevChoices): # Alternatively: getOptionsBoxKey2()

        return '1'

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''
        #print 'Executing...'
        utfil = open(galaxyFn,'w')
        histItems = choices[0].values()
        numLines = int(choices[1])
        print>>utfil, open(histItems[0].split(':')[2]).read()
        for histItem in histItems[1:]:
            for line in open(histItem.split(':')[2]).readlines()[numLines:]:
                utfil.write(line)
            print>>utfil, ''

        utfil.close()

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        return None


    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'txt'


class FilterHistElOnMatchingColumns(GeneralGuiTool):
    @staticmethod
    def getToolName():

        return "Filter history item on matching columns"

    @staticmethod
    def getInputBoxNames():

        return ['Select history item','Select history item','select columns to match on(eg. c1, c3)'] #Alternatively: [ ('box1','key1'), ('box2','key2') ]


    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey1()

        return '__history__', 'bed', 'bedgraph'

    @staticmethod
    def getOptionsBox2(prevChoices): # Alternatively: getOptionsBoxKey2()

        return '__history__', 'bed', 'bedgraph'

    @staticmethod
    def getOptionsBox3(prevChoices): # Alternatively: getOptionsBoxKey2()

        return ''


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        transDict = dict([('c%i'%i, i-1)for i in range(1,100)])
        fn1 = ExternalTrackManager.extractFnFromGalaxyTN(choices[0].split(':'))
        fn2 = ExternalTrackManager.extractFnFromGalaxyTN(choices[1].split(':'))
        columnList = [transDict[v.strip()] for v in choices[2].split(',')]
        file1Dict = cls.makeDictOfFile(fn1, columnList)
        file2Dict = cls.makeDictOfFile(fn2, columnList)
        print 'len(file2Dict), len(file1Dict)', len(file2Dict), len(file1Dict)
        print file1Dict.keys()[:10], file2Dict.keys()[:10]
        sameKeys = list(set(file1Dict.keys()).intersection(set(file2Dict.keys())))
        sameKeys.sort()

        utfil = open(galaxyFn,'w')
        for key in sameKeys:
            print>>utfil, '\n'.join(file2Dict[key])

        utfil.close()

    @classmethod
    def makeDictOfFile(cls, fn, columnList):
        resDict = defaultdict(list)
        maxColumn = max(columnList)+1
        for line in open(fn):
            lineTab = line.split()
            if len(lineTab)>=maxColumn:
                key = '_'.join([lineTab[v] for v in columnList])
                resDict[key].append(line)

        return resDict

    @staticmethod
    def validateAndReturnErrors(choices):
        return None


    @staticmethod
    def getOutputFormat(choices):
        return 'bed'


class ExtractColumnsFromTrack(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Extract columns from track"

    @staticmethod
    def getInputBoxNames():

        return ['Select genome','Select track', 'Select Chromosomes', 'Select columns'] #Alternatively: [ ('box1','key1'), ('box2','key2') ]


    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey1()
        return '__genome__'

    @staticmethod
    def getOptionsBox2(prevChoices): # Alternatively: getOptionsBoxKey2()

        return '__track__'

    @staticmethod
    def getOptionsBox3(prevChoices):

        #return PROCESSED_DATA_PATH
        if prevChoices[-2] and prevChoices[0] not in [None, '----- Select -----', ]:
            genome, tn = prevChoices[0], prevChoices[1].split(':')
            if ProcTrackOptions.isValidTrack(genome, tn, True):
                filePath = PROCESSED_DATA_PATH +'/100000/noOverlaps/'+prevChoices[0]+'/'+prevChoices[-2].replace(':','/')
                tName = prevChoices[-2].split(':')
                with changedWorkingDir(filePath):

                    return OrderedDict( [(v.split('.')[0], False)  for v in glob.glob('*') if v not in ['rightIndex.int32','leftIndex.int32']] )

        #    track = PlainTrack(prevChoices[0], tName)
        #    return OrderedDict([('key1', True), ('key2', False), ('key3', False)])

    @staticmethod
    def getOptionsBox4(prevChoices):
        if prevChoices[-2]:
            if any(prevChoices[-2].values()):
                filePath = PROCESSED_DATA_PATH +'/100000/noOverlaps/'+prevChoices[0]+'/'+prevChoices[1].replace(':','/')+'/'
                key = [k for k, v in prevChoices[-2].items() if v][0]
                if os.path.isdir(filePath+key):
                    with changedWorkingDir(filePath+key):
                        return OrderedDict( [(v.split('.')[0], False)  for v in glob.glob('*') if v not in ['rightIndex.int32','leftIndex.int32']] )

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        if choices[-1]:
            utfil = open(galaxyFn,'w')
            chroms = [k for k, v in choices[2].items() if v]
            genome, tn = choices[0], choices[1].split(':')
            selections = [k for k,v in choices[3].items() if v]


            filePath = PROCESSED_DATA_PATH +'/100000/noOverlaps/'+genome+'/'+'/'.join(tn)+'/'
            for chrom in chroms:
                with changedWorkingDir(filePath+chrom):
                    filesChosen = [v.split('.') for v in glob.glob('*') if v.split('.')[0] in selections]
                    resultList, chrLength = [], 0
                    for choiceTuple in filesChosen:
                        fileContents = [str(el) for el in list(np.memmap(filesChosen[0], filesChosen[-1], mode='r'))]
                        if chrLength == 0:
                            chrLength = len(fileContents)
                            chrList = [chrom]*chrLength
                            resultList.append(chrList)
                        resultList.append(fileContents)
                    transResult = zip(*resultList)
                    for lineTuple in transResult:
                        print>>utfil, '\t'.join(lineTuple)
            utfil.close()


    @staticmethod
    def validateAndReturnErrors(choices):
        return None


    @staticmethod
    def getOutputFormat(choices):
        return 'interval'





# This is a template prototyping GUI that comes together with a corresponding
# web page.

class Make3dGtrackFiles(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Make 3D-gtrack files from .mat files"

    @staticmethod
    def getInputBoxNames():

        return ['Select genome','Specify accessible root path', 'specify chromosome ordrer(comma-seperated)'] #Alternatively: [ ('box1','key1'), ('box2','key2') ]


    @staticmethod
    def getOptionsBox1(): # Alternatively: getOptionsBoxKey1()

        return '__genome__'

    @staticmethod
    def getOptionsBox2(prevChoices): # Alternatively: getOptionsBoxKey2()
        '''
        See getOptionsBox1().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return ''

    @staticmethod
    def getOptionsBox3(prevChoices):
        return ''



    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''
        genome = choices[0]
        chrLength = GenomeInfo.getStdChrLengthDict(genome)#{'chrY': 59373566, 'chrX': 155270560, 'chr13': 115169878, 'chr12': 133851895, 'chr11': 135006516, 'chr10': 135534747, 'chr17': 81195210, 'chr16': 90354753, 'chr15': 102531392, 'chr14': 107349540, 'chr19': 59128983, 'chr18': 78077248, 'chr1': 249250621, 'chr22': 51304566, 'chr20': 63025520, 'chr21': 48129895, 'chr7': 159138663, 'chr6': 171115067, 'chr5': 180915260, 'chr4': 191154276, 'chr3': 198022430, 'chr2': 243199373, 'chr9': 141213431, 'chr8': 146364022}
        gtrackHeader = '##Track type: linked genome partition\n##Edge weights: true\n##Undirected edges: true\n###end        id        edges'
        boundRegMal = '####genome=%s;seqid=%s;start=%i;end=%i'
        edgeMal =  '%s:%s='
        binDict = {'1M':1000000, '100K':100000, '200K':200000, '500K':500000, '80K':80000, '160K':160000, '40K':40000, '20K':20000, '10K':10000}

        chromList = [v.strip() for v in choices[2].split(',')]
        prefix = chromList[0][:3]

        #constructType = 'All', 'Intra', 'Inter'
        with changedWorkingDir(choices[1]):

            for constructType in ['All','Intra', 'Inter']:
                for root, dirs, files in os.walk('.'): # Walk directory tree
                    if dirs == [] and not root.find('Gtrack')>=0:
                        print constructType, root
                        segLength = root.split('-')[-1]
                        binSize = binDict[segLength.upper()]
                        segCounter = Counter()


                        for chrom in chromList:
                            print chrom
                            resultDict = dict() #defaultdict(list)
                            chrNum = chrom.split(prefix)[-1]
                            for fil in [f for f in files if f.find('.mat')>0 and f.find(chrNum)>=0]:
                                chrs = [prefix+ v for v in fil.split('.')[:2]]
                                with open('/'.join([root, fil])) as innfil:
                                    if chrs[0] == prefix+chrNum:
                                        lineTab = [v.strip().split()[3:] for v in innfil.readlines()]
                                        resultDict['-'.join(chrs)] =lineTab
                                    elif chrs[0] != chrs[1]:
                                        lineTab = zip(*[v.strip().split()[3:] for v in innfil.readlines()])
                                        chrs.reverse()
                                        resultDict['-'.join(chrs)] =lineTab


                            nokler = resultDict.keys()
                            finalResDict = defaultdict(list)

                            for key in nokler:
                                #print key, len(resultDict[key])
                                fromId, toId = key.split('-')
                                edgeIdList = [edgeMal % (toId, str(v+1)+'*'+segLength) for v in range(len(resultDict[key][0]))]
                                for index, vals in enumerate(resultDict[key]):
                                    if constructType == 'Intra':
                                        vals = [v if edgeIdList[i].find(chrom+':')>=0 else '.' for i, v in enumerate(vals)]
                                    elif constructType == 'Inter':
                                         vals = [v if edgeIdList[i].find(chrom+':')<0 else '.' for i, v in enumerate(vals)]

                                    finalResDict[fromId+':'+str(index+1)+'*'+segLength] += zip(edgeIdList, vals)

                            try:
                                os.makedirs('Gtrack/'+constructType+'/'+root.replace('./',''))
                            except:
                                pass

                            with open('/'.join(['Gtrack',constructType,root.replace('./',''),chrom+'.gtrack']),'w') as utfil:
                                print>>utfil, gtrackHeader
                                print>>utfil, boundRegMal % (genome, chrom, 0, chrLength[chrom])
                                for i in range(1,1000000):
                                    if finalResDict.has_key(chrom+':'+str(i)+'*'+segLength):
                                        streng = ';'.join([v[0]+v[1] for v in finalResDict[chrom+':'+str(i)+'*'+segLength]])
                                        if i*binSize<chrLength[chrom]:
                                            print>>utfil,str(i*binSize)+'\t'+chrom+':'+str(i)+'*'+segLength+'\t'+streng
                                        else:
                                            print>>utfil,str(chrLength[chrom])+'\t'+chrom+':'+str(i)+'*'+segLength+'\t'+streng

                                    else:
                                        break

            tnList = choices[1].split('/tempColl/')[1].split('/')

            path = createOrigPath(genome, tnList[1:])
            copytree('Gtrack', path)

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        if choices[1] not in [None, '']:
            if choices[1].find('tempColl')<0:
                return 'The root folder must be inside the following path:  /usit/invitro/work/hyperbrowser/nosync/tempColl/'
            else:
                tnList = choices[1].split('/tempColl/')[1].split('/')
                path = createOrigPath(tnList[0], tnList[1:])
                if os.path.exists(path):
                    return 'The root path (%s) must not be present at the standardized-track area.' % ('/'.join(tnList))

            if choices[2] not in [None,'']:
                chrfasit = GenomeInfo.getChrList(choices[0])
                for chrom in [v.strip() for v in choices[2].split(',')]:
                    if not chrom in chrfasit:
                        return 'The following chromosome is wrongly specified %s.'%chrom

        return None
