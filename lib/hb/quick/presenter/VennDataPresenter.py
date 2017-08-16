from gold.result.Presenter import Presenter
from gold.util.CommonFunctions import strWithStdFormatting
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.webtools.plot.CreateBpsVennDIagram import CreateBpsVennDIagram
class VennDataPresenter(Presenter):
    def __init__(self, results, baseDir=None):
        Presenter.__init__(self, results, baseDir)

    def getDescription(self):
        return 'Summary'
        
    def getReference(self, resDictKey):
        globalRes = self._results.getGlobalResult()
        htmlObj = GalaxyRunSpecificFile(['test.html'], self._baseDir)
        fileObj = open(htmlObj.getDiskPath(ensurePath=True),'w')
        #fileObj.write( 'globalRes ' + str(globalRes))
        htmlText = CreateBpsVennDIagram.getHtmlString(globalRes['result']['catInfo'], globalRes['result']['stateBPCounter'], globalRes['result']['genome'])
        fileObj.write(htmlText)
        fileObj.close()

        return htmlObj.getLink('link to results')
        return str(globalRes)
        return strWithStdFormatting( globalRes[resDictKey] ) if globalRes not in [None,{}] else 'None'


