import re

from config.Config import STATIC_PATH
from proto.hyperbrowser.HtmlCore import HtmlCore


class GtrackSpecParser(object):
    def __init__(self, filPath, outFilePath):
        self.core = HtmlCore()
        self.specStr = open(filPath,'r').read()
        self.outFilePath = outFilePath
        self.htmlMal = '<html><body>%s</body></html>'
        self.htmlStr = ''
        self.divCounter = 0
        self.fullContentTab =[]

    def getContentList(self):
        return self.specStr.split('\n----------------')[2].strip().split('\n')
    
    def getContentlineSearcStr(self, line):
        anchorIndex = 0
        if line.strip().startswith('*'):
            anchorIndex = 2
            searchStr = line[2:].strip()+'\n----'
        elif len(line.strip()) and line.strip() == '-':
            anchorIndex = line.find('-')+4
            searchStr = line.strip()[2:].strip()+'\n  ----'
        elif line.strip()!='':
            anchorIndex = 8
            searchStr = line.strip().replace('  ',' ')+'\n  ----'
        else:
            searchStr = None
        return searchStr, anchorIndex
        #x.  Comments
        
    def findAll(self, substring, string):
        starts = [match.start() for match in re.finditer(re.escape(substring), string)]
        return [x for i,x in enumerate(starts) if i == 0 or i > 0 and x - starts[i-1] != len(substring)]
        
    def checkHeader(self, header, contentStr, devNotes=True):
        headerIndex = contentStr.find(header)
        falseHeaderIndex = contentStr.find('"' + header)
        if headerIndex != -1 and not (falseHeaderIndex != -1 and headerIndex == falseHeaderIndex +1):
            devChunckList = contentStr.split(header)
            resultStr = devChunckList[0]
            for value in devChunckList[1:]:
                resultStr+= '''<a onclick ="javascript:ShowHide('HiddenDiv%s')" href="javascript:;" >%s</a>''' % (str(self.divCounter), header)
                dashLine = '-' * len(header)
                if devNotes:
                    dotList = value.split(dashLine)
                    resultStr+= '<div class="mid" id="HiddenDiv%s" style="DISPLAY: none" >%s%s%s%s</div>' % (str(self.divCounter), dotList[0], dashLine, dotList[1], dashLine)+dashLine.join(dotList[2:])
                else:
                    lastDashLine = self.findAll('----', value)[-1]
                    if value[lastDashLine-2:lastDashLine] == '  ':
                        lastDashLine -= 2
                    mainContent = ''.join(value[1:lastDashLine])
                    newHeader = ''.join(value[lastDashLine:])
                    resultStr+= '<div class="mid" id="HiddenDiv%s" style="DISPLAY: none" >%s</div>\n  ' % (str(self.divCounter), mainContent) + dashLine + '\n\n' + newHeader
                self.divCounter+=1
            return resultStr
        else:
            return contentStr
        
    def checkRestrictions(self, contentStr):
        if contentStr.find('- Restrictions')>0:
            devChunckList = contentStr.split('- Restrictions')
            resultStr = devChunckList[0]
            for value in devChunckList[1:]:
                resultStr+= '''- <a onclick ="javascript:ShowHide('HiddenDiv%s')" href="javascript:;" >Restrictions</a>\n''' % str(self.divCounter)
                restrictTab, extraTab = [], []
                valueTab = value.split('\n')
                
                for index, resVal in enumerate(valueTab):
                    if resVal.strip() == '' or (len(resVal) > 2 and resVal[2].isspace()):
                        restrictTab.append(resVal)
                    else:
                        extraTab = valueTab[index:]
                        break
                        
                for val in restrictTab:
                    if val.strip() == '':
                        restrictTab = restrictTab[1:]
                    else:
                        break
                        
                for val in reversed(restrictTab):
                    if val.strip() == '':
                        restrictTab = restrictTab[:-1]
                    else:
                        break
                    
                resultStr+= '<div class="mid" id="HiddenDiv%s" style="DISPLAY: none" >\n%s</div>' % (str(self.divCounter), '\n'.join(restrictTab))+'\n\n' + '\n'.join(extraTab)
                self.divCounter+=1
            return resultStr
        else:
            return contentStr
        
    
    
    def parseSpecFile(self):
        contentList =  self.getContentList()
        # TODO: make sure that scripts and css are imported
        # relatively with "../../" instead of absolute path
        # For now, change the resulting HTLM file manually
        self.core.begin()
        self.core.script("function ShowHide(divId)\n{\nif(document.getElementById(divId).style.display == 'none')\n{\ndocument.getElementById(divId).style.display='block';\n}\nelse\n{\ndocument.getElementById(divId).style.display = 'none';\n}\n}\n")
        self.core.append('<pre class="largefont">'+self.specStr.split(contentList[0])[0])
        for i in contentList:
            searchStr, entry = self.getContentlineSearcStr(i)
            self.core.append(i[:entry])
            self.core.link(i[entry:], '#'+searchStr.split('\n')[0])
            self.core.append('\n')
        
        self.core.append('\n\n\n')
        for index, value in enumerate(contentList):
            print value
            startPoint, entry = self.getContentlineSearcStr(value)
            endPoint, entry =  self.getContentlineSearcStr(contentList[index +1]) if index +1 < len(contentList) else (None, 0)
            self.core.anchor('', startPoint.split('\n')[0])
            content = self.specStr[self.specStr.find(startPoint):] if not endPoint else self.specStr[self.specStr.find(startPoint):self.specStr.find(endPoint)]
            content = self.checkHeader('Developer notes', content, True)
            content = self.checkHeader('Detailed specification of character usage', content, False)
            content = self.checkHeader('Redefining column names', content, False)
            content = self.checkHeader('WIG compatibility', content, False)
            content = self.checkHeader('FASTA compatibility', content, False)
            content = self.checkHeader('Defining GTrack subtypes', content, False)
            content = self.checkRestrictions(content)
            self.core.append(content)
        self.core.append('</pre>')
        self.core.end()
        utfil = open(self.outFilePath,'w')
        utfil.write(str(self.core))
        #print self.core
    
    #def parseSpecFile(self):
    #    contentList =  self.getContentList()
    #    self.core.append('<pre>'+self.specStr.split(contentList[0])[0])
    #    for i in contentList:
    #        self.core.link(i, '#'+self.getContentlineSearcStr(i).split('\n')[0])
    #        
    #    self.fullContentTab.append('\n'.join(['<a href="#%s">%s</a>' % (self.getContentlineSearcStr(v).split('\n')[0],v) for v in contentList])+'\n\n')
    #    utfil = open('resultat.html','w')
    #    
    #    for index, value in enumerate(contentList):
    #        print value
    #        startPoint = self.getContentlineSearcStr(value)
    #        endPoint =  self.getContentlineSearcStr(contentList[index +1]) if index +1 < len(contentList) else None
    #        content = '<a name="%s">%s</a>' % (startPoint.split('\n')[0],startPoint) + (gParser.specStr.split(startPoint)[1] if not endPoint else gParser.specStr.split(startPoint)[1].split(endPoint)[0])
    #        self.fullContentTab.append(content)    
    #    utfil.write( self.htmlMal % ('<pre>'+''.join(gParser.fullContentTab)+'</pre>'))
    
        #return searchStr+self.specStr.split(searchStr)[1].split('\n\n----')[0] if searchStr else -1


