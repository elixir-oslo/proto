#!/usr/bin/env python
import ast

import mechanize
import time
import os.path
import re
from gold.util.CustomExceptions import MissingEntryError, ArgumentValueError
from gold.util.CommonFunctions import createOrigPath, createCollectedPath
from quick.util.CommonFunctions import ensurePathExists
from gold.description.TrackInfo import TrackInfo
from quick.util.GenomeInfo import GenomeInfo
from gold.application.LogSetup import logMessage
from quick.application.GalaxyInterface import GalaxyInterface
UCSC_CACHED_PATH = "/tmp"

class UcscHandler(object):
    UCSC_CATEGORIES = ('clade','org','db', 'hgta_group','hgta_track','hgta_table','hgta_outputType' )
    GENOME_TO_CATEGORY_PATH = '/Users/trengere/HB/ucsc_docs/'
    BED_TRACKNAME_SUFFIX = 'bed'
    CATBED_TRACKNAME_SUFFIX = 'category.bed'
    DATA_TRACKNAME_SUFFIX = 'primaryTable'
    WIG_TRACKNAME_SUFFIX = 'bedgraph'
    
    def __init__(self, state=None):
        if state:
            temp = state.split('#')
            self._sessionId = temp[0]
            self._genome = temp[-2]
            self.valueListOfDicts = ast.literal_eval(temp[-1])
        else:
            self._sessionId = self._genome = None
            self.valueListOfDicts = []
    
    
    def genomeToCategoryValues(self, genome):
        gi = GenomeInfo(genome)
        if gi.ucscClade != '' and gi.ucscGenome != '' and gi.ucscAssembly != '':
            return [gi.ucscClade, gi.ucscGenome, gi.ucscAssembly]
        return []
        
    def getPrettyTrackNameStr(self):
        return self.valueListOfDicts[-1].keys()[0] if self.valueListOfDicts else ''    
    
    def _getNextParamKey(self, get_key=None):
        next_key_dict = {'clade':'org', 'org':'db', 'db':'hgta_group', 'hgta_group':'hgta_track', 'hgta_track':'hgta_table',\
                         'hgta_table':'hgta_outputType','hgta_outputType':None}
        return next_key_dict[get_key] if get_key else 'clade'
        

    def _makeUrlstreng(self, hgsid=False, param=False, valg=False):
        #http://genome-mirror.moma.ki.au.dk/cgi-bin/hgTables
        return 'http://genome.ucsc.edu/cgi-bin/hgTables'+ ('?hgsid=%s&%s=%s' % (hgsid,param, valg.replace(' ','+')) if hgsid else '')
        
    
    def _getWebPageAndForm(self, urlstreng):
        request_obj = mechanize.Request(urlstreng)
        request_obj.add_header('User-Agent','Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_3; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/8.0.552.237 Safari/534.10')
        webObject = mechanize.urlopen(request_obj)
        
        return webObject, self._getForm(webObject)
    
    def _getForm(self, response):
        forms = mechanize.ParseResponse(response, backwards_compat=False)       
        return forms[0]
    
    def _loopThroughAllPages(self, genome, trackNames):
        parameterValueList = self.genomeToCategoryValues(genome) + trackNames[1:]
        
        webObject, paramForm = self._getWebPageAndForm(self._makeUrlstreng())
        UCSC_CATEGORIES = ('clade','org','db', 'hgta_group','hgta_track','hgta_table','hgta_outputType' )
        for i in range(min(len(UCSC_CATEGORIES), len(parameterValueList))):
            time.sleep(0.5)
            webObject, paramForm = self._getWebPageAndForm( self._makeUrlstreng(paramForm['hgsid'], self.UCSC_CATEGORIES[i], parameterValueList[i]) )
        return webObject, paramForm
        
    def _loopThroughUcscPages(self, genome, category, catValue):
        #logMessage('category and catval = '+str(category)+', '+str(catValue))
        if not (category and catValue):
            parameterValueList = self.genomeToCategoryValues(genome)
            webObject, paramForm = self._getWebPageAndForm(self._makeUrlstreng())
        
            for i in range(len(parameterValueList)):
                time.sleep(0.5)
                webObject, paramForm = self._getWebPageAndForm( self._makeUrlstreng(paramForm['hgsid'], self.UCSC_CATEGORIES[i], parameterValueList[i]) )
            
            self._category = self.UCSC_CATEGORIES[len(parameterValueList)-1]
            self._catValue = parameterValueList[-1]
            return paramForm    
        else:
            webObject, paramForm = self._getWebPageAndForm( self._makeUrlstreng(self._sessionId, category, catValue) )
            return paramForm
   
        
    def isGenomeAvailable(self, genome):
        parameterValueList = self.genomeToCategoryValues(genome)
        return len(parameterValueList) == 3 
        
    
    def _storeUcscInfoBox(self, genome, parameterForm, trackName):
        htmlText = mechanize.urlopen(parameterForm.click('hgta_doSchema')).read()
        htmlText = htmlText.replace('h2>','H2>').replace('p>', 'P>').replace('<a href','<A HREF')
        
        #open('/tmp/TrackInfo_UcscHtmlDump.txt','w').write(htmlText)
        htmlSubText = htmlText[htmlText.find('<H2>'):htmlText.rfind('</P>')].replace('<A HREF="http:..', ' <A HREF="http://genome.ucsc.edu')
        #logMessage('htmlTrackInfo:  '+htmlSubText[:50])
        if htmlSubText:
            htmlSubText += '</P>'
            print ' : '.join(trackName) +',   '+genome
            trackInfoObject = TrackInfo(genome, trackName)
            tInfoVarConverter = {'Description':'description', 'Methods':'methods', 'Credits':'credits','References':'reference', 'Data Release Policy':'restrictions', 'Display Conventions and Configuration':'displayConvConf'}
        
            htmlSubList = htmlSubText.split('<H2>')[1:]            
            for i in htmlSubList:
                header = i[:i.find('</H2>')].replace(':','').strip()
                if header in tInfoVarConverter.keys():
                    setattr(trackInfoObject, tInfoVarConverter[header], i.split('</H2>')[1])
                    
                    
                #if header == 'Description':
                #    print 'Description'
                #    trackInfoObject.description = i.split('</H2>')[1]
                #elif header == 'Methods':
                #    print 'Methods'
                #    trackInfoObject.methods = i.split('</H2>')[1]
                #elif header == 'Credits':
                #    print 'Credits'
                #    trackInfoObject.credits = i.split('</H2>')[1]
                #elif header == 'References':
                #    print 'References'
                #    trackInfoObject.reference = i.split('</H2>')[1]
                #else:
                #    pass
            trackInfoObject.store()
    
    def getUcscMetaData(self, genome, parameterForm, trackName):
        htmlText = mechanize.urlopen(parameterForm.click('hgta_doSchema')).read()
        htmlSubText = htmlText[htmlText.upper().find('<H2>'):htmlText.upper().rfind('</P>')].replace('<A HREF="http:..', ' <A HREF="http://genome.ucsc.edu')
        htmlMetaData = dict()
        tInfoVarConverter = {'Description':'description', 'Methods':'methods', 'Credits':'credits','References':'reference', 'Data Release Policy':'restrictions', 'Display Conventions and Configuration':'displayConvConf'}
        if htmlSubText:
            htmlSubText += '</P>'
            
            htmlSubList =  re.split('<[hH]2>', htmlSubText)[1:]            
            for i in htmlSubList:
                header = i[:i.find('</')].replace(':','').strip()
                if header in tInfoVarConverter.keys():
                    htmlMetaData[tInfoVarConverter[header]] = re.split('</[hH]2>',i)[1]
                else:
                    pass
        return htmlMetaData
    
            
    def _isSameGenome(self,genome):
        if not genome == self._genome:
            self._sessionId = None
            self._genome = genome
            self.valueListOfDicts = []
    
    def _filterValues(self, valueList):
        filterlist = [('All Tracks', 'allTracks', False), ('All Tables', 'allTables', False)]
        for i in filterlist:
            if i in valueList:
                valueList.remove(i)
        return valueList
    
    
    def getFinalLevelTrackNames(self, genome, trackName):
        webObject, paramForm = self._loopThroughAllPages(genome, trackName)
        outputType = [item.name for item in paramForm.find_control("hgta_table").items]
        return outputType
    
    def getSubTrackNames(self, genome, trackName=[]):
        self._category = self.UCSC_CATEGORIES[len(trackName)+1]# gets right category based on length of trackName
        #logMessage('trackName = '+str(trackName))
        self._isSameGenome(genome)
        #check if its in the cache first...
        indexLastElInTrackName = len(trackName)-1
        if len(self.valueListOfDicts) >= len(trackName) and self.valueListOfDicts[indexLastElInTrackName].has_key(trackName[-1]):
            
            valueList = self.valueListOfDicts[indexLastElInTrackName][trackName[-1]]
            return valueList, self.makeState()
        
        #if not get it from UCSC-Pages...                   
        else:
            self.valueListOfDicts = self.valueListOfDicts[:indexLastElInTrackName]
    
            self._catValue = trackName[-1] if self._category and not trackName[-1]=='ucsc' else None
            paramForm = self._loopThroughUcscPages(genome, self._category, self._catValue )
            self._sessionId = paramForm['hgsid']
            
            if self._category =='hgta_outputType':
                
                self._storeUcscInfoBox(genome, paramForm, trackName)
                return [], self.makeState()
        
            else:
                nextCategory = self._getNextParamKey(self._category)
                
                if nextCategory == 'hgta_outputType':
                    outputType = [item.name for item in paramForm.find_control("hgta_outputType").items]

                    valueList = [('Segments (BED)', self.BED_TRACKNAME_SUFFIX, False), ('Valued Segments (Categorical BED)', self.CATBED_TRACKNAME_SUFFIX, False)] \
                                if 'bed' in outputType or 'wigBed' in  outputType else []
                else:
                    valueList = self._filterValues([(item.attrs['label'], item.name, False) for item in paramForm.find_control(self._getNextParamKey(self._category)).items])
                    if nextCategory=='hgta_table':
                        valueList = self._filterValueListAndMakeTrackInfoObjects(nextCategory, valueList, genome, trackName)
                   
                self.valueListOfDicts.append({trackName[-1]:valueList})
                #logMessage(str(valueList))
                return valueList, self.makeState()
    
    def makeState(self):
        return self._sessionId+'#'+self._genome+'#'+str(self.valueListOfDicts)
    
    def _filterValueListAndMakeTrackInfoObjects(self, category, valueList, genome, trackName):
        prunedValueList = []
        trackNames = [trackName+[v[1]]for v in valueList]
        for index, trackTuple in enumerate(trackNames):
            trackInfoObj = TrackInfo(genome, trackTuple)
            if trackInfoObj.fileType =='':
                
                webObject, paramForm = self._getWebPageAndForm( self._makeUrlstreng(self._sessionId, 'hgta_table', trackTuple[-1]) )
                self._storeUcscInfoBox(genome, paramForm, trackTuple)
                if set(['bed', 'wigBed']) & set(['.']+[item.name for item in paramForm.find_control("hgta_outputType").items]):
                        lastForm = self._getForm(mechanize.urlopen(paramForm.click('hgta_doFilterPage')))
                        if len([control.name for control in lastForm.controls if control.name.find('_.maxOutput')>0]) == 0:
                            prunedValueList.append(valueList[index])
                            trackInfoObj.fileType = 'bed'
                trackInfoObj.fileType = 'ucscdb' if trackInfoObj.fileType == '' else 'bed'            
            elif trackInfoObj.fileType =='bed':
                prunedValueList.append(valueList[index]) 
            trackInfoObj.store()
            
        return prunedValueList
    
        
    def getTableData(self, genome, trackName):
        webObject, paramForm = self._getWebPageAndForm( self._makeUrlstreng(self._sessionId, 'hgta_outputType', trackName[-1]) )
        response = mechanize.urlopen(paramForm.click('hgta_doTopSubmit'))
        fn = createCollectedPath(genome, trackName, 'fromUcsc.'+trackName[-1])
        ensurePathExists(fn)
        open(fn,'w').write(response.read())    
    
    
    def downloadTrack(self, genome, trackName):
        if trackName[-1]=='primaryTable':
            self.getTableData(genome, trackName)
        else:
            bedString, metaData = self.getBedData(genome, trackName)
            #fileName = 'fromUcsc.bed' if trackName[-1][-3:] == 'bed' else 'fromUcsc.'+trackName[-1]
            fileName = 'fromUcsc.'+trackName[-1]
        
            fn = createOrigPath(genome, trackName, fileName)
            ensurePathExists(fn)
            open(fn,'w').write(bedString)
        
        
    def getBedData(self, genome, trackName):
        
        outputType = 'bed' if trackName[-1]=='category.bed' else trackName[-1]
        if not self._sessionId:
            
            webObject, paramForm = self._loopThroughAllPages(genome, trackName)
        else:
            webObject, paramForm = self._getWebPageAndForm( self._makeUrlstreng(self._sessionId, 'hgta_outputType', outputType) )
        
        metaData = self.getUcscMetaData(genome, paramForm, trackName)
        response = mechanize.urlopen(paramForm.click('hgta_doTopSubmit'))
        returnStr = None
        if outputType in ['wigData','primaryTable'] :
            returnStr = response.read()
        try:
            lastForm =  self._getForm(response)
            temp = mechanize.urlopen(lastForm.click('hgta_doGetBed')).read()
            if temp.strip() =='':
                raise MissingEntryError
            returnStr =  temp
        except:
            returnStr = response.read()
        return returnStr, metaData
    
#if __name__ == "__main__":
#    ucscObject = UcscHandler()
#    
#    ucscObject.getSubTrackNames('hg18',['ucsc'])
#    session=raw_input('skriv inn session_id: ')
#    while True:
#        key=raw_input('skriv inn key: ')
#        index =int(raw_input('skriv inn index for value: '))
#        value = ucscObject.valueList[index]
#        
#        ucscObject = UcscHandler(tilstand)
#        ucscObject.getSubTrackNames('hg18',['ucsc',tilstand,value])
#        if hasattr(ucscObject, 'state'):
#            tilstand = ucscObject.state
#        else:
#            break
#     
