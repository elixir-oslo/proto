import os
import subprocess
import sys
from StringIO import StringIO
from collections import namedtuple
from copy import copy
from functools import partial
from itertools import chain
from tempfile import NamedTemporaryFile

from gold.origdata.GtrackGenomeElementSource import GtrackGenomeElementSource
from gold.origdata.GtrackHeaderExpander import expandHeadersOfGtrackFileAndReturnComposer
from gold.track.GenomeRegion import GenomeRegion
from gold.util.CustomExceptions import InvalidFormatError
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from third_party.asteval_raise_errors import Interpreter

FileContentsInfo = namedtuple('FileContentsInfo', ['table', 'numCols', 'error'])

class TabularToGtrackTool(GeneralGuiTool):
    #DEFAULT_COLUMNS = [ 'genome', 'seqid', 'start', 'end', 'strand', 'value', 'id', 'edges']
    DEFAULT_COLUMNS = [ 'seqid', 'start', 'end', 'strand', 'value', 'id', 'edges']
    DEFAULT_3D_EXTRA_COLS = ['linked_seqid', 'linked_start', 'linked_end', 'link_weight']
    DEFAULT_3D_COLS = DEFAULT_COLUMNS[:3] + DEFAULT_3D_EXTRA_COLS
    NUM_COLUMN_FUNCTIONS = 50
    NUM_ROWS_IN_TABLE = 10

    @staticmethod
    def getToolName():
        return "Create GTrack file from unstructured tabular data"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return [('', 'basicQuestionId'), \
                ('Select input source:', 'source'), \
                ('Select tabular file:', 'history'), \
                ('Type or paste in tabular file:', 'input'), \
                ('Character to use to split lines into columns: ', 'splitChar'), \
                ('Number of lines to skip (from front):', 'numSkipLinesList'), \
                ('Type the number of lines to skip:', 'numSkipLines'), \
                ('File contents info (hidden)', 'fileContentsInfo'), \
                ('Column selection method:', 'columnSelection'), \
                ('Select GTrack file for the column specification:','colSpecFile')] + \
                [x for x in chain(*((('Select the name for column #%s:' % (i+1), 'column%s' % i), \
                                     ('Type in a custom name for column #%s:' % (i+1), 'customColumn%s' % i)) \
                    for i in xrange(TabularToGtrackTool.NUM_COLUMN_FUNCTIONS)))] + \
                [('Select a specific genome build:', 'selectGenome'), \
                 ('Genome build:', 'genome'), \
                 ('The beginning of the tabular file (without skipped rows):', 'table'), \
                 ('Create dense track type (i.e. function, step function, or genome partition):', 'createDense'), \
                 ('Generate id by:', 'idGeneration'), \
                 ('Create undirected edges:', 'undirected'), \
                 ('Create complete graph:', 'complete'), \
                 ('Current track type (based on the selected column names):', 'trackType'), \
                 ('Indexing standard used for start and end coordinates:', 'indexing'), \
                 ("Auto-correct the sequence id ('seqid') column:", 'handleSeqId'), \
                 ("Crop segments crossing sequence ends:", 'cropCrossingSegments')]

    @staticmethod
    def getOptionsBoxBasicQuestionId():
        return '__hidden__', None

    @staticmethod
    def getOptionsBoxSource(prevChoices):
        return ['Tabular file from history', 'Tabular file from input box']

    @staticmethod
    def getOptionsBoxHistory(prevChoices):
        if prevChoices.source == 'Tabular file from history':
            from galaxy.model import datatypes_registry
            return ('__history__', type(datatypes_registry.get_datatype_by_extension('tabular')))

    @staticmethod
    def getOptionsBoxInput(prevChoices):
        if prevChoices.source == 'Tabular file from input box':
            return '', 10

    @staticmethod
    def getOptionsBoxSplitChar(prevChoices):
        if prevChoices.history or prevChoices.input:
            return ['Tab', 'Space', 'Any whitespace']

    @staticmethod
    def _getSplitChar(prevChoices):
        splitChar = prevChoices.splitChar
        if splitChar == 'Tab':
            return '\t'
        elif splitChar == 'Space':
            return ' '
        else:
            return None

    @staticmethod
    def getOptionsBoxNumSkipLinesList(prevChoices):
        if prevChoices.history or prevChoices.input:
            return [str(x) for x in range(11)] + ['-- other --']

    @staticmethod
    def getOptionsBoxNumSkipLines(prevChoices):
        if prevChoices.numSkipLinesList == '-- other --':
            return '0'

    @staticmethod
    def _getNumSkipLines(prevChoices):
        if prevChoices.numSkipLinesList != '-- other --':
            numSkipLines = int(prevChoices.numSkipLinesList)
        else:
            try:
                numSkipLines = int(prevChoices.numSkipLines.strip())
            except:
                return

        return numSkipLines

    @staticmethod
    def getOptionsBoxFileContentsInfo(prevChoices):
        if prevChoices.history or prevChoices.input:
            if prevChoices.history:
                inputFile = open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.history.split(':')), 'r')
            else:
                inputFile = StringIO(prevChoices.input)

            for i in xrange(TabularToGtrackTool._getNumSkipLines(prevChoices)):
                inputFile.readline()

            table = []
            splitChar = TabularToGtrackTool._getSplitChar(prevChoices)
            numCols = None
            error = None
            for i,line in enumerate(inputFile):
                row = [x.strip() for x in line.strip().split(splitChar)]
                if numCols == None:
                    numCols = len(row)
                elif numCols != len(row):
                    numCols = max(numCols, len(row))
