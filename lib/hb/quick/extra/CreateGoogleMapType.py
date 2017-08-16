import os, shutil
import sys
from quick.util.CommonFunctions import ensurePathExists
from quick.extra.CustomFuncCatalog import makeLowercaseName2NameShelfFromTnSubTypes, createShelvesBehindRankedGeneLists
from config.Config import STATIC_PATH


def createMapType(mapId, genome, rowTrackName, colTrackName, col2GeneListFn, galaxyId, countType):

    googleMapsCommonDir = '/'.join([STATIC_PATH, 'maps', 'common'])
    googleMapsMapIdDir = '/'.join([googleMapsCommonDir, mapId])
    
    ensurePathExists(googleMapsMapIdDir + '/test')
    
    makeLowercaseName2NameShelfFromTnSubTypes(genome, rowTrackName, '/'.join([googleMapsMapIdDir, 'rowLowerCaseName2Name.shelf']))
    makeLowercaseName2NameShelfFromTnSubTypes(genome, colTrackName, '/'.join([googleMapsMapIdDir, 'colLowerCaseName2Name.shelf']))
    
    rowBaseTrackNameFile = open('/'.join([googleMapsMapIdDir, 'rowBaseTrackName.txt']), 'w')
    colBaseTrackNameFile = open('/'.join([googleMapsMapIdDir, 'colBaseTrackName.txt']), 'w')
    
    rowBaseTrackNameFile.write(rowTrackName + '\n')
    colBaseTrackNameFile.write(colTrackName + '\n')
    
    rowBaseTrackNameFile.close()
    colBaseTrackNameFile.close()
    
    if col2GeneListFn != 'None':
        shutil.copy(col2GeneListFn, '/'.join([googleMapsMapIdDir, 'col2GeneList.shelf']))
        createShelvesBehindRankedGeneLists(galaxyId, mapId, countType)
if '__name__' == '__main__':
    if len(sys.argv) != 8:
        print 'Usage: python createGoogleMapType.sh mapId genome rowTrackName colTrackName col2GeneListFn galaxyId countType'
        sys.exit(0)

    mapId, genome, rowTrackName, colTrackName, col2GeneListFn, galaxyId, countType = [sys.argv[x] for x in [1,2,3,4,5,6,7]]
    createMapType(mapId, genome, rowTrackName, colTrackName, col2GeneListFn, galaxyId, countType)
