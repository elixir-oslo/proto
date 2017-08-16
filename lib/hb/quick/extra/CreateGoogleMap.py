import ast
import getpass
import os
import shutil
import sys
from subprocess import Popen, PIPE

from config.Config import RESULTS_FILES_PATH, STATIC_PATH
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.extra.CustomFuncCatalog import parseMatrixTextFileToShelf, mergeShelvesTransitively, reverseMappingHavingListValues
from quick.util.CommonFunctions import getGalaxyFnFromDatasetId


#print resultsFilesDir
#print resultsStaticDir
#print googleMapsDir
#print googleMapsCommonDir
#print self.CUR_DIR_ON_INVITRO
#print self.CUR_DIR_ON_MEDSEQPROD

class GoogleMapCreator(object):
    USERNAME = getpass.getuser()
    #todo: needs fix for generality
    HOME_DIR_ON_INVITRO = '/cluster/home/' + USERNAME
    HOME_DIR_ON_MEDSEQPROD = '/insilico_home/' + USERNAME
    TMP_DIR_ON_INVITRO = HOME_DIR_ON_INVITRO + '/tmp'
    TMP_DIR_ON_MEDSEQPROD = HOME_DIR_ON_MEDSEQPROD + '/tmp'
    IMAGEMAGICK_TMP_DIR_ON_MEDSEQPROD = '/usit/med-seqprod01/data/sveinugu/tmp'

    CUR_DIR_ON_INVITRO = Popen(['pwd'], shell=True, stdout=PIPE).communicate()[0].strip()
    CUR_DIR_ON_MEDSEQPROD = CUR_DIR_ON_INVITRO.replace(HOME_DIR_ON_INVITRO, HOME_DIR_ON_MEDSEQPROD)

    def __init__(self, name, id, mapId, batchid='0', genome=None):
        self._name = name
        self._mapId = mapId
        self._id = id
        colldir = createFullGalaxyIdFromNumber(id)[0]
        galaxyFn = getGalaxyFnFromDatasetId(id)
        self._genome = genome

        self._resultsFilesDir = '/'.join([RESULTS_FILES_PATH, colldir])
        self._resultsStaticDir = GalaxyRunSpecificFile([batchid], galaxyFn).getDiskPath()
        self._googleMapsDir = '/'.join([STATIC_PATH, 'maps', name])
        self._googleMapsCommonDir = '/'.join([STATIC_PATH, 'maps', 'common'])
        self._googleMapsCommonMapIdDir = '/'.join([self._googleMapsCommonDir, mapId])

    def tile(self, onMedSeqProd):
        from config.Config import HB_SOURCE_CODE_BASE_DIR
        databaseFile = open(self._resultsFilesDir + '/dataset_%s.dat' % self._id, 'r')

        for line in databaseFile:
            if line.startswith('('):
                imagesize = max([int(x) for x in line.replace('(','').replace(',','').replace(')','').strip().split()])

        shutil.copy(HB_SOURCE_CODE_BASE_DIR+'/third_party/tileCutter3.py', '/'.join([self.TMP_DIR_ON_INVITRO, 'tileCutter3.py']))

        if not os.path.exists('/'.join([self.TMP_DIR_ON_INVITRO, self._name, 'data'])):
            os.makedirs('/'.join([self.TMP_DIR_ON_INVITRO, self._name, 'data']))

        shutil.copy(self._resultsStaticDir + '/ClusterMatrixStat_Result_heatmap.png', \
                    '/'.join([self.TMP_DIR_ON_INVITRO, self._name, 'data']))
        outputDir = '/'.join([self._name, 'tiles'])

    #    print Popen(['ssh','med-seqprod01.uio.no', 'cd', self.TMP_DIR_ON_MEDSEQPROD, ';', 'python', 'tileCutter3.py', outputDir, 'png', '/'.join([self._name, 'data', 'ClusterMatrixStat_Result_heatmap.png']), '0', '0', str(imagesize), str(imagesize), '0', '0', '0', '255', '255', '\"#111111\"'], stdout=PIPE).communicate()[0]
        if onMedSeqProd:

            print Popen(['/usit/titan/u1/sveinugu/HyperBrowser/DiseaseTFBS/test.sh', \
                         'export MAGICK_TMPDIR=%s;' % self.IMAGEMAGICK_TMP_DIR_ON_MEDSEQPROD +\
                         'export PATH=%s/bin:$PATH;' % self.HOME_DIR_ON_MEDSEQPROD +\
                         'export MAGICK_AREA_LIMIT=\"120GiB\";' +\
                         'export MAGICK_MEMORY_LIMIT=\"120GiB\";' +\
                         'export MAGICK_MAP_LIMIT=\"500GiB\";' +\
                         'export MAGICK_DISK_LIMIT=\"500GiB\";' +\
                         'identify -list resource;' +\
                         'cd ' + self.TMP_DIR_ON_MEDSEQPROD + '; python tileCutter3.py ' + outputDir + \
                         ' png ' + '/'.join([self._name, 'data', 'ClusterMatrixStat_Result_heatmap.png']) + \
                         ' 0 0 ' + str(imagesize) + ' ' + str(imagesize) + \
                         ' 0 0 0 255 255 \"#111111\"'], stdout=PIPE).communicate()[0]
        else:
            os.chdir(self.TMP_DIR_ON_INVITRO)
            print Popen(['python', 'tileCutter3.py', outputDir, \
                         'png', '/'.join([self._name, 'data', 'ClusterMatrixStat_Result_heatmap.png']), \
                         '0', '0', str(imagesize), str(imagesize), \
                         '0', '0', '0', '255', '255', '#111111'], stdout=PIPE).communicate()[0]
    #    shutil.move(self.TMP_DIR_ON_INVITRO + '/t-images_%s' %id, '/'.join([self.TMP_DIR_ON_INVITRO, self._name, 'tiles']))
        shutil.move('/'.join([self.TMP_DIR_ON_INVITRO, self._name]), self._googleMapsDir)


    def copyWithoutTiling(self):
        if os.path.exists( '/'.join([self.TMP_DIR_ON_INVITRO, self._name]) ):
            shutil.move('/'.join([self.TMP_DIR_ON_INVITRO, self._name]), self._googleMapsDir)
        else:
            if not os.path.exists('/'.join([self._googleMapsDir, 'data'])):
                os.makedirs('/'.join([self._googleMapsDir, 'data']))

            shutil.copy(self._resultsStaticDir + '/ClusterMatrixStat_Result_heatmap.png', self._googleMapsDir + '/data/')

    def copyResultFiles(self):
        shutil.copy(self._resultsStaticDir + '/Result_table.txt', self._googleMapsDir + '/data/')
        shutil.copy(self._resultsStaticDir + '/Result_table.html', self._googleMapsDir + '/data/')

        if os.path.exists(self._resultsStaticDir + '/Result_counts_table.txt'):
            shutil.copy(self._resultsStaticDir + '/Result_counts_table.txt', self._googleMapsDir + '/data/')
            shutil.copy(self._resultsStaticDir + '/Result_counts_table.html', self._googleMapsDir + '/data/')

        if os.path.exists(self._resultsStaticDir + '/Result_pval_table.txt'):
            shutil.copy(self._resultsStaticDir + '/Result_pval_table.txt', self._googleMapsDir + '/data/')
            shutil.copy(self._resultsStaticDir + '/Result_pval_table.html', self._googleMapsDir + '/data/')

        if os.path.exists(self._resultsStaticDir + '/Result_significance_table.txt'):
            shutil.copy(self._resultsStaticDir + '/Result_significance_table.txt', self._googleMapsDir + '/data/')
            shutil.copy(self._resultsStaticDir + '/Result_significance_table.html', self._googleMapsDir + '/data/')

        shutil.copy(self._resultsStaticDir + '/ClusterMatrixStat_Result_heatmap.txt', self._googleMapsDir + '/data/')

    #if os.path.exists( self._googleMapsDir + '/data/Result_table.shelve' ):
    #    os.remove( self._googleMapsDir + '/data/Result_table.shelve' )

    def createResultShelves(self):
        parseMatrixTextFileToShelf(self._googleMapsDir + '/data/Result_table.txt', \
                                   self._googleMapsDir + '/data/Result_table.shelf', \
                                   self._googleMapsDir + '/data/rowPos2Name.shelf', \
                                   self._googleMapsDir + '/data/colPos2Name.shelf', \
                                   self._googleMapsDir + '/data/rowPos2ElCount.shelf', \
                                   self._googleMapsDir + '/data/colPos2ElCount.shelf', \
                                   keyType='pos')

        if os.path.exists(self._googleMapsDir + '/data/Result_counts_table.txt'):
            parseMatrixTextFileToShelf(self._googleMapsDir + '/data/Result_counts_table.txt', \
                                       self._googleMapsDir + '/data/Result_counts_table.shelf', \
                                       keyType='pos')

        if os.path.exists(self._googleMapsDir + '/data/Result_pval_table.txt'):
            parseMatrixTextFileToShelf(self._googleMapsDir + '/data/Result_pval_table.txt', \
                                       self._googleMapsDir + '/data/Result_pval_table.shelf', \
                                       keyType='pos')

        if os.path.exists(self._googleMapsDir + '/data/Result_significance_table.txt'):
            parseMatrixTextFileToShelf(self._googleMapsDir + '/data/Result_significance_table.txt', \
                                       self._googleMapsDir + '/data/Result_significance_table.shelf', \
                                       keyType='pos')

        htmlFileContents = open(self._resultsFilesDir + '/dataset_%s.dat' % self._id, 'r').read()
        runDescFile = open(self._googleMapsDir + '/data/Run_description.html', 'w')
        runDescFile.write(htmlFileContents[htmlFileContents.find("<div class=\"infomessagesmall"):
                                           htmlFileContents.find("<hr />\n<h3>REFERENCES</h3>")])
        runDescFile.close()

        reverseMappingHavingListValues(self._googleMapsDir + '/data/rowPos2Name.shelf', \
                                       self._googleMapsDir + '/data/rowName2Pos.shelf')
        reverseMappingHavingListValues(self._googleMapsDir + '/data/colPos2Name.shelf', \
                                       self._googleMapsDir + '/data/colName2Pos.shelf')

        if os.path.exists(self._googleMapsCommonMapIdDir):
            if 'extraRowNames2Name.shelf' in os.listdir(self._googleMapsCommonMapIdDir):
                mergeShelvesTransitively(self._googleMapsCommonMapIdDir + '/extraRowNames2Name.shelf', \
                                         self._googleMapsDir + '/data/rowName2Pos.shelf', \
                                         self._googleMapsDir + '/data/new_rowName2Pos.shelf', \
                                         includeSecondShelf=True)
                shutil.move(self._googleMapsDir + '/data/new_rowName2Pos.shelf', self._googleMapsDir + '/data/rowName2Pos.shelf')

            if 'extraColNames2Name.shelf' in os.listdir(self._googleMapsCommonMapIdDir):
                mergeShelvesTransitively(self._googleMapsCommonMapIdDir + '/extraColNames2Name.shelf', \
                                         self._googleMapsDir + '/data/colName2Pos.shelf', \
                                         self._googleMapsDir + '/data/new_colName2Pos.shelf', \
                                         includeSecondShelf=True)
                shutil.move(self._googleMapsDir + '/data/new_colName2Pos.shelf', self._googleMapsDir + '/data/colName2Pos.shelf')

    def createIndexFile(self, title, genome):
        #Placed here, since it will be updated more often than other data
        if title != self._name:
            open(self._googleMapsDir + '/data/Title.txt', 'w').write(title)

        if self._genome is not None:
            open(self._googleMapsDir + '/data/Genome.txt', 'w').write(genome)

        templateFile = open(self._googleMapsCommonDir + '/template.html', 'r')

        oldIndexFileLines = None
        if os.path.exists(self._googleMapsDir + '/index.html'):
            shutil.move(self._googleMapsDir + '/index.html', self._googleMapsDir + '/index.html.old')
            oldIndexFileLines = [line for line in open(self._googleMapsDir + '/index.html.old')]

        htmlFile = open(self._googleMapsDir + '/index.html', 'w')

        for line in templateFile:
            lineCopiedFromOldFile = False
            if oldIndexFileLines is not None:
                for key in ['debug', 'numRows', 'numCols', 'northPixel', 'westPixel', 'southPixel', 'eastPixel']:
                    if key in line:
                        oldLinesWithKey = [oldLine for oldLine in oldIndexFileLines if key in oldLine]
                        if len(oldLinesWithKey) == 1:
                            htmlFile.write(oldLinesWithKey[0])
                            lineCopiedFromOldFile = True

            if not lineCopiedFromOldFile:
                line = line.replace('NAME', self._name)
                line = line.replace('MAPID', self._mapId)
                if title.startswith('* '):
                    title = title[2:]
                line = line.replace('TITLE', title)
                htmlFile.write(line)

        templateFile.close()
        htmlFile.close()

    def fixPermissions(self):
        print Popen(['chmod', '-R', '775', self._googleMapsDir], stdout=PIPE).communicate()[0]


