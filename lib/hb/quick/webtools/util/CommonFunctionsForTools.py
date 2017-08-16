import urllib
from quick.origdata.UcscHandler import UcscHandler
from gold.application.LogSetup import logException
from gold.util.CustomExceptions import AbstractClassError

def validateURLs(urls):
    for url in urls:
        urlError = validateURL(url)
        if urlError:
            return urlError

def validateURL(url):
    try:
        filehandle=urllib.urlopen(url)
        code = filehandle.getcode()
        if code != 200 and filehandle.url[:filehandle.url.find('://')] not in ['sftp', 'ftp', 'file']:
            return "Url: " + url + " did not return a file, HTTP code="+str(code)
    except IOError, e:
        return "Url: %s was not accepted as a valid URL. Error: %s" % (url, str(e))
    
def validateUcscValues(ucscValues):
    if not (all(x != '' for x in ucscValues) or all(x == '' for x in ucscValues)):
        return 'Either none or all UCSC mapping attributes must be set.'
    
    if all(x != '' for x in ucscValues):  
        ucscHandler = UcscHandler()
        try:
            if not ucscHandler.isUcscValuesCorrect(ucscValues):
                return 'UCSC mapping values do not correspond to an assembly in the UCSC database.'
        except Exception, e:
            logException(e)
            pass
        
def processIndicesString(rowIndicesStr):
    '''
    Get list of indices from a string input 
    e.g.
    1-10, 13, 19 -> [1,2,3,4,5,6,7,8,9,13,19]
    '''
    selectedIndices = []
    for indexPart in rowIndicesStr.split(','):
        if '-' in indexPart:
            startIndex, endIndex = [int(x.strip()) for x in indexPart.split('-')]
            selectedIndices += list(xrange(startIndex, endIndex))
        else:
            selectedIndices.append(int(indexPart.strip())) #assuming single value
    return selectedIndices