#                    error = 'Error: the number of columns varies over the rows of the tabular file.'

                table.append(row)
                if i == TabularToGtrackTool.NUM_ROWS_IN_TABLE:
                    break

            numCols = max(len(row) for row in table) if len(table) > 0 else 0

            if error is None:
                if numCols > TabularToGtrackTool.NUM_COLUMN_FUNCTIONS:
                    error = 'Error: the tabular file has more columns than is allowed by the tool (%s > %s).' % (numCols, TabularToGtrackTool.NUM_COLUMN_FUNCTIONS)

            return '__hidden__', FileContentsInfo(table=table, numCols=numCols, error=error)

    @staticmethod
    def getOptionsBoxColumnSelection(prevChoices):
        if prevChoices.history or prevChoices.input:
            return ['Select individual columns', 'Base columns on existing GTrack file', 'Default 3D columns (Hi-C)', 'Default 3D columns (ChIA-PET)']

    @staticmethod
    def getOptionsBoxColSpecFile(prevChoices):
        if prevChoices.columnSelection == 'Base columns on existing GTrack file':
            return '__history__', 'gtrack'

    @classmethod
    def setupColumnFunctions(cls):
        for i in xrange(cls.NUM_COLUMN_FUNCTIONS):
            setattr(cls, 'getOptionsBoxColumn%s' % i, partial(cls.getColumnList, index=i))
            setattr(cls, 'getOptionsBoxCustomColumn%s' % i, partial(cls.getCustomColumn, index=i))

    @classmethod
    def _getAllPrevColumnChoices(cls, prevChoices, index):
        return [getattr(prevChoices, 'column%s' % i) for i in xrange(index)]

    @classmethod
    def getColumnList(cls, prevChoices, index):
        if (prevChoices.history or prevChoices.input) and prevChoices.columnSelection != 'Base columns on existing GTrack file':
            defaultCols = copy(cls.DEFAULT_COLUMNS)

            if prevChoices.columnSelection.startswith('Default 3D columns'):
                defaultCols += cls.DEFAULT_3D_EXTRA_COLS

            fileContentsInfo = TabularToGtrackTool._getFileContentsInfo(prevChoices)
            if fileContentsInfo and fileContentsInfo.error is None and index < fileContentsInfo.numCols:
                prevColChoices = cls._getAllPrevColumnChoices(prevChoices, index)

                colList = []
                if prevChoices.columnSelection.startswith('Default 3D columns'):
                    if index < len(cls.DEFAULT_3D_COLS):
                        col = cls.DEFAULT_3D_COLS[index]
                        if col not in prevColChoices:
                            colList = [col]
                            prevColChoices += [col, 'id', 'edges']

                colList += ['-- ignore --'] + \
                           [x for x in defaultCols if x not in prevColChoices] + \
                           ['-- custom --']
                return colList

    @classmethod
    def getCustomColumn(cls, prevChoices, index):
        if (prevChoices.history or prevChoices.input) and prevChoices.columnSelection != 'Base columns on existing GTrack file':
            return None if getattr(prevChoices, 'column%s' % index) !=  '-- custom --' else ''

    @staticmethod
    def _getFileContentsInfo(prevChoices):
        fileContentsInfo = prevChoices.fileContentsInfo
        if isinstance(fileContentsInfo, basestring):
            aeval = Interpreter()
            aeval.symtable['FileContentsInfo'] = FileContentsInfo
            fileContentsInfo = aeval(fileContentsInfo)
        return fileContentsInfo

    @staticmethod
    def getOptionsBoxSelectGenome(prevChoices):
        if prevChoices.history or prevChoices.input:
            return ['No', 'Yes']

    @staticmethod
    def getOptionsBoxGenome(prevChoices):
        if prevChoices.selectGenome == 'Yes':
            return "__genome__"

    @staticmethod
    def _getHeaders(prevChoices):
        numCols = TabularToGtrackTool._getFileContentsInfo(prevChoices).numCols
        if prevChoices.columnSelection != 'Base columns on existing GTrack file':
            header = []
            for i in xrange(numCols):
                if hasattr(prevChoices, 'column%s' % i):
                    colHeader = getattr(prevChoices, 'column%s' % i)
                    if colHeader is None or colHeader == '-- ignore --':
                        header.append('')
                    elif colHeader == '-- custom --':
                        header.append(getattr(prevChoices, 'customColumn%s' % i).strip())
                    else:
                        header.append(colHeader)
                else:
                    header.append('')
            return header
        else:
            genome = prevChoices.genome if prevChoices.selectGenome == 'Yes' else None
            try:
                inFn = ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.colSpecFile.split(':'))
                geSource = GtrackGenomeElementSource(inFn, genome=genome)
                geSource.parseFirstDataLine()
                return geSource.getColumns()[:numCols]
            except Exception, e:
                return []

    @staticmethod
    def getOptionsBoxTable(prevChoices):
        if prevChoices.columnSelection == 'Base columns on existing GTrack file' and not prevChoices.colSpecFile:
            return

        if prevChoices.history or prevChoices.input:
            fileContentsInfo = TabularToGtrackTool._getFileContentsInfo(prevChoices)
            table = copy(fileContentsInfo.table)
            numCols = fileContentsInfo.numCols

            table = [["%s.&nbsp;%s" % (i+1, header) for i, header in
                      enumerate(TabularToGtrackTool._getHeaders(prevChoices))]] + table
            for row in table:
                if len(row) < numCols:
                    row += [''] * (numCols - len(row))

            return table

    @staticmethod
    def getOptionsBoxCreateDense(prevChoices):
        if prevChoices.columnSelection == 'Base columns on existing GTrack file' and not prevChoices.colSpecFile:
            return

        if prevChoices.history or prevChoices.input:
            if TabularToGtrackTool._getFileContentsInfo(prevChoices).error is None:
                if prevChoices.columnSelection == 'Default 3D columns (Hi-C)':
                    return ['Yes', 'No']
                else:
                    return ['No', 'Yes']

    @staticmethod
    def _create3dData(prevChoices):
        headers = TabularToGtrackTool._getHeaders(prevChoices)
        return all(x in headers for x in ['linked_seqid', 'linked_start'])

    @staticmethod
    def getOptionsBoxIdGeneration(prevChoices):
        if prevChoices.history or prevChoices.input:
            if TabularToGtrackTool._create3dData(prevChoices):
                if TabularToGtrackTool._getFileContentsInfo(prevChoices).error is None:
                    return ['Counting', 'Using genome region']

    @staticmethod
    def getOptionsBoxUndirected(prevChoices):
        if prevChoices.history or prevChoices.input:
            if TabularToGtrackTool._create3dData(prevChoices):
                if TabularToGtrackTool._getFileContentsInfo(prevChoices).error is None:
                    return ['Yes', 'No']

    @staticmethod
    def getOptionsBoxComplete(prevChoices):
        if prevChoices.history or prevChoices.input:
            if TabularToGtrackTool._create3dData(prevChoices):
                if TabularToGtrackTool._getFileContentsInfo(prevChoices).error is None:
                    if prevChoices.columnSelection == 'Default 3D columns (Hi-C)':
                        return ['Yes', 'No']
                    else:
                        return ['No', 'Yes']

    @staticmethod
    def getOptionsBoxTrackType(prevChoices):
        if prevChoices.columnSelection == 'Base columns on existing GTrack file' and not prevChoices.colSpecFile:
            return

        if prevChoices.history or prevChoices.input:
            headers = set(TabularToGtrackTool._getHeaders(prevChoices))
            if prevChoices.createDense == 'Yes' and 'start' in headers:
                headers.remove('start')

            if not 'edges' in headers and TabularToGtrackTool._create3dData(prevChoices):
                headers.add('edges')

            trackType = GtrackGenomeElementSource.getTrackTypeFromColumnSpec(headers)
            if trackType is not None:
                words = [x.capitalize() for x in trackType.split()]
                abbrv = ''.join([x[0] for x in words])
                fullTrackType = ' '.join(words) + ' (%s)' % abbrv
                return (fullTrackType, 1, True)

    @staticmethod
    def getOptionsBoxIndexing(prevChoices):
        if prevChoices.history or prevChoices.input:
            if TabularToGtrackTool._getFileContentsInfo(prevChoices).error is None:
                return ['0-indexed, end exclusive', '1-indexed, end inclusive']

    @staticmethod
    def getOptionsBoxHandleSeqId(prevChoices):
        if (prevChoices.history or prevChoices.input):
            if TabularToGtrackTool._getFileContentsInfo(prevChoices).error is None:
                return ['No', 'Yes, auto-correct to the best match in the genome build']

    @staticmethod
    def getOptionsBoxCropCrossingSegments(prevChoices):
        if (prevChoices.history or prevChoices.input):
            if TabularToGtrackTool._getFileContentsInfo(prevChoices).error is None:
                if prevChoices.columnSelection == 'Default 3D columns (Hi-C)':
                    return ['Yes', 'No']
                else:
                    return ['No', 'Yes']

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']

    @staticmethod
    def _getGenomeRegion(seqid, start, end):
        if seqid in [None, '', '.'] or start in [None, '', '.']:
            return None

        curReg = GenomeRegion(chr=seqid, start=int(start))
        if end is not None:
            curReg.end = int(end)
        else:
            curReg.end = int(end) + 1

        return curReg

    @staticmethod
    def _checkOverlap(prevReg, curReg, line):
        if prevReg is not None and curReg.overlaps(prevReg):
            raise InvalidFormatError('The segments/points are not allowed to overlap ' \
                                     'when creating dense or 3D track types. First overlapping line: ' + repr(line))

    @staticmethod
    def _writeBlockLines(firstRegInBlock, prevReg, curReg, tempContents, tempDataLines):
        if prevReg is not None and firstRegInBlock is not None:
            if curReg is None or not curReg.touches(prevReg):
                tempContents.write('####' + 'seqid=%s; start=%s; end=%s' % \
                                   (firstRegInBlock.chr, firstRegInBlock.start, prevReg.end) + os.linesep)
                tempDataLines.flush()
                tempDataLines.seek(0)
                tempContents.write(tempDataLines.read())
                tempDataLines = NamedTemporaryFile()
                firstRegInBlock = curReg

        return firstRegInBlock, tempDataLines


    @staticmethod
    def _writeDataLines(cols, colIndexes, tempDataLines):
        if cols:
            tempDataLines.write('\t'.join(cols[j] for j in colIndexes) + os.linesep)

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history. If getOutputFormat is anything else than HTML, the output should be written to the file with path galaxyFn.gtr
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''

        try:
            if choices.history:
                inputFile = open(ExternalTrackManager.extractFnFromGalaxyTN(choices.history.split(':')), 'r')
            else:
                inputFile = StringIO(choices.input)

            headers = cls._getHeaders(choices)
            headerIdxs = {}
            for i, header in enumerate(headers):
                headerIdxs[header] = i

            createDense = choices.createDense == 'Yes'
            if createDense:
                firstRegInBlock = None
                curReg = None

                assert headerIdxs['seqid'] is not None
                assert headerIdxs['start'] is not None

                headers[headerIdxs['start']] = ''

            create3dData = cls._create3dData(choices)
            if create3dData:
                if any(x in headers for x in ['id', 'edges']):
                    print >> sys.stderr, "Error: when using the special 3D input columns 'linked_seqid' and " + \
                                         "'linked_start', the columns 'id' and 'edges' must not " + \
                                         "be specified in addition."
                    return

                for header in ['linked_seqid', 'linked_start', 'linked_end', 'link_weight']:
                    if header in headerIdxs:
                        headers[headerIdxs[header]] = ''

                for header in ['id', 'edges']:
                    headerIdxs[header] = len(headers)
                    headers += [header]

                regs = []
                regIdx = 0
                prevRegIdx = 0
                idDict = {}
                idCount = 0
                curCols = None
                prevLine = ''

                firstRegInBlock = None
                curReg = None
                prev3dReg = None
                nextReg = None

            if createDense or create3dData:
                newInputFile = NamedTemporaryFile()
                sortedInputFile = NamedTemporaryFile()

            colIndexes = [i for i, header in enumerate(headers) if header != '']
            numSkipLines = cls._getNumSkipLines(choices)

            tempContents = NamedTemporaryFile()
            tempDataLines = NamedTemporaryFile()

            if choices.indexing == '1-indexed, end inclusive':
                tempContents.write('##1-indexed: true' + os.linesep)
                tempContents.write('##end inclusive: true' + os.linesep)

            tempContents.write('###' + '\t'.join([headers[i] for i in colIndexes]) + os.linesep)

            for passType in ['pre','final'] if createDense or create3dData else ['final']:
                for i in xrange(numSkipLines):
                    inputFile.readline()

                splitChar = cls._getSplitChar(choices)
                numCols = cls._getFileContentsInfo(choices).numCols
                regionsDecreased = False

                autoCorrectSeqId = choices.handleSeqId == 'Yes, auto-correct to the best match in the genome build'
                cropCrossingSegments = choices.cropCrossingSegments == 'Yes'
                genome = choices.genome

                for i, line in enumerate(inputFile):
                    if line == '' or len(line) > 0 and line[0] == '#':
                        pass

                    cols = [x.strip() for x in line.strip().split(splitChar)]
                    if create3dData:
                        cols += ['', '']

                    for j in colIndexes:
                        if len(cols) <= j:
                            print >> sys.stderr, "Error in line #%s: %s" % (i+1, line)
                            print >> sys.stderr, "The line does not include the column #%s, which is defined with " \
                                                 "the name '%s' (the number of columns is %s). Please fix the input " \
                                                 "file or redefine the column names of this column." \
                                                 % (j+1, headers[j], len(cols))
                            return

                    if autoCorrectSeqId:
                        from quick.util.GenomeInfo import GenomeInfo
                        cols[headerIdxs['seqid']] = GenomeInfo.findBestMatchingChr(genome, cols[headerIdxs['seqid']])

                    for j, col in enumerate(cols):
                        if col == '':
                            cols[j] = '.'
                        else:
                            cols[j] = GtrackGenomeElementSource.convertPhraseToAllowed(col)

                    if cropCrossingSegments:
                        from quick.util.GenomeInfo import GenomeInfo
                        for seqidHdr, startHdr, endHdr in [('seqid','start','end')] \
                                + ([('linked_seqid','linked_start','linked_end')] if create3dData else []):
                            if endHdr in headerIdxs:
                                seqid = cols[headerIdxs[seqidHdr]]
                                start = cols[headerIdxs[startHdr]]
                                end = cols[headerIdxs[endHdr]]
                                if not any(x == '.' for x in [seqid, start, end]):
                                    start, end = int(start), int(end)
                                    if choices.indexing == '1-indexed, end inclusive':
                                        start -= 1
                                    chrLen = GenomeInfo().getChrLen(genome, seqid)
                                    if start < chrLen and end > chrLen:
                                        cols[headerIdxs[endHdr]] = str(chrLen)

                    if createDense or create3dData:
                        prevReg = curReg
                        curReg = cls._getGenomeRegion(cols[headerIdxs['seqid']], cols[headerIdxs['start']], \
                                                                       cols[headerIdxs['end']] if headerIdxs.get('end') else None)

                        if passType == 'pre':
                            newInputFile.write(line.strip() + os.linesep)

                            if create3dData:
                                id = curReg.strShort()
                                if id not in idDict:
                                    regs.append(curReg)
                                    idDict[id] = ''

                                linkedReg = cls._getGenomeRegion(cols[headerIdxs['linked_seqid']], cols[headerIdxs['linked_start']], \
                                                                                     cols[headerIdxs['linked_end']] if 'end' in headerIdxs else None)
                                if choices.undirected == 'Yes' and linkedReg and linkedReg != curReg:
                                    id = linkedReg.strShort()
                                    if id not in idDict:
                                        regs.append(linkedReg)
                                        idDict[id] = ''

                                    cols[headerIdxs['seqid']], cols[headerIdxs['linked_seqid']] = cols[headerIdxs['linked_seqid']], cols[headerIdxs['seqid']]
                                    cols[headerIdxs['start']], cols[headerIdxs['linked_start']] = cols[headerIdxs['linked_start']], cols[headerIdxs['start']]
                                    if 'end' in headerIdxs:
                                        cols[headerIdxs['end']], cols[headerIdxs['linked_end']] = cols[headerIdxs['linked_end']], cols[headerIdxs['end']]

                                    newInputFile.write(splitChar.join(cols[:-2]) + os.linesep)

                        else: #passType == 'final':
                            if firstRegInBlock is None:
                                firstRegInBlock = curReg

                            if create3dData:
                                if curReg != prevReg:
                                    prevCols = curCols
                                    prevRegIdx = regIdx
                                    regIdx = 0
                                    id = curReg.strShort()
                                    curCols = copy(cols)
                                    curCols[headerIdxs['id']] = idDict[id] if choices.idGeneration == 'Counting' else id
                                    curCols[headerIdxs['edges']] = ''

                                linkedReg = cls._getGenomeRegion(cols[headerIdxs['linked_seqid']], cols[headerIdxs['linked_start']], \
                                                                                 cols[headerIdxs['linked_end']] if 'end' in headerIdxs else None)

                                if linkedReg:
                                    edges = curCols[headerIdxs['edges']]

                                    if edges != '':
                                        edges += ';'

                                    id = linkedReg.strShort()
                                    if id not in idDict:
                                        raise InvalidFormatError("Error: linked region '%s' is not present in tabular file. Line: %s" % (linkedReg, line))

                                    if choices.complete == 'Yes':
                                        while regIdx < len(regs) and regs[regIdx] != linkedReg:
                                            missingId = regs[regIdx].strShort()
                                            edges += '%s=.;' % (idDict[missingId] if choices.idGeneration == 'Counting' else missingId)
                                            regIdx += 1

                                    edges += idDict[id] if choices.idGeneration == 'Counting' else id
                                    if 'link_weight' in headerIdxs:
                                        edges += '=' + GtrackGenomeElementSource.convertPhraseToAllowed(cols[headerIdxs['link_weight']])
                                    regIdx += 1

                                    curCols[headerIdxs['edges']] = edges

                                if curReg != prevReg and prevCols:
                                    if choices.complete == 'Yes':
                                        for i in xrange(prevRegIdx, len(regs)):
                                            missingId = regs[i].strShort()
                                            if i != 0:
                                                prevCols[headerIdxs['edges']] += ';'
                                            prevCols[headerIdxs['edges']] += '%s=.' % (idDict[missingId] if choices.idGeneration == 'Counting' else missingId)

                                    if prevCols[headerIdxs['edges']] == '':
                                        prevCols[headerIdxs['edges']] = '.'

                                    cls._checkOverlap(prev3dReg, prevReg, prevLine)

                                    if createDense:
                                        firstRegInBlock, tempDataLines = cls._writeBlockLines \
                                            (firstRegInBlock, prev3dReg, prevReg, tempContents, tempDataLines)

                                    cls._writeDataLines(prevCols, colIndexes, tempDataLines)

                                    prev3dReg = prevReg
                                prevLine = line
                            else: #createDense
                                cls._checkOverlap(prevReg, curReg, line)

                                firstRegInBlock, tempDataLines = cls._writeBlockLines \
                                    (firstRegInBlock, prevReg, curReg, tempContents, tempDataLines)

                                cls._writeDataLines(cols, colIndexes, tempDataLines)
                    else:
                        cls._writeDataLines(cols, colIndexes, tempDataLines)

                if passType == 'pre':
                    newInputFile.flush()

                    inputFile.close()

                    sortCmd = ["sort", newInputFile.name, "-t$'%s'" % splitChar, "-s"] +\
                               ["-k%s,%s%s" % (headerIdxs[x]+1, headerIdxs[x]+1, s) if x in headerIdxs else "" \
                                for x,s in [('seqid',''), ('start','n'), ('end','n'), \
                                            ('linked_seqid',''), ('linked_start','n'), ('linked_end','n')]] +\
                                ["-o", sortedInputFile.name]
                    subprocess.call(' '.join(sortCmd), stderr=sys.stderr, stdout = sys.stdout, shell=True)

                    #print >> sys.stderr, ' '.join(sortCmd)
                    #os._exit(0)
                    newInputFile.close()

                    if create3dData:
                        regs = sorted(regs)
                        for i,reg in enumerate(regs):
                            idDict[reg.strShort()] = str(i)

                    inputFile = sortedInputFile
                    inputFile.seek(0)
                    numSkipLines = 0
                    curReg = None
                else: #passType == 'final':
                    if create3dData:
                        if choices.complete == 'Yes':
                            for i in xrange(regIdx, len(regs)):
                                missingId = regs[i].strShort()
                                if i != 0:
                                    curCols[headerIdxs['edges']] += ';'
                                curCols[headerIdxs['edges']] += '%s=.' % (idDict[missingId] if choices.idGeneration == 'Counting' else missingId)

                        if curCols[headerIdxs['edges']] == '':
                            curCols[headerIdxs['edges']] = '.'

                        cls._checkOverlap(prev3dReg, curReg, prevLine)

                        if createDense:
                            firstRegInBlock, tempDataLines = cls._writeBlockLines \
                                (firstRegInBlock, prev3dReg, curReg, tempContents, tempDataLines)

                        cls._writeDataLines(curCols, colIndexes, tempDataLines)

                    if createDense:
                        firstRegInBlock, tempDataLines = cls._writeBlockLines \
                            (firstRegInBlock, curReg, None, tempContents, tempDataLines)

                    tempDataLines.flush()
                    tempDataLines.seek(0)
                    tempContents.write(tempDataLines.read())
                    tempContents.flush()
                    tempContents.seek(0)

            #print tempContents.read()
            #tempContents.seek(0)

            expandHeadersOfGtrackFileAndReturnComposer(tempContents.name).composeToFile(galaxyFn)
            geSource = GtrackGenomeElementSource(galaxyFn, genome=genome, printWarnings=False)
            for ge in geSource:
                pass

        except Exception, e:
            print >> sys.stderr, e
            raise

    @staticmethod
    def validateAndReturnErrors(choices):
        if choices.source == 'Tabular file from history':
            if choices.history in [None, '']:
                return 'Error: Please select a tabular file from your history. You may need to change the format of your history items to "tabular" or other tabular formats.'
        else:
            if choices.input == '':
                return 'Please type or paste the contents of a tabular file into the input box.'

        if choices.numSkipLines is not None:
            try:
                int(choices.numSkipLines.strip())
            except:
                return 'Error: please type a correct number of lines to skip ("%s")' % choices.numSkipLines.strip()

        fileContentsInfo = TabularToGtrackTool._getFileContentsInfo(choices)
        if fileContentsInfo and fileContentsInfo.error is not None:
            return fileContentsInfo.error

        if choices.selectGenome == 'Yes':
            genome = choices.genome
            if genome in [None, '']:
                return 'Please select a genome build.'
        else:
            genome = None

        if choices.handleSeqId == 'Yes, auto-correct to the best match in the genome build':
            if choices.selectGenome != 'Yes':
                return 'To auto-correct the sequence ids, you need to specify a genome build.'

        if choices.cropCrossingSegments == 'Yes':
            if choices.selectGenome != 'Yes':
                return 'To crop segments crossing sequence ends, you need to specify a genome build.'

        if choices.columnSelection == 'Base columns on existing GTrack file':
            return GeneralGuiTool._checkHistoryTrack(choices, 'colSpecFile', genome, 'GTrack')

        headers = TabularToGtrackTool._getHeaders(choices)
        if not 'seqid' in headers:
            return "Error: the 'seqid' column is mandatory but is missing."

        if 'edges' in headers and not 'id' in choices:
            return "Error: the 'id' column is missing, but is mandatory since the 'edges' column has been selected."

        if choices.createDense == 'Yes' and not 'start' in headers:
            return 'The start column must be defined in order to create dense track types.'

        if choices.trackType is None:
            return 'Error: the columns selected do not define a GTrack track type. Please refer to the GTrack specification for more information.'
        elif any(x in choices.trackType.lower() for x in ['function', 'partition', 'base pairs']) and choices.createDense == 'No':
            denseTracksBasis = {'Function (F)': 'Valued Points (VP)', 'Step Function (SF)': 'Valued Segments (VS)',
                                'Genome Partition (GP)': 'Segments (S)', 'Linked Base Pairs (LBP)': 'Points (P)'}
            trackType, trackTypeBasis = choices.trackType, denseTracksBasis[choices.trackType]
            return 'Error: to create track type "%s", you must use select columns corresponing to track type "%s" and ' % (trackType, trackTypeBasis) + \
                    'select "Yes" for "Create dense track type". For linked track types, select the appropriate "linked" or "edges" columns.'

        return None

    @staticmethod
    def isPublic():
        return True
    #
    #@staticmethod
    #def isRedirectTool():
    #    return False
    #
    #@staticmethod
    #def isHistoryTool():
    #    return True
    #
    #@staticmethod
    #def isDynamic():
    #    return True
    #
    @staticmethod
    def getResetBoxes():
        return ['columnSelection']
    #
    @staticmethod
    def getToolDescription():
        core = HtmlCore()
        core.paragraph('This tool is used to create GTrack files from any tabular input file. The '
                       'user must select the column names for the table, enabling the GTrack '
                       'header expander to automatically expand the headers, effectively converting '
                       'the file to a GTrack file. Custom column names are also supported.')
        core.divider()

        core.smallHeader('The following column names are part of the GTrack specification')
        core.descriptionLine('seqid', "An identifier of the underlying sequence of "
                                      "the track element (i.e. the row). Example: 'chr1'", emphasize=True)
        core.descriptionLine('start', 'The start position of the track element', emphasize=True)
        core.descriptionLine('end', 'The end position of the track element', emphasize=True)
        core.descriptionLine('value', 'A value associated to the track element. '
                                      'The value type is automatically found by the tool.', emphasize=True)
        core.descriptionLine('strand', "The strand of the track element, either '+', '-' or '.'", emphasize=True)
        core.descriptionLine('id', "An unique identifier of the track element, e.g. 'a'", emphasize=True)
        core.descriptionLine('edges', "A semicolon-separated list of id's, representing "
                                      "edges from this track element to other elements. "
                                      "Weights may also be specified. Example: 'a=1.0;b=0.9'", emphasize=True)
        core.paragraph("See the 'Show GTrack specification' tool for more information.")
        core.divider()

        core.smallHeader('Column selection method')
        core.paragraph('The tool supports two ways of selecting column names. First, you can select '
                       'the column names manually. The other option is to select a GTrack file in the '
                       'the history. The tool will then use the same column names (only using the first '
                       'columns if the number of columns in the current tabular file is less than in the '
                       'GTrack file.')
        core.divider()

        core.smallHeader('Genome')
        core.paragraph("Some GTrack files require a specified genome to be valid, e.g. if bounding regions "
                       "are specified without explicit end coordinates. A genome build must thus be selected if "
                       "such a GTrack file is to be used as template file for column specification. "
                       "Also, auto-correction of the sequence id ('seqid') column requires the selection of a "
                       "genome build. The resulting GTrack file in the history will be associated with the "
                       "selected genome.")
        core.divider()

        core.smallHeader('Track type')
        core.paragraph('According to the columns selected, the tool automatically finds the '
                       'corresponding track type according to the GTrack specification. '
                       'Note that dense track types are noe supported yet byt this tool.')
        core.divider()

        core.smallHeader('Indexing standard')
        core.paragraph('Two common standards of coordinate indexing are common in bioinformatics. A track '
                       'element covering the first 10 base pairs of chr1 are represented in two ways:' )
        core.descriptionLine('0-indexed, end exclusive', "seqid=chr1, start=0, end=10", emphasize=True)
        core.descriptionLine('1-indexed, end inclusive', "seqid=chr1, start=1, end=10", emphasize=True)
        core.paragraph('The GTrack format supports both standards, but the user must inform the system '
                       'which standard is used for each particular case.')
        core.divider()

        core.smallHeader('Auto-correction of sequence id')
        core.paragraph("The tool supports auto-correction of the sequence id ('seqid') column. "
                       "If this is selected, a search is carried out on the sequence id's defined "
                       "for the current genome build. The nearest match, if unique, is inserted in "
                       "the new GTrack file. If no unique match is found, the original value is "
                       "used. The algorithm also handles roman numbers. Example: 'IV' -> 'chr4'")
        core.divider()

        core.smallHeader('Example')
        core.paragraph('Input table')
        core.tableHeader(['start','','id','something','seqid'])
        core.tableLine(['100','.','a','yes','chr1'])
        core.tableLine(['250','.','b','yes','chr1'])
        core.tableLine(['120','.','c','no','chr2'])
        core.tableFooter()

        core.paragraph('Output file')
        core.styleInfoBegin(styleClass='debug')
        core.append(
'''##gtrack version: 1.0
##track type: points
##uninterrupted data lines: true
##sorted elements: true
##no overlapping elements: true
###seqid  start  id	 something
chr1	  100	 a	 yes
chr1	  250	 b	 yes
chr2	  120	 c	 no''')
        core.styleInfoEnd()

        return str(core)
    #
    #@staticmethod
    #def getToolIllustration():
    #    return None
    #

    @staticmethod
    def getFullExampleURL():
        return 'u/hb-superuser/p/create-gtrack-file'

    #@staticmethod
    #def isDebugMode():
    #    return True
    #

    @staticmethod
    def getOutputFormat(choices=None):
        '''The format of the history element with the output of the tool.
        Note that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.
        '''
        return 'gtrack'

TabularToGtrackTool.setupColumnFunctions()
