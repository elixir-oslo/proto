from quick.webtools.imports.TrackSearchTool import TrackSearchTool
from quick.trackaccess.DatabaseTrackAccessModule import DatabaseTrackAccessModule
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from config.Config import HB_SOURCE_DATA_BASE_DIR
from quick.trackaccess.EncodeTrackAccessModule import GWASTrackAccessModule

class GWASTrackSearchTool(TrackSearchTool):
    DISEASE_COLUMN_NAME = '"DISEASE/TRAIT"'
    CHR_COLUMN_NAME = '"CHR_ID"'
    START_COLUMN_NAME = '"CHR_POS"'
    VAL_COLUMN_NAME = '"PVALUE_MLOG"'
    
    HISTORY_PROGRESS_TITLE = 'Progress'
    HISTORY_HIDDEN_TRACK_STORAGE = 'GSuite track storage'
    DATABASE_GENOME = 'hg38'
    OUTPUT_GENOME = 'hg19'
    GTRACK_BLUEPRINT_PATH = HB_SOURCE_DATA_BASE_DIR + '/gsuite/GWAS_blueprint.gtrack'

#    DATABASE_TRACK_ACCESS_MODULE_CLS = EncodeDatabaseTrackAccessModule
    def __new__(cls, *args, **kwArgs):
        return TrackSearchTool.__new__(GWASTrackSearchTool, *args, **kwArgs)
    
    @staticmethod
    def getToolName():
        return "NHGRI-EBI GWAS Catalog"
    
    @classmethod
    def _getTableName(cls):
        return 'file_gwas'
    
    @classmethod
    def _getClassAttributes(cls, db):
        return ['hb_experiment_type','hb_genomebuild','hb_target','CHR_ID','CONTEXT','DISEASE/TRAIT',\
                'MAPPED_GENE','INTERGENIC',\
                'PLATFORM [SNPS PASSING QC]','PUBMEDID','REGION','REPORTED GENE(S)','SNPS','STUDY']
        # # attributes = []
        # # 
        # # colList = db._db.getTableCols(cls.TABLE_NAME)
        # # for col in colList:
        # #     attributes.append(col)
        # # attributes.remove('uri')
        # # attributes.remove('hb_datatype')
        # # 
        # # return attributes
    
    @classmethod
    def getColListString(cls):
        cols = cls.DB._db.correctColumNames\
            (cls.DB._db.getTableCols(cls.TABLE_NAME))
        colListString = ''
        cols.insert(0, cols.pop(cols.index('"uri"')))
        cols.insert(1, cols.pop(cols.index('"hb_datatype"')))
        return cols, ','.join(cols)
    
    @classmethod
    def _getDownloadProtocol(cls):
        return 'rsync'

    @classmethod
    def getExtraHistElements(cls, choices):
        fileList = []

        if choices.outFormat == 'gsuite':
            from gold.gsuite.GSuiteConstants import GSUITE_SUFFIX, GSUITE_STORAGE_SUFFIX
            from quick.webtools.GeneralGuiTool import HistElement
            fileList.append( HistElement(cls.HISTORY_PROGRESS_TITLE, 'customhtml') )
            fileList.append( HistElement(cls.HISTORY_HIDDEN_TRACK_STORAGE, GSUITE_STORAGE_SUFFIX, hidden=True))

        return fileList

    @staticmethod
    def _fixColNameForGTrack(col):
        return col.strip('"').strip().lower().replace(' ','_').replace('-','_')

    @classmethod
    def printGSuite(cls, choices, cols, rows, colListString, outFile):
        #print cols
        from quick.extra.ProgressViewer import ProgressViewer

        from gold.gsuite.GSuite import GSuite
        from gold.gsuite.GSuiteTrack import GSuiteTrack, GalaxyGSuiteTrack
        import gold.gsuite.GSuiteComposer as GSuiteComposer

        from gold.origdata.GtrackGenomeElementSource import GtrackGenomeElementSource
        from gold.origdata.GtrackComposer import ExtendedGtrackComposer
        from gold.origdata.GESourceWrapper import ListGESourceWrapper
        from gold.origdata.GenomeElement import GenomeElement

        from collections import defaultdict
        from copy import copy
        from urllib import quote

        from unidecode import unidecode
        from pyliftover import LiftOver

        gSuite = GSuite()

        diseaseColIndex = cols.index(cls.DISEASE_COLUMN_NAME)
        chrColIndex = cols.index(cls.CHR_COLUMN_NAME)
        startColIndex = cols.index(cls.START_COLUMN_NAME)
        valColIndex = cols.index(cls.VAL_COLUMN_NAME)
        
        orderedExtraKeys = copy(cols)
        extraIndexes = range(len(cols))
        for colName in [cls.DISEASE_COLUMN_NAME, cls.CHR_COLUMN_NAME,
                        cls.START_COLUMN_NAME, cls.VAL_COLUMN_NAME]:
            extraIndexes.remove(cols.index(colName))
            orderedExtraKeys.remove(colName)
        orderedExtraKeys = [cls._fixColNameForGTrack(key) for key in orderedExtraKeys]

        diseaseToRowsDict = defaultdict(list)
        for row in rows:
            disease = row[diseaseColIndex]
            if isinstance(disease, unicode):
                disease = unidecode(disease).replace('\x00', '')

            diseaseToRowsDict[disease].append(row)

        progressViewer = ProgressViewer([('Create GWAS tracks for diseases/traits', len(diseaseToRowsDict))],
                                        cls.extraGalaxyFn[cls.HISTORY_PROGRESS_TITLE] )

        for disease in sorted(diseaseToRowsDict.keys()):
            uri = GalaxyGSuiteTrack.generateURI(galaxyFn=cls.extraGalaxyFn[cls.HISTORY_HIDDEN_TRACK_STORAGE],
                                                extraFileName=disease.replace('/', '_') + '.gtrack')
            gSuiteTrack = GSuiteTrack(uri, title=disease, genome=cls.OUTPUT_GENOME)
            gSuite.addTrack(gSuiteTrack)

            shouldLiftOver = cls.DATABASE_GENOME != cls.OUTPUT_GENOME
            if shouldLiftOver:
                liftOver = LiftOver(cls.DATABASE_GENOME, cls.OUTPUT_GENOME)

            geList = []
            for row in diseaseToRowsDict[disease]:
                extra = {}
                for col, index in zip(orderedExtraKeys, extraIndexes):
                    cell = row[index].strip()
                    if isinstance(cell, unicode):
                        cell = unidecode(cell)

                    extra[col] = cell if cell != '' else '.'

                chrom = 'chr' + row[chrColIndex]
                if chrom == 'chr23':
                    chrom = 'chrX'
                if chrom == 'chr24':
                    chrom = 'chrY'
                if chrom == 'chrMT':
                    chrom = 'chrM'

                start = int(row[startColIndex])
                if shouldLiftOver:
                    newPosList = liftOver.convert_coordinate(chrom, start)
                    if newPosList is None or len(newPosList) != 1:
                        print 'SNP with position %s on chromosome %s ' % (chrom, start) +\
                              'could not be lifted over from reference genome ' +\
                              '%s to %s (for disease/trait "%s")' % \
                              (cls.DATABASE_GENOME, cls.OUTPUT_GENOME, disease)
                    else:
                        chrom, start = newPosList[0][0:2]
                #print extra
                geList.append(GenomeElement(chr=chrom, start=start,
                                            val=row[valColIndex], orderedExtraKeys=orderedExtraKeys,
                                            extra=extra))

            geSource = GtrackGenomeElementSource(cls.GTRACK_BLUEPRINT_PATH)
            wrappedGeSource = ListGESourceWrapper(geSource, geList)
            composer = ExtendedGtrackComposer(wrappedGeSource)
            composer.composeToFile(gSuiteTrack.path)

            progressViewer.update()

        GSuiteComposer.composeToFile(gSuite, outFile)

    @classmethod
    def getOutputName(cls, choices):
        from quick.gsuite.GSuiteHbIntegration import getGSuiteHistoryOutputName

        description = cls._getAttrSelectionDescription(choices)
        return getGSuiteHistoryOutputName('primary', description)