if __name__ == '__main__':
    #gParser = GtrackSpecParser(STATIC_PATH+'/gtrack/GTrack_specification.txt',
    #                           STATIC_PATH+'/gtrack/GTrack_specification.html')
    #gParser.parseSpecFile()
    gParser = GtrackSpecParser(STATIC_PATH+'/gsuite/GSuite_specification.txt',
                               STATIC_PATH+'/gsuite/GSuite_specification.html')
    gParser.parseSpecFile()
    #contentList =  gParser.getContentList()
    #utfil = open('resultat.html','w')
    #for index, value in enumerate(contentList):
    #    print value
    #    startPoint = gParser.getContentlineSearcStr(value)
    #    endPoint =  gParser.getContentlineSearcStr(contentList[index +1]) if index +1 < len(contentList) else None
    #    content = startPoint + (gParser.specStr.split(startPoint)[1] if not endPoint else gParser.specStr.split(startPoint)[1].split(endPoint)[0])
    #    gParser.fullContentTab.append(content)
    #gParser.fullContentTab.insert(0, '\n'.join(contentList)+'\n\n')
    #    
    #utfil.write( gParser.htmlMal % ('<pre>'+''.join(gParser.fullContentTab)+'</pre>'))
    #    #print '\n\n\n\n\n\n'
        
        