if __name__ == "__main__":
    if len(sys.argv) not in [8,9,10,11]:
        print 'Usage: python createGoogleMap.py id batchid name mapId doTiling doCreateResultShelves doCreateIndexFile title=name onMedSeqProd=False genome=None'
        sys.exit(0)


    id, batchid, name, mapId = [sys.argv[x] for x in [1,2,3,4]]
    doTiling, doCreateResultShelves, doCreateIndexFile = [ast.literal_eval(sys.argv[x]) for x in [5,6,7]]
    assert all([x in [False, True] for x in [doTiling, doCreateResultShelves, doCreateIndexFile]])

    if len(sys.argv) >= 9:
        title = sys.argv[8]
    else:
        title = name

    if len(sys.argv) == 10:
        onMedSeqProd = ast.literal_eval(sys.argv[9])
    else:
        onMedSeqProd = False

    if len(sys.argv) == 11:
        genome = sys.argv[10]
        if genome == 'None':
            genome = None
    else:
        genome = None

    creator = GoogleMapCreator(name, id, mapId, batchid, genome)

    if doTiling:
        creator.tile(onMedSeqProd)
    else:
        creator.copyWithoutTiling()

    creator.copyResultFiles()

    if doCreateResultShelves:
        creator.createResultShelves()

    if doCreateIndexFile:
        creator.createIndexFile(title, genome)

    creator.fixPermissions()
