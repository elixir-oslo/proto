import os
import csv
import time 
import cPickle as pickle
import operator
import math
from quick.webtools.restricted.DianasTool3 import vis
from quick.application.ExternalTrackManager import ExternalTrackManager

class calculationPS():
    
    def __init__(self, folderFileList, matureFile, precursorFile):
        self._folderFileList= folderFileList
        self._matureFile = matureFile
        self._precursorFile=precursorFile

    def readFile(self, precursor):
        
        with open(ExternalTrackManager.extractFnFromGalaxyTN(precursor), 'r') as f:
            read=[]
            readsDict={}
            precursorDict={}
            i=0
            for line in f:
                if i%2==0:
                    name = line.strip('\n').replace('\r','').replace('>', '').split('_')[0]
                else:
                    psDict={}
                    psDict1={}
                    psDict2={}
                    
                    for chNum in range(0, len(line)):
                        psDict[chNum]=0
                        psDict1[chNum]=0
                        psDict2[chNum]=0
                    
                    elLine=line.strip('\n').replace('\r','')
                    precursorDict[name] = list(elLine)
                    read.append([name, elLine, psDict, psDict1, [], psDict2])
                    readsDict[name]={}
                    
                    for j in range(0, 2):
                        readsDict[name][j] = {}
                        readsDict[name][j]['values'] = []
                        readsDict[name][j]['totalVal'] = []
                        readsDict[name][j]['rpm'] = []
                i+=1
        f.closed
        
        print 'done readFile Precursor'
        
        return read, precursorDict, readsDict
    
    def readFileMatures(self, mature, newFileList):

        number = 30
        with open(ExternalTrackManager.extractFnFromGalaxyTN(mature), 'rb') as f:
            readCsv = csv.reader(f, delimiter='\t', quotechar='|')
            read={}
            
            for line in readCsv:
                name = line[0].split('_')[0]
                
                for fL in newFileList:
                    if not fL in read.keys():
                        read[fL]={}
                    
                    #m c red, s blue 
                    if not name in read[fL].keys():
                        read[fL][name]={}
                        
                    
                    #blue
                    if 's' in line[1]:
                        if not 'star' in read[fL][name]:
                            read[fL][name]['star']={}
                        read[fL][name]['star']['values'] =  [x for x in range(int(line[2]) + number,  int(line[3]) + number)]
                        
                        for el1 in ['template-reads', 'non-templated-reads', 'non-templated-readsLetter', 'non-templated-readsLetterNot']:
                            if not el1 in read[fL][name]['star']:
                                read[fL][name]['star'][el1]={}
                        
                         
                        for el in ["5' elongated", "5' truncated", "3' elongated", "3' truncated", 'both elongated', 'both truncated', 'canonical']:
                            for el1 in ['template-reads', 'non-templated-reads']:
                                if not el in read[fL][name]['star'][el1]:
                                    read[fL][name]['star'][el1][el]=0
                            for el1 in ['non-templated-readsLetter', 'non-templated-readsLetterNot']:
                                if not el in read[fL][name]['star'][el1]:
                                    read[fL][name]['star'][el1][el]=[]
                    #red                
                    elif 'm' in line[1] or 'c' in line[1]:
                        
                        elM='mature'
                        if not 'star' in read[fL][name]:
                            if 'mature' in read[fL][name]:
                                elM='co-mature'
                                        
#                         elM=''
#                         if 'star' in read[fL][name]:
#                             elM='mature'
#                         else:
#                             if 'mature' in read[fL][name]:
#                                 elM='co-mature'
#                             else:
#                                 elM='mature'
                            
                        if not elM in read[fL][name]:
                            read[fL][name][elM]={}
                        read[fL][name][elM]['values'] =  [x for x in range(int(line[2]) + number,  int(line[3]) + number)]
                        
                        
                        for el1 in ['template-reads', 'non-templated-reads', 'non-templated-readsLetter', 'non-templated-readsLetterNot']:
                            if not el1 in read[fL][name][elM]:
                                read[fL][name][elM][el1]={}
                        
                         
                        for el in ["5' elongated", "5' truncated", "3' elongated", "3' truncated", 'both elongated', 'both truncated', 'canonical']:
                            for el1 in ['template-reads', 'non-templated-reads']:
                                if not el in read[fL][name][elM][el1]:
                                    read[fL][name][elM][el1][el]=0
                            for el1 in ['non-templated-readsLetter', 'non-templated-readsLetterNot']:
                                if not el in read[fL][name][elM][el1]:
                                    read[fL][name][elM][el1][el]=[]
            #banaj
            
        f.closed
        print 'done readFile Matures'
        
        return read
    
    def findStringValue(self, sign):
        
        if 'x' in sign:
            return int(sign.split('x')[1])
        
        if '#' in sign:
            return int(sign.split('#')[1])
        
    
    def readFilesPre(self, fileList):
        
        fileTotal = {}
        for filename in fileList:
            if filename not in fileTotal:
                fileTotal[filename] = 0
               
            with open(self._folderFileList + '/' + filename, 'rb') as f:
                for line in csv.reader(f, delimiter='\t', quotechar='|'):
                    if line[0] != '@PG' and line[0] !='@SQ' and line[0] !='@HD' and line[2]!= '*':
                        fileTotal[filename] += self.findStringValue(line[0])
            if fileTotal[filename] == 0:
                del fileTotal[filename]
                
        
        print 'done readFilesPre'
        return fileTotal
    
    def readFiles(self, fileList,  mature, readsDict, fileTotal):
        
        letterDict={}
        readDict=[]
        
        for filename in fileList:
            
            print 'Open file ' + str(filename)
            
            if filename in fileTotal:
                fileTotal[filename] = float(fileTotal[filename])/1000000
                
            totalVal=0
            readDictPart={}
            with open(self._folderFileList + '/' + filename, 'rb') as f:
                readCsv = csv.reader(f, delimiter='\t', quotechar='|')
                i=0
                fL = filename.split('.')[0]
                readDictPart['fileName']=fL
                
                if not fL in letterDict.keys():
                    letterDict[fL] = {}
                
                readDictPart['values']={}
                
                for line in readCsv:
                    if line[0] != '@PG' and line[0] !='@SQ' and line[0] !='@HD':
                        name = line[2].split('_')[0]
                        if name not in readDictPart['values']:
                            readDictPart['values'][name] = []
                        
                        if not name in letterDict[fL].keys():
                            letterDict[fL][name] = {}
                        
                        if line[2]!= '*':
                            findStrVal = self.findStringValue(line[0])
                            if findStrVal/fileTotal[filename] >= 1:
                                
                                mismatch=0
                                if len(line) == 14:
                                    mismatch = int(line[13].replace('NM:i:', ''))
                                    if mismatch !=0:
                                        mismatch = 1
                                
                                if mismatch ==0:
                                    pS = int(line[3])
                                    pK = len(line[9])
                                    readDictPart['values'][name].append([findStrVal, pS, pK, mismatch])
                                    
                                    read = []
                                    for el in range(0, int(line[3])):
                                        read.append('')
                                    read+= list(line[9])
                                    readsDict[name][0]['values'].append(read)
                                    readsDict[name][0]['totalVal'].append(findStrVal)
                                    readsDict[name][0]['rpm'].append(fileTotal[filename])
                                       
                                    mature[fL][name] = self.calculateStatistic(mature[fL][name], [findStrVal, pS, pK, mismatch], 'template-reads', [])
                                    
                                else:
                                    
                                    read = ['' for el in range(0, int(line[3]))]
#                                     for el in range(0, int(line[3])):
#                                         read.append('')
                                    read += list(line[9])
                                    readsDict[name][1]['values'].append(read)
                                    readsDict[name][1]['totalVal'].append(findStrVal)
                                    readsDict[name][1]['rpm'].append(fileTotal[filename])
                                    
                                    #count mismatches
                                    gapNum = int(line[13].replace('NM:i:', ''))
                                    
                                    mismatchIndexList = []
                                    tempLine12 = line[12].replace('MD:Z:','')
                                    mm = ''
                                    nm='MDZ'
                                    countMmInt=0
                                    
                                    
                                    for elTempList in tempLine12:
                                        if elTempList.isdigit():
                                            mm += mm.join(elTempList)
                                        else:
                                            mmInt = int(mm)
                                            countMmInt+=mmInt        
                                            mismatchIndexList.append([nm, '', int(mm), list(line[9])])
                                            nm=''
                                            mm=''
                                            nm += nm.join(elTempList)
                                    
                                    
                                    mismatchIndexList.append([nm, '', int(mm), list(line[9])])
                                    
                                    mismatchPos=-1
                                    gapList=[]
                                    if len(mismatchIndexList) == 1:
                                        mismatchPos=mismatchIndexList[0][2]
                                    elif len(mismatchIndexList) >= 2:
                                        mismatchPos=mismatchIndexList[0][2]
                                        if gapNum >1:
                                            for elInd in range(1, len(mismatchIndexList)):
                                                gapList.append(mismatchIndexList[elInd][2])
                                    mismatchPos = int(mismatchPos)-1
                                    
                                    resList=[]
                                    resListAll = range(int(line[3])-1,int(line[3])+len(line[9])-1)
                                    
                                    
                                    mismatchNumber  = int(gapNum)
                                    resListMismatch=[]
                                    
                                    listLetterToStatistic=[]
                                    
                                    newEl= mismatchPos+int(line[3])
                                    if len(gapList) == 0:
                                    
                                        resListMismatch = range(newEl, newEl+mismatchNumber)
                                        
                                        
                                        letterList = list(line[9])    
                                        for letterPos in resListMismatch:
                                            if not letterPos in letterDict[fL][name]:
                                                letterDict[fL][name][letterPos]=[]
                                            
                                            lPos=letterPos-int(line[3])+1
                                            
                                            if not letterDict[fL][name][letterPos]:
                                                letterDict[fL][name][letterPos].append({letterList[lPos]:findStrVal})
                                                listLetterToStatistic.append({letterPos:letterList[lPos]})
                                            else:
                                                if not letterList[lPos] in letterDict[fL][name][letterPos][0].keys():
                                                    letterDict[fL][name][letterPos].append({letterList[lPos]:findStrVal})
                                                else:
                                                    letterDict[fL][name][letterPos][0][letterList[lPos]] += findStrVal
                        
                                    else:
                                        resListMismatch=[newEl]
                                         
                                        if not newEl in letterDict[fL][name]:
                                            letterDict[fL][name][newEl]=[]
                                        
                                        let= mismatchPos+1
                                        lPos = mismatchIndexList[0][3][let]
                                        
                                        if not letterDict[fL][name][newEl]:
                                            letterDict[fL][name][newEl].append({lPos:findStrVal})
                                            listLetterToStatistic.append({newEl:lPos})
                                        else:
                                            if not lPos in letterDict[fL][name][newEl][0].keys():
                                                letterDict[fL][name][newEl][0][lPos] = findStrVal
                                            else:
                                                letterDict[fL][name][newEl][0][lPos] += findStrVal
                                        
                                        i=2
                                        #print gapList
                                        for elNum in range(0, len(gapList)-1):
                                            newEl += gapList[elNum]+1
                                            resListMismatch.append(newEl)
                                             
                                            if not newEl in letterDict[fL][name]:
                                                letterDict[fL][name][newEl]=[]
                                        
                                            let = newEl-int(line[3])+1
                                            
                                            if not letterDict[fL][name][newEl]:
                                                letterDict[fL][name][newEl].append({lPos:findStrVal})
                                                listLetterToStatistic.append({newEl:lPos})
                                            else:
                                                if not lPos in letterDict[fL][name][newEl][0].keys():
                                                    letterDict[fL][name][newEl][0][lPos] = findStrVal
                                                else:
                                                    letterDict[fL][name][newEl][0][lPos] += findStrVal
                                            i+=1
                                   
                                    
                                    mature[fL][name] = self.calculateStatistic(mature[fL][name], [findStrVal, int(line[3]), len(line[9]), mismatch], 'non-templated-reads', listLetterToStatistic)
                                    
                                    resList = list(set(resListAll)-set(resListMismatch))
                                    readDictPart['values'][name].append([findStrVal, resListMismatch, [], mismatch, resList])
                        totalVal+=findStrVal
                    i+=1
            readDictPart['totalVal']=totalVal
            readDict.append(readDictPart)
            f.closed
        
        
        
        with open('results/tempData/letterDict.pkl','wb') as fp:
            pickle.dump(letterDict,fp)    
        with open('results/tempData/mature.pkl','wb') as fp:
            pickle.dump(mature,fp)
        with open('results/tempData/readsDict.pkl','wb') as fp:
            pickle.dump(readsDict,fp)
        with open('results/tempData/readDict.pkl','wb') as fp:
            pickle.dump(readDict,fp)
        
        print 'done readFile SamFiles'
        return readDict
    
    
    def calculateStatistic(self, mature, samFile, resName, listLetterToStatistic):
        
        
        percentage = 80
        start = samFile[1]-1
        end = samFile[1] + samFile[2]-2
        samFileList = [x for x in range(start, end+1)]
        
        
        endRed=0
        startBlue=10000
        startRed = 0
        endBlue=10000
        
        
        if 'star' in mature.keys():#blue
            el='star'
            startBlue = mature[el]['values'][0]
            endBlue = mature[el]['values'][len(mature[el]['values'])-1]
            
            if 'co-mature' in mature.keys():
                el='co-mature'
                endRed = mature[el]['values'][len(mature[el]['values'])-1]
                startRed = mature[el]['values'][0]
            elif 'mature' in mature.keys():
                el='mature'
                endRed = mature[el]['values'][len(mature[el]['values'])-1]
                startRed = mature[el]['values'][0]
    
        else:
            el='co-mature'
            startBlue = mature[el]['values'][0]
            endBlue = mature[el]['values'][len(mature[el]['values'])-1]
            
            el='mature'
            endRed = mature[el]['values'][len(mature[el]['values'])-1]
            startRed = mature[el]['values'][0]
        
      
        
        for el in mature.keys():
            
            tick = False
            colorListLen = len(mature[el]['values'])
            
            if startBlue == 10000:
                colorListLen=colorListLen/2
            
            intersectionListLen = len([val for val in samFileList if val in mature[el]['values']])
            
            
            if intersectionListLen > float(percentage)/100*colorListLen:
                #do ktorego nalezy element
                
                if endRed <= startBlue:
                    if el == 'star' or el == 'co-mature':#czy niebieski jest powyzej czerownego
                        if start > endRed:
                            tick= True
                    if el == 'mature':#czy czerwony jest ponizej niebieskiego
                        if end < startBlue:
                            tick=True
                            
                else:
                    if el == 'star' or el == 'co-mature':#czy czerwony jest ponizej niebieskiego
                        if start < endBlue:
                            tick= True
                    if el == 'mature':#czy niebieski jest powyzej czerownego
                        if end > startRed:
                            tick=True
           
            
            if tick == True:
                matSt = mature[el]['values'][0]
                matEnd = mature[el]['values'][len(mature[el]['values'])-1]
               
                samFileValue = samFile[0]
        
                
                
                temp1 = [0,0,0]
                if start == matSt:#equal
                    temp1=[1,0,0]
                elif start < matSt:#longer
                    temp1=[0,1,0]
                else:
                    temp1=[0,0,1]#shorter
                
                temp2 = [0,0,0]
                if end == matEnd:#equal
                    temp2=[1,0,0]
                elif end < matEnd:#shorter
                    temp2=[0,0,1]
                else:
                    temp2=[0,1,0]#longer
                
               
                if temp1 !=-1 and temp2!=-1:
                    
                    resList = [x + y for x, y in zip(temp1, temp2)]
                    
                    whichField=''  
                    
                    if resList[0] == 2:
                        mature[el][resName]['canonical']+=samFileValue
                        whichField='canonical'
                    elif resList[1] == 2:
                        mature[el][resName]['both truncated']+=samFileValue
                        whichField='both truncated'
                    elif resList[2] == 2:
                        mature[el][resName]['both elongated']+=samFileValue
                        whichField='both elongated'
                    else:
                        if temp1[1] == 1:
                            mature[el][resName]["5' elongated"]+=samFileValue
                            whichField="5' elongated"
                        elif temp1[2] == 1:
                            mature[el][resName]["5' truncated"]+=samFileValue
                            whichField="5' truncated"
#                         else:
#                             mature[el][resName]['rightEqual']+=1
                        
                        if temp2[1] == 1:
                            mature[el][resName]["3' elongated"]+=samFileValue
                            whichField="3' elongated"
                        elif temp2[2] == 1:
                            mature[el][resName]["3' truncated"]+=samFileValue
                            whichField="3' truncated"
#                         else:
#                             mature[el][resName]['leftEqual']+=1
                    if listLetterToStatistic:
                        for key in listLetterToStatistic[0].keys():
                            if key >=matSt and key <=matEnd:
                                if not listLetterToStatistic[0][key] in mature[el][resName +'Letter'][whichField]:
                                    mature[el][resName +'Letter'][whichField].append(listLetterToStatistic[0][key])
                            else:
                                if not listLetterToStatistic[0][key] in mature[el][resName +'LetterNot'][whichField]:
                                    mature[el][resName +'LetterNot'][whichField].append(listLetterToStatistic[0][key])
        
        

        return mature
    
    def calcValues(self, precursor, samFiles):
        
        precursorList=[]
        
        
        for samFile in range(0, len(samFiles)):
            precursorMod = {}
            precursorMod['totalVal'] = samFiles[samFile]['totalVal']
            precursorMod['fileName'] = samFiles[samFile]['fileName']  
            
         
            precursorMod['values'] = []
            for pr in precursor:
              
                if pr[0] in samFiles[samFile]['values'].keys():
    
                    maxPr2 = max(pr[2].keys())
                    newPr2 = {}
                    for chNum in range(0, maxPr2):
                        newPr2[chNum]=0
                    
                    maxPr3 = max(pr[3].keys())
                    newPr3 = {}
                    for chNum in range(0, maxPr3):
                        newPr3[chNum]=0
                        
                    maxPr5 = max(pr[5].keys())
                    newPr5 = {}
                    for chNum in range(0, maxPr5):
                        newPr5[chNum]=0
                    
                    
                    for elNum in range(0,len(samFiles[samFile]['values'][pr[0]])):
                        
                        if samFiles[samFile]['values'][pr[0]][elNum][3] == 0:
                            ##check if the position is all right
                            for numPS in range(samFiles[samFile]['values'][pr[0]][elNum][1]-1, samFiles[samFile]['values'][pr[0]][elNum][1]-1+samFiles[samFile]['values'][pr[0]][elNum][2]):
                                newPr2[numPS] += samFiles[samFile]['values'][pr[0]][elNum][0]
                        else:
                            for numPS in samFiles[samFile]['values'][pr[0]][elNum][1]:
                                newPr3[numPS] += samFiles[samFile]['values'][pr[0]][elNum][0]
                                
                        if samFiles[samFile]['values'][pr[0]][elNum][3] == 1 and len(samFiles[samFile]['values'][pr[0]][elNum][4]) != 0:
                            for el in samFiles[samFile]['values'][pr[0]][elNum][4]:
                                newPr5[el] += samFiles[samFile]['values'][pr[0]][elNum][0]
            
                    precursorMod['values'].append([pr[0], pr[1], newPr2, newPr3, newPr5])
        
            precursorList.append(precursorMod)
       
        
        
        with open('results/tempData/precursor.pkl','wb') as fp:
            pickle.dump(precursorList,fp)
        
        print 'done calcValues'
        #return precursorList
    
    
    def visualizateTable(self,writeFile, newFileList):
        
        writeFile.write("""
        <style>
        table {
            display: table;
            width: 100%; 
            background: #fff;
            margin: 0;
            box-sizing: border-box;
        }
        .th {
            background-color: #31BC86;
            font-weight: bold;
            color: #FFF;
            white-space: nowrap;
            
        }
        th, td {
            padding: 0.50em 1.0em;
            text-align: left;
            border:  1px dotted #010101;
        }
        
        table#tabReads{
        border-collapse: collapse;
        }
        
        table#tabReads td{
        padding:0;
        padding-left:0.15em;
        border:0px;
        
        }
        
        
        select{
        -webkit-appearance: none;
        -moz-appearance: none;
        appearance: none;
        padding: 0.2em 1.5em;
        }
        
        .statistic{
        border:  1px dotted #198b19;
        clear: both;
        display: block;
        margin: 10px 0px;
        overflow: hidden;
        }
        .statisticTitle{
        text-transform: uppercase;
        background-color:#198b19;
        border-bottom:  1px dotted #198b19;
        padding:10px 0px;
        text-align:center;
        color:#FFF;
        }
        .statisticTitleDesc{
        text-align:left;
        margin-left:10px;
        font-size:16px;
        float:left;
        text-transform:lowercase;
        }
        </style>
        """)
       
        
        
        writeFile.write('<table >')
        writeFile.write('<tr>')
        
        writeFile.write('<th>')
        writeFile.write('Option')
        writeFile.write('</th>')
        writeFile.write('<th>')
        writeFile.write('Files')
        writeFile.write('</th>')
        writeFile.write('<th>')
        writeFile.write('Statistics')
        writeFile.write('</th>')
        
        for filename in newFileList:
            writeFile.write('<tr>')
            writeFile.write('<td>')
            writeFile.write('<input type="checkbox"  checked="checked" name="fileList" id ="' + str(filename)  + '" value="' + str(filename) + '" ' + ' onclick="showMe(' +"'container_" + str(filename) + "'" + ')"'   + '\>')
            writeFile.write('</td>')
            writeFile.write('<td>')
            writeFile.write(filename)
            writeFile.write('</td>')
            writeFile.write('<td>')
            writeFile.write('<input type="checkbox"  checked="checked" name="fileListPieChart" id ="' + str(filename)  + '" value="' + str(filename) + '" ' + ' onclick="showMePieChart(' +"'containerPieChart_" + str(filename) + "'" + ')"'   + '\>')
            writeFile.write('</td>')
            writeFile.write('</tr>')
        
        writeFile.write('</tr>')
        writeFile.write('</table>')
        
         
        writeFile.write('''
        <div style="padding: 0.50em 0em;">
        <div style="border-bottom:1px dotted green;padding: 0.50em 0em 0.2em 0.2em; width:20%">
        Mismatches:
        <input type="checkbox" id="selectMismatcheslist" name="selectMismatcheslist" type="" onClick="showMeOptionListChb('')"\>
        
         <!-- <select id="selectMismatcheslist" onChange="showMeOptionList('')">
          <option value=0>No</option>
          <option value=1>Yes</option>
        </select> --> 
        </div>
        
        
        <div style="border-bottom:1px dotted green;padding: 0.50em 0em 0.2em 0.2em; width:20%">
        Show reads <input type="checkbox" id="showReads"  name="showReads" onClick="showReads()" value="0" \>
        </div>
        <div style="border-bottom:1px dotted green;padding: 0.50em 0em 0.2em 0.2em; width:20%">
        Statistic:
        <input type="checkbox" id="selectStatisticList" name="selectStatisticlist" type="" onClick="showMeOptionListStat('')"\>
        
        
        
        </div>
        </div>
        ''')
            
        return writeFile
    
    def visualizateTableWithout(self,writeFile, newFileList):
        
        writeFile.write("""
        <style>
        table {
            display: table;
            width: 100%; 
            background: #fff;
            margin: 0;
            box-sizing: border-box;
        }
        .th {
            background-color: #31BC86;
            font-weight: bold;
            color: #FFF;
            white-space: nowrap;
            
        }
        th, td {
            padding: 0.50em 1.0em;
            text-align: left;
            border:  1px dotted #010101;
        }
        
        table#tabReads{
        border-collapse: collapse;
        }
        
        table#tabReads td{
        padding:0;
        padding-left:0.15em;
        border:0px;
        
        }
        
        
        select{
        -webkit-appearance: none;
        -moz-appearance: none;
        appearance: none;
        padding: 0.2em 1.5em;
        }
        
        .statistic{
        border:  1px dotted #198b19;
        clear: both;
        display: block;
        margin: 10px 0px;
        overflow: hidden;
        }
        .statisticTitle{
        text-transform: uppercase;
        background-color:#198b19;
        border-bottom:  1px dotted #198b19;
        padding:10px 0px;
        text-align:center;
        color:#FFF;
        }
        .statisticTitleDesc{
        text-align:left;
        margin-left:10px;
        font-size:16px;
        float:left;
        text-transform:lowercase;
        }
        </style>
        """)
       
        
        
         
        writeFile.write('''
        <div style="padding: 0.50em 0em;">
        <div style="border-bottom:1px dotted green;padding: 0.50em 0em 0.2em 0.2em; width:20%">
        Mismatches:
        <input type="checkbox" id="selectMismatcheslist" name="selectMismatcheslist" type="" onClick="showMeOptionListChb('')"\>
        
         <!-- <select id="selectMismatcheslist" onChange="showMeOptionList('')">
          <option value=0>No</option>
          <option value=1>Yes</option>
        </select> --> 
        </div>
        
        
        <div style="border-bottom:1px dotted green;padding: 0.50em 0em 0.2em 0.2em; width:20%">
        Show reads <input type="checkbox" id="showReads"  name="showReads" onClick="showReads()" value="0" \>
        </div>
        <div style="border-bottom:1px dotted green;padding: 0.50em 0em 0.2em 0.2em; width:20%">
        Statistic:
        <input type="checkbox" id="selectStatisticList" name="selectStatisticlist" type="" onClick="showMeOptionListStat('')"\>
        
        
        
        </div>
        </div>
        ''')
            
        return writeFile
    
    
    def visualizateTableForTable(self, writeFile, newFileList, howMany=0):
        
        writeFile.write("""
        <style>
        .tabSel {
            display: table;
            width: 100%; 
            background: #fff;
            margin: 0;
            box-sizing: border-box;
        }
        .tabSel.th {
            background-color: #31BC86;
            font-weight: bold;
            color: #FFF;
            white-space: nowrap;
            
        }
        .tabSel th, .tabSel td {
            padding: 0.50em 1.0em;
            text-align: left;
            border:  1px dotted #010101;
        }
        select{
        -webkit-appearance: none;
        -moz-appearance: none;
        appearance: none;
        padding: 0.2em 1.5em;
        }
        
        .statistic{
        border:  1px dotted #198b19;
        clear: both;
        display: block;
        margin: 10px 0px;
        overflow: hidden;
        }
        .statisticTitle{
        text-transform: uppercase;
        background-color:#198b19;
        border-bottom:  1px dotted #198b19;
        padding:10px 0px;
        text-align:center;
        color:#FFF;
        }
        .statisticTitleDesc{
        text-align:left;
        margin-left:10px;
        font-size:16px;
        float:left;
        text-transform:lowercase;
        }
        </style>
        """)
       
       #how many precursors!
        
        writeFile.write('Show more data <input type="checkbox" id="data" name="data" value="Show Overall Data" onclick="check(' + str(howMany) + ')"/>')
        writeFile.write('<table class="tabSel">')
        writeFile.write('<tr>')
        
        writeFile.write('<th>')
        writeFile.write('Files')
        writeFile.write('</th>')
        writeFile.write('<th>')
        writeFile.write('Option')
        writeFile.write('</th>')
        
        
        for filename in newFileList:
            writeFile.write('<tr>')
            writeFile.write('<td>')
            writeFile.write(filename)
            writeFile.write('</td>')
            writeFile.write('<td>')
            writeFile.write('<input type="checkbox"  checked="checked" name="fileList" id ="' + str(filename)  + '" value="' + str(filename) + '" ' + ' onclick="showMe(' +"'table_" + str(filename) + "'" + ')"'   + '\>')
            writeFile.write('</td>')
            writeFile.write('</tr>')
        
        writeFile.write('</tr>')
        writeFile.write('</table>')
        
            
        return writeFile
    
    def visualizateTableGlobal(self, writeFile, newFileList):
        
        writeFile.write("""
        <style>
        table {
            display: table;
            width: 100%; 
            background: #fff;
            margin: 0;
            box-sizing: border-box;
        }
        .th {
            background-color: #31BC86;
            font-weight: bold;
            color: #FFF;
            white-space: nowrap;
            
        }
        th, td {
            padding: 0.50em 1.0em;
            text-align: left;
            border:  1px dotted #010101;
        }
        select{
        -webkit-appearance: none;
        -moz-appearance: none;
        appearance: none;
        padding: 0.2em 1.5em;
        }
        
        .statistic{
        border:  1px dotted #198b19;
        clear: both;
        display: block;
        margin: 10px 0px;
        overflow: hidden;
        }
        .statisticTitle{
        text-transform: uppercase;
        background-color:#198b19;
        border-bottom:  1px dotted #198b19;
        padding:10px 0px;
        text-align:center;
        color:#FFF;
        }
        .statisticTitleDesc{
        text-align:left;
        margin-left:10px;
        font-size:16px;
        float:left;
        text-transform:lowercase;
        }
        </style>
        """)
       
        
        
        writeFile.write('<table >')
        writeFile.write('<tr>')
        
        writeFile.write('<th>')
        writeFile.write('Files')
        writeFile.write('</th>')
        writeFile.write('<th>')
        writeFile.write('Statistics')
        writeFile.write('</th>')
        
        for filename in newFileList:
            writeFile.write('<tr>')
            writeFile.write('<td>')
            writeFile.write(filename)
            writeFile.write('</td>')
            writeFile.write('<td>')
            writeFile.write('<input type="checkbox"  checked="checked" name="fileListPieChart" id ="' + str(filename)  + '" value="' + str(filename) + '" ' + ' onclick="showMePieChart(' +"'containerPieChart_" + str(filename) + "'" + ')"'   + '\>')
            writeFile.write('</td>')
            writeFile.write('</tr>')
        
        writeFile.write('</tr>')
        writeFile.write('</table>')
        
        return writeFile
    
    
    def visualizateTableHistogram(self, writeFile, newFileList):
        
        writeFile.write("""
        <style>
        table {
            display: table;
            width: 100%; 
            background: #fff;
            margin: 0;
            box-sizing: border-box;
        }
        .th {
            background-color: #31BC86;
            font-weight: bold;
            color: #FFF;
            white-space: nowrap;
            
        }
        th, td {
            padding: 0.50em 1.0em;
            text-align: left;
            border:  1px dotted #010101;
        }
        select{
        -webkit-appearance: none;
        -moz-appearance: none;
        appearance: none;
        padding: 0.2em 1.5em;
        }
        
        .statistic{
        border:  1px dotted #198b19;
        clear: both;
        display: block;
        margin: 10px 0px;
        overflow: hidden;
        }
        .statisticTitle{
        text-transform: uppercase;
        background-color:#198b19;
        border-bottom:  1px dotted #198b19;
        padding:10px 0px;
        text-align:center;
        color:#FFF;
        }
        .statisticTitleDesc{
        text-align:left;
        margin-left:10px;
        font-size:16px;
        float:left;
        text-transform:lowercase;
        }
        
        .statDescColor1{
        color:orange;
        font-weight:bold;
        }
        .statDescColor2{
        color:green;
        font-weight:bold;
        }
        
        .but{
        padding:10px;
        }
        
        
        
        input[type=button] {
        color:#08233e;
        font-size:14px;    
        border-bottom:  1px dotted #198b19;
        padding:10px 5px;
        cursor:pointer;
        margin: 5px;
        }

            input[type=button]:hover {
                color:#4c4cff;
            }
        </style>
        """)
       
        
    
    def visualizateTableLegend(self, writeFile, seriesNameMature):
        
        writeFile.write("""
        <style>
        table {
            display: table;
            width: 100%; 
            background: #fff;
            margin: 0;
            box-sizing: border-box;
        }
        .th {
            background-color: #31BC86;
            font-weight: bold;
            color: #FFF;
            white-space: nowrap;
            
        }
        th, td {
            padding: 0.50em 1.0em;
            text-align: left;
            border:  1px dotted #010101;
        }
        select{
        -webkit-appearance: none;
        -moz-appearance: none;
        appearance: none;
        padding: 0.2em 1.5em;
        }
        
        .statistic{
        border:  1px dotted #198b19;
        clear: both;
        display: block;
        margin: 10px 0px;
        overflow: hidden;
        }
        .statisticTitle{
        text-transform: uppercase;
        background-color:#198b19;
        border-bottom:  1px dotted #198b19;
        padding:10px 0px;
        text-align:center;
        color:#FFF;
        }
        .statisticTitleDesc{
        text-align:left;
        margin-left:10px;
        font-size:16px;
        float:left;
        width:500px;
        text-transform:lowercase;
        }
        .statDescColor1{
        color:orange;
        font-weight:bold;
        }
        .statDescColor2{
        color:green;
        font-weight:bold;
        }
        
        .button0 {
        }
           
      .button1 {
        }
           
      .button2 {
        }
           
      .button3 {
        }
           
      .button4 {
        }
           
      .button5 {
        }
           
      .button6 {
        }
           
      .button7 {
        }
           
      .button8 {
        }
           
      .button9 {
        }
           
      .button10 {
        }
           
      .button11 {
        }
           
      .button12 {
        }
           
      .button13 {
        }
        #legendTable{
        display:none;
        }
        #legendTable a{
        text-decoration: none;
        }
    
        
      
        
        
        </style>
        """)
       
        
        tableArr = ['#7cb5ec', '#434348', '#99D6D6', '#90ed7d', '#f7a35c',  '#005C5C', '#292933', '#336699','#8085e9', '#B2CCFF', '#f15c80',  '#e4d354',  '#8085e8',  '#8d4653',  '#6699FF','#91e8e1','#7A991F','#525266','#1A334C']
        
        writeFile.write('<div id="legendTable" >')
        writeFile.write('<table >')
        writeFile.write('<tr>')
        writeFile.write('<td style="background-color:#4b4b4b" colspan="7">')
        writeFile.write('<p style="text-align:center; color:#FCFCFC; font-size:21px; text-transform: uppercase;  font-weight:bold;"> Legend </p>')
        writeFile.write('</td>')
        writeFile.write('</tr>')
        i=0
        for sNM in range(0, len(seriesNameMature)):
            if i%7 == 0:
                writeFile.write('<tr>')
            writeFile.write('<td style="background-color:' + str(tableArr[sNM]) + '">')
            writeFile.write('<p style="cursor:pointer" class="button'+str(sNM)+'" id="' + str(sNM) + '">' + seriesNameMature[sNM] + '</p>')
            writeFile.write('</td>')
            i+=1
            if i%7 ==0 :
                writeFile.write('</tr>')
            
        
        writeFile.write('</table>')
        writeFile.write('</div>')
        
        return writeFile
    
    def getColorList(self, newFileList):
        
        print 'start get Colors'
        colors = [    '#7cb5ec',
                      '#434348',
                      '#99D6D6',
                      '#90ed7d',
                      '#f7a35c',
                      '#005C5C',
                      '#292933',
                      '#336699',
                      '#8085e9',
                      '#B2CCFF',
                      '#f15c80',
                      '#e4d354',
                      '#8085e8',
                      '#8d4653',
                      '#6699FF',
                      '#91e8e1',
                      '#7A991F',
                      '#525266',
                      '#1A334C',
                      '#334C80',
                      '#292900',
                      '#142900',
                      '#99993D',
                      '#009999',
                      '#1A1A0A',
                      '#5C85AD',
                      '#804C4C',
                      '#1A0F0F',
                      '#A3A3CC',
                      '#660033',
                      '#3D4C0F',
                      '#fde720',
                      '#554e44',
                      '#1ce1ce',
                      '#dedbbb',
                      '#facade',
                      '#baff1e',
                      '#aba5ed',
                      '#f2b3b3',
                      '#f9e0e0',
                      '#abcdef',
                      '#f9dcd3',
                      '#eb9180',
                      '#c2dde5'
                      ];
        
        colorDictRes={}
        i=0
        for el in newFileList:
            colorDictRes[str(el)] = colors[i]
            colorDictRes[str(el)+ str(' - mismatch')] = '#ff3232'
            colorDictRes[str(el)+ str(' - match&mismatch')] = colors[i]
            i+=1
        
        print 'get Colors'
        return colorDictRes
        
        
    
    def checkColor(self, seriesName, colorDictRes):
        
        
        checkColorList=[]
        for sN in seriesName:
            checkColorList.append(colorDictRes[sN])
        
        
        return checkColorList
        
        
    
    def visualizateResults(self, outputResults, precursor, letterDict, combinationsFileList, newFileList, mature, precursorDict, colorDictRes, readsDict):
        
        heatmapResultsV3={}
        plotList={}
        sampleRes={}
        for psNum in range(0, len(precursor)):
            for psNumPart in range(0, len(precursor[psNum]['values'])):
                
                if not precursor[psNum]['values'][psNumPart][0] in plotList.keys():
                    plotList[precursor[psNum]['values'][psNumPart][0]]={}
                
                if not precursor[psNum]['fileName'] in plotList[precursor[psNum]['values'][psNumPart][0]].keys():
                    plotList[precursor[psNum]['values'][psNumPart][0]][precursor[psNum]['fileName']]={}
                
                #tatlVal different for all out, blood
                numMil = 1000000
                if precursor[psNum]['totalVal']!=0:
                    dataY=[]#without mismatches
                    
                    for x in precursor[psNum]['values'][psNumPart][2].values():
                        val = round(float(x)/(float(precursor[psNum]['totalVal'])/float(numMil)),2)
                        dataY.append(val)
                    
                    
                    dataM=[]#some mismatches
                    for x in precursor[psNum]['values'][psNumPart][3].values():
                        val=round(float(x)/(float(precursor[psNum]['totalVal'])/float(numMil)),2)
                        dataM.append(val)
                    
                    
                    
                    dataMatchMismatch=[]#matches from mismatches    
                    for x in precursor[psNum]['values'][psNumPart][4].values():
                        val=round(float(x)/(float(precursor[psNum]['totalVal'])/float(numMil)),2)
                        dataMatchMismatch.append(val)
                    
                    
                for i in letterDict[precursor[psNum]['fileName']][precursor[psNum]['values'][psNumPart][0]].keys():
                    for key, value in letterDict[precursor[psNum]['fileName']][precursor[psNum]['values'][psNumPart][0]][i][0].items():
                        val = round(float(value/(float(precursor[psNum]['totalVal'])/float(numMil))), 2)
                        letterDict[precursor[psNum]['fileName']][precursor[psNum]['values'][psNumPart][0]][i][0][key]=val
                
                
                categories = list(precursor[psNum]['values'][psNumPart][1])
                
                plotPartList={}
                plotPartList['dataY'] = dataY
                plotPartList['dataM'] = dataM
                plotPartList['dataMatchMismatch'] = dataMatchMismatch
                plotPartList['seriesName'] = precursor[psNum]['fileName']
                plotPartList['categories'] = categories
                
               
                    
                plotList[precursor[psNum]['values'][psNumPart][0]][precursor[psNum]['fileName']] = plotPartList
#                 with open(filename,'wb') as fp:
#                     pickle.dump(dict1,fp)
        
        print 'done visualizateResults'
        
        for pr in plotList.keys():
            sampleRes, heatmapResultsV3 = self.doSeries(plotList[pr], pr,  combinationsFileList, newFileList, mature, letterDict, outputResults, precursorDict, colorDictRes, readsDict, sampleRes, heatmapResultsV3)
        
        
        with open('results/tempData/sampleRes.pkl','wb') as fp:
            pickle.dump(sampleRes, fp) 
        
        return plotList, heatmapResultsV3
#         return sampleRes
    
    
    def doSeries(self, plotList, pr, combinationsFileList, newFileList, mature, letterDict, outputResults, precursorDict, colorDictRes, readsDict, sampleRes, heatmapResultsV3):
      
        
        
        plotListRes={}
        
        #for plotKey in plotList.keys(): 
        plotListRes['plotKey'] = {}
            
        #for every element
        
        for combEl in combinationsFileList:
           
            
            combElLine =  '/'.join(combEl)
            
            if '/'.join(combEl) not in plotListRes.keys():
                plotListRes['/'.join(combEl)] = {}       
            
            dataMY = []
            
            seriesName=[]
            seriesNameM=[]
            
            
            if len(combEl)==1:
                
                dataY=[]
                if '/'.join(combEl) in plotList.keys():
                    
                    dataY = plotList['/'.join(combEl)]['dataY']
                    dataMY.append(dataY)
                    dataMY.append(plotList['/'.join(combEl)]['dataM'])
                    dataMY.append(plotList['/'.join(combEl)]['dataMatchMismatch'])
                    
                    categories = plotList['/'.join(combEl)]['categories']
                
                    seriesNameM = ['/'.join(combEl), '/'.join(combEl) + str(' - mismatch'), '/'.join(combEl) + str(' - match&mismatch')]
                    seriesName = ['/'.join(combEl)]
                
                        
            else:
                #for every possible combinations
                
                categories=[]
                dataMY=[]
                seriesName=[]
                seriesNameM=[]
                dataY=[]
                for newCombEl in combEl:
                    
                    
                    newCombElJoin = ''.join(newCombEl)
                    
                    if len(newCombEl)!=0 and newCombElJoin in plotList.keys():
                        
                        dY=plotList[newCombElJoin]['dataY']
                        dataY.append(dY)
                        dataMY.append(dY)
                        dataMY.append(plotList[newCombElJoin]['dataM'])
                        dataMY.append(plotList[newCombElJoin]['dataMatchMismatch'])
                        
                        categories = plotList[newCombElJoin]['categories']
                    
                        seriesNameM.append(newCombElJoin)
                        seriesNameM.append( newCombElJoin + str(' - mismatch'))
                        seriesNameM.append( newCombElJoin + str(' - match&mismatch'))
                        
                        seriesName.append(newCombElJoin)
            
            plotListRes[combElLine]['containerName'] = combElLine
            plotListRes[combElLine]['seriesName'] = seriesName
            plotListRes[combElLine]['seriesNameM'] = seriesNameM
            
            if len(dataY) !=0 or len(dataMY) !=0 :
                plotListRes[combElLine]['dataY'] = dataY
                plotListRes[combElLine]['dataM'] = dataMY
                plotListRes[combElLine]['categories'] = categories
            else:
                plotListRes[combElLine]['dataY'] = [0]
                plotListRes[combElLine]['dataM'] = [0]
                plotListRes[combElLine]['categories'] = [0]
        
        
        
        plotKey=pr
       
        
        sampleRes, heatmapResultsV3 = self.doPlot(combinationsFileList, plotListRes, plotKey, newFileList, mature, letterDict, outputResults, precursorDict[plotKey], colorDictRes, sampleRes, readsDict[plotKey], heatmapResultsV3)
        
        
        plotListRes={}
        
        
        
        print 'done doSeries'
        return sampleRes, heatmapResultsV3
    
    def addScriptExtraOld(self, elPl):
        return """
        
           $('#""" + str(elPl)+  """').click(function () {
             
             
             var e = document.getElementById("selectMismatcheslist");
            var selVal = e.options[e.selectedIndex].value;
            
                var chboxs = document.getElementsByName("fileList");
                newBox= ''
                var vis = "none";
                var j=0;
                for(var i=0;i<chboxs.length;i++) { 
                    if(chboxs[i].checked)
                    {
                    if(j==0)
                    {
                     newBox = newBox.concat('container_', chboxs[i].value);
                    }
                    else
                    {
                    newBox = newBox.concat('/', chboxs[i].value);
                    }
                    
                    j++;
                     vis = "block";
                        
                    }
                }
                
                name=''
                name = name.concat('#container_',selVal);
                var chart = $(name).highcharts();
                
                //console.log(newBox, typeof seriesD[newBox.concat('-', selVal)], newBox.concat('-', selVal) );
                
                if( typeof seriesD[newBox.concat('-', selVal)] == 'number')
                {
                     $(chart.series).each(function(){
                        this.setVisible(false, false);
                    });
                    number=seriesD[newBox.concat('-', selVal)]
                    chart.series[number].show();
                }
                else
                {
                    $(chart.series).each(function(){
                        this.setVisible(false, false);
                    });
                    for(i=0; i < seriesD[newBox.concat('-', selVal)].length; i++)
                    {
                        number = seriesD[newBox.concat('-', selVal)][i];
                        chart.series[number].show();
                    }
                }
                chart.redraw();
    });
             
        
        """
    def addScriptExtra(self, elPl):
        return """
        
           $('#""" + str(elPl)+  """').click(function () {
             
             
            var e = document.getElementById("selectMismatcheslist");
            var selVal = e.options[e.selectedIndex].value;
            
            var chboxs = document.getElementsByName("fileList");
            newBox= ''
            var j=0;
            
             name=''
            name = name.concat('#container_',selVal);
            var chart = $(name).highcharts();
            
       
            $(chart.series).each(function(){
                this.setVisible(false, false);
            });
            
           
            if(selVal == 0)
            {
                for(var i=0;i<chboxs.length;i++) 
                { 
                    if(chboxs[i].checked)
                    {
                     chart.series[myMap0[chboxs[i].value]].show();   
                    }
                }
            }
            else
            {
                for(var i=0;i<chboxs.length;i++) 
                { 
                    if(chboxs[i].checked)
                    {
                     chart.series[myMap1[chboxs[i].value]].show(); 
                     chart.series[myMap1[chboxs[i].value + " - mismatch"]].show(); 
                     chart.series[myMap1[chboxs[i].value + " - match&mismatch"]].show(); 
                    }
                }
            }
            chart.redraw();
    });
             
        
        """
    
    def calcPlotband(self, name, data):
        
        xAxis = """ if (result['""" + str(name) + """'] ==  1 ) { """
        
        i=0
        start=-1
        for numdY in range(0, len(data)):
            if data[numdY] > 0:
                if i==0:
                    start = numdY - 0.25                  
                i+=1
            else:
                if start!=-1:
                    end = numdY-0.75
                    i=0
                    xAxis += """
                      this.chart.xAxis[0].addPlotBand({
                        from: """ + str(start)  + """,
                        to: """ + str(end)  + """,
                        color: '#fff',
                        id: '""" + str(name)  + """',
                    });
                    """
                    start=-1
        xAxis += '}'
        return xAxis
    
    def addReads(self, readsDict, precursorDict, colorBoth):
    
        
        tab=''
        for key1 in readsDict:
            
            tab+='<div style="display:none;" id = tabReads_' + str(key1) + ' >'
            tab +='<table class="sortable" id = "tabReads" >'
            tab +='<tr style="border-bottom:1px solid green;">'
            for el in range(0, len(precursorDict)):
                tab +='<td>+</td>'
            tab +='<td></td>'
            tab+='<td style="width:80px;padding-right:10px;padding-left:10px;border-left:1px solid green;">Value</td>'
            tab+='<td style="padding-right:10px;padding-left:10px;border-left:1px solid green;">RPM</td>'
            tab +='</tr>'
            if len(readsDict[key1]['values'])>0:
                i=0
                
                
                
                lElRN = []
                for elRN in range(0, len(readsDict[key1]['values'])):
                    countN=0
                    for emptyN in range(0, len(readsDict[key1]['values'][elRN])):
                        if readsDict[key1]['values'][elRN][emptyN] == '':
                            countN+=1
                        else:
                            strNN=''
                            for emptyNN in range(emptyN, len(readsDict[key1]['values'][elRN])):
                                if readsDict[key1]['values'][elRN][emptyNN] != '':
                                    strNN+=readsDict[key1]['values'][elRN][emptyNN]
                            break
                    lElRN.append([elRN, countN, strNN])
                #print lElRN
                
                sort_lElRN = sorted(lElRN, key=operator.itemgetter(1, 2), reverse=False)
                theSameValsort_lElRN={}
                
                
                if len(sort_lElRN) > 1:
                    elRR=sort_lElRN[0]
                    for elRN in range(1, len(sort_lElRN)):
                        if sort_lElRN[elRN][2] == elRR[2]:
                            if not elRR[0] in theSameValsort_lElRN:
                                theSameValsort_lElRN[elRR[0]] = []
                            theSameValsort_lElRN[elRR[0]].append(sort_lElRN[elRN][0])
                            sort_lElRN[elRN] = []
                        else:
                            elRR=sort_lElRN[elRN]
                indexList =[]
                
                for el in sort_lElRN:
                    if len(el)>1:
                        indexList.append(el[0])
                        
                
#                 t = [el for el in range(0, min(map(len, readsDict[key1]['values'])))]
#                 print t
#                 sorted_list = sorted(readsDict[key1]['values'], key=operator.itemgetter(*t), reverse=True)
#                 print sorted_list
#                 
#                 indexList=[]
#                 for el1 in sorted_list:
#                     inx=0
#                     for el2 in readsDict[key1]['values']:
#                         if el1 == el2:
#                             if inx not in indexList:
#                                 indexList.append(inx)
#                         inx+=1
                
                    
                
                
                for rd in indexList:
                    tab+='<tr>'
                    
                    
                    for r in range(1, len(readsDict[key1]['values'][rd])):
                        addStyle=''
                        if 'red' in colorBoth:
                            if r-1 in colorBoth['red']:
                                addStyle+= "background-color:#ffe5e5;"
                        if 'blue' in colorBoth:
                            if r-1 in colorBoth['blue']:
                                addStyle+= "background-color:#cce6ff;"
                        if readsDict[key1]['values'][rd][r]=='':
                            tab+='<td style ="' + addStyle + '">' + '-' + '</td>'
                        else:
                            if key1 == 1 and readsDict[key1]['values'][rd][r]!=precursorDict[r-1]:
                                addStyle='background-color:#F00;color:#f0f0f0;'
                            tab+='<td style ="' + addStyle + '">' + str(readsDict[key1]['values'][rd][r]) + '</td>'
                            
                    
                    for el in range(r, len(precursorDict)):
                        addStyle=''
                        if 'red' in colorBoth:
                            if el in colorBoth['red']:
                                addStyle+= "background-color:#ffe5e5;"
                        if 'blue' in colorBoth:
                            if el in colorBoth['blue']:
                                addStyle+= "background-color:#cce6ff;"
                        tab+='<td style ="' + addStyle + '">' + '-' + '</td>'
                    
                    tab +='<td></td>'
                    
                    totValNew = readsDict[key1]['totalVal'][rd-1]
                    totalValRPMnew = float(readsDict[key1]['totalVal'][rd])/float(readsDict[key1]['rpm'][rd])
                    
                    if rd in theSameValsort_lElRN.keys():
                        for elNTSV in theSameValsort_lElRN[rd]:
                            totValNew += readsDict[key1]['totalVal'][elNTSV-1]
                            totalValRPMnew += float(readsDict[key1]['totalVal'][elNTSV-1])/float(readsDict[key1]['rpm'][elNTSV-1])
                              
                    
                    tab+='<td style="width:80px;padding-right:10px;padding-left:10px;border-left:1px solid green;">' + str(totValNew) + '</td>'
                    tab+='<td style="padding-right:10px;padding-left:10px;border-left:1px solid green;">'  + str(round(totalValRPMnew, 2))   + '</td>'
                    
                    
                    tab+='</tr>'
                    i+=1
            tab+='<tr>'
            for el in range(0, len(precursorDict)):
                addStyle=''
                if 'red' in colorBoth:
                    if el in colorBoth['red']:
                        addStyle+= "background-color:#ffe5e5;"
                if 'blue' in colorBoth:
                    if el in colorBoth['blue']:
                        addStyle+= "background-color:#cce6ff;"
                tab+='<td style ="' + addStyle + '">' + str(precursorDict[el])  + '</td>'
            tab +='<td></td>'
            tab+='<td style="width:80px;padding-right:10px;padding-left:10px;border-left:1px solid green;"></td>'
            tab+='<td style="padding-right:10px;padding-left:10px;border-left:1px solid green;"></td>'
            tab+='<tr>' 
            tab+='</table>'
            tab+='</div>'
                
        return tab
    
    
    
    def doPlot(self, combinationsFileList, plotLRes, pL, newFileList, mature, letterDict, outputResults, precursorDict, colorDictRes, sampleRes, readsDict, heatmapResultsV3 ):
        
        
        printData=''
#         writeFile = open(outputResults + '/' + str(pL)  + '.html', 'w')
#         writeFile.write('<HTML><HEAD>')
#         writeFile.write(""" 
#          <script src="http://www.kryogenix.org/code/browser/sorttable/sorttable.js" type="text/javascript"></script> 
#         """)
#         
#         
#         writeFile.write('<link href="https://fonts.googleapis.com/css?family=Roboto+Condensed:300" rel="stylesheet" type="text/css"></HEAD><BODY onLoad="loadPage()" style="font-family: Roboto Condensed;font-size:1.5em"><div id ="plot">')
        hist = vis()
        
        script = '' 
        dictName ={}
        dictNameM ={}
        countHow=0
        countHow2=0
        
        for nF in newFileList:
            script += self.addScriptExtra(nF)
            
        m=-1000
        elM=''
        for k in plotLRes.keys():
            if len(k) > m:
                m=len(k)
                elM = k
        
        
        elPl = elM
        
        for name in plotLRes[elPl]['seriesName']:
            dictName[name] = countHow
            countHow+=1
        for name in plotLRes[elPl]['seriesNameM']:
            dictNameM[name] = countHow2
            countHow2+=1
        
        
#         writeFile.write('<script>' + 'var myMap0 = ' + str(dictName) + '; </script>\n')
#         writeFile.write('<script>' + 'var myMap1 = ' + str(dictNameM) + '; </script>\n')  
#         
#         
#         
#         writeFile.write(hist.addLoadPage())
#         writeFile.write(hist._addLib())
#         writeFile.write(hist._addStyle())
#         writeFile.write(hist.addShowHide())

        
        countHow = 0
        titleText=[]
        
        colorBoth={}
        for elPl in plotLRes:
            
            if countHow == 0:
                for k in plotLRes.keys():
                    if k in mature.keys():
                        blueTF = False
                        
                        if 'star' in mature[k][pL].keys():
#                             writeFile.write('<script> var blue = ' + str(mature[k][pL]['star']['values']) + '; </script>\n')
                            printData += '<script> var blue = ' + str(mature[k][pL]['star']['values']) + '; </script>\n'
                            colorBoth['blue'] = mature[k][pL]['star']['values']
                            blueTF = True
                            titleText.append('star')
                        if blueTF == False:
#                             writeFile.write('<script>var blue=[]; </script>\n')
                            printData += '<script>var blue=[]; </script>\n'
                        
                        #combain mature and co-mature
                        refTF = False
                        if 'mature' in mature[k][pL].keys() or 'co-mature' in mature[k][pL].keys():
                            if blueTF == False:
#                                 writeFile.write('<script> var red = ' + str(mature[k][pL]['mature']['values']+mature[k][pL]['co-mature']['values']) + '; </script>\n')
                                printData += '<script> var red = ' + str(mature[k][pL]['mature']['values']+mature[k][pL]['co-mature']['values']) + '; </script>\n'
                                colorBoth['red'] = mature[k][pL]['mature']['values']+mature[k][pL]['co-mature']['values']
                                
                            else:
                                if 'mature' in mature[k][pL].keys():
#                                     writeFile.write('<script> var red = ' + str(mature[k][pL]['mature']['values']) + '; </script>\n')
                                    printData += '<script> var red = ' + str(mature[k][pL]['mature']['values']) + '; </script>\n'
                                    if 'red' not in colorBoth:
                                        colorBoth['red'] = mature[k][pL]['mature']['values']
                                    else:
                                        colorBoth['red'] += mature[k][pL]['mature']['values']
                                    
                                if 'co-mature' in mature[k][pL].keys():
#                                     writeFile.write('<script> var red = ' + str(mature[k][pL]['co-mature']['values']) + '; </script>\n')
                                    printData += '<script> var red = ' + str(mature[k][pL]['co-mature']['values']) + '; </script>\n'
                                    if 'red' not in colorBoth:
                                        colorBoth['red'] = mature[k][pL]['co-mature']['values']
                                    else:
                                        colorBoth['red'] += mature[k][pL]['co-mature']['values']
                            
                            if 'mature' in mature[k][pL].keys() and 'co-mature' in mature[k][pL].keys():   
                                if  min(mature[k][pL]['mature']['values']) <= mature[k][pL]['co-mature']['values']:
                                    titleText.append('mature')
                                    titleText.append('co-mature')
                                else:
                                    titleText.append('co-mature')
                                    titleText.append('mature')
                            elif 'mature' in mature[k][pL].keys() and 'co-mature' not in mature[k][pL].keys():
                                titleText.append('mature')
                            elif 'co-mature' in mature[k][pL].keys() and 'mature' not in mature[k][pL].keys():
                                titleText.append('co-mature')
                                
                            refTF = True
                        if refTF == False:
#                             writeFile.write('<script>var red=[]; </script>\n')
                            printData += '<script>var red=[]; </script>\n'
                        break
                
#                  writeFile.write('<script> var categories = ' + str([] + precursorDict) + '; </script>\n')
                printData += '<script> var categories = ' + str([] + precursorDict) + '; </script>\n'
                
                ffl =[]
                for val in newFileList:
                    ffl.append(val + str(' - mismatch') )
#                 writeFile.write('<script> var folderFileList = ' + str(ffl) + '; </script>\n')
                
                printData += """
                 <script>
                function inArray(myArray,myValue){
                    var inArray = false;
                    myArray.map(function(key){
                        if (key === myValue){
                            inArray=true;
                        }
                    });
                    return inArray;
                };
                </script>
                """
#                 writeFile.write("""
#                 <script>
#                 function inArray(myArray,myValue){
#                     var inArray = false;
#                     myArray.map(function(key){
#                         if (key === myValue){
#                             inArray=true;
#                         }
#                     });
#                     return inArray;
#                 };
#                 </script>
#                 """)
#               
#                 #matches
#                 writeFile.write('<script>mismatch = Array(10000);</script>\n');
                elIndx=0
                
                
                
                for el in newFileList:
                    if pL in  letterDict[el].keys():
                        letterResList = []
                        for i in range(0, len(plotLRes[elPl]['categories'])):
                            if i in letterDict[el][pL].keys():
                                strLetter=''
                                for j in range(0, len(letterDict[el][pL][i])):
                                    for key, value in letterDict[el][pL][i][j].items():
                                        strLetter += '<b>' + str(key) + '</b>: ' + str(value) + ', '
                                letterResList.append(strLetter)
                            else:
                                letterResList.append('')
#                         writeFile.write('<script> mismatch[' + str(elIndx) + '] = ' + str(letterResList) + '; </script>\n')
                    else:
#                         writeFile.write('<script> mismatch[' + str(elIndx) + '] = [0]; </script>\n')
                        pass
                    elIndx+=1
                    
            countHow+=1 
            
        
        m=-1000
        elM=''
        for k in plotLRes.keys():
            if len(k) > m:
                m=len(k)
                elM = k
        
         
        elPl = elM
        
        
        
        listMatureGlobal=[]
        lInx=0
        dataListMature=[]
        dataListMatureName=[]
        
        for key0 in mature.keys():
            dataListMatureName.append(key0)
            
            
            listMature=[]
            seriesNameMature=[]
            seriesNameMatureNew=[]
            
            
            titleText = sorted(titleText)
            
            
            for key1 in titleText:
                if key1 in mature[key0][pL].keys():
                    listMaturePart=[]
                    for key2 in mature[key0][pL][key1].keys():
                        if key2!= 'values' and key2!= 'non-templated-readsLetterNot' and key2!='non-templated-readsLetter':
                            
                            listMaturePart = listMaturePart + mature[key0][pL][key1][key2].values()
                            
                            script =''
                            if key2 == 'non-templated-reads':
                                seriesNameMatureNew=[]
                                for el in mature[key0][pL][key1][key2].keys():
                                    seriesNameMatureNew.append(str(el)  + ' mismatch')
                                
                                scriptList={}
                                if 'non-templated-readsLetter' in mature[key0][pL][key1].keys():
                                    script += ' var resMisLetter =' 
                                    for el in mature[key0][pL][key1]['non-templated-readsLetter'].items():
                                        scriptList[str(el[0]) + ' mismatch'] = el[1]
                                    script += str(scriptList) + ' ;'
                                    #script += ' var resMisLetter =' + str( mature[key0][pL][key1]['non-templated-readsLetter']) + '; \n'
                                if 'non-templated-readsLetterNot' in mature[key0][pL][key1].keys():
                                    script += '\n var resMisLetterNot =' 
                                    for el in mature[key0][pL][key1]['non-templated-readsLetterNot'].items():
                                        scriptList[str(el[0]) + ' mismatch'] = el[1]
                                    script += str(scriptList) + ' ;'
                            
                            seriesNameMature = mature[key0][pL][key1][key2].keys() + seriesNameMatureNew
                            containerNameMature = str(key0) + '-' + str(key1) + '-' + str(key2)
                            
                    listMature.append(listMaturePart)
            
            
            ratioDesc = self.calcRatioDesc(listMature, titleText)  
            heteroHomoDesc, ratioHH, ratioHHAll = self.calcHeteroHomoDesc(listMature, titleText)
          
            
            if not key0 in sampleRes:
                sampleRes[key0]={}
                heatmapResultsV3[key0]={}
                
            if not pL in sampleRes[key0]:
                sampleRes[key0][pL] = {}
                heatmapResultsV3[key0][pL]={}
                heatmapResultsV3[key0][pL]={}
                
            sampleRes[key0][pL]['values'] = listMature
            sampleRes[key0][pL]['seriesNameMature'] = seriesNameMature
            
            
            sampleRes[key0][pL]['isoform'] = ratioHH
            sampleRes[key0][pL]['isoformAll'] = ratioHHAll
            
            scriptPartMiddle=''
            
            
            if (sum(listMature[0]) + sum(listMature[1])) > 0:
                lInx+=1
                                
                for elN in range(0, len(listMature)):
                    el=listMature[elN]
                    heatmapResultsV3[key0][pL][elN]=sum(el[0:14])
                
                dataListMature.append(listMature)
                
                if lInx==1:
                    listMatureGlobal = listMature
                else:
                    for l in range(0, len(listMature)):
                        for lK in range(0, len(listMature[l])):
                            listMatureGlobal[l][lK] += listMature[l][lK]

            
            else:
                scriptPartMiddle += ("""
                
                
                if (chboxs[i].id == '""" + str(key0) + """')
                {   
                    chboxs[i].disabled = true;  
                }
                
                 """)
            
         
            if scriptPartMiddle!= '':
                scriptPartStart = """
                <script>
                var chboxs = document.getElementsByName("fileListPieChart");
                        
                        var j=0;
                        for(var i=0;i<chboxs.length;i++) { 
                """
                
                scriptPartEnd = """
                }
                </script>
                """
            
#                 writeFile.write( scriptPartStart + scriptPartMiddle +  scriptPartEnd)
        
        
        
        
        changePlot=''
        changePlot += "this.chart.xAxis[0].removePlotBand('all');"
        for nelNpR in plotLRes[elPl]['seriesName']:
            changePlot += "this.chart.xAxis[0].removePlotBand('" + str(nelNpR) + "');\n"
        for elNpR in plotLRes[elPl]['seriesNameM']:
            changePlot += "this.chart.xAxis[0].removePlotBand('" + str(elNpR) + "');\n"
        
        changePlot += """
        
           var visible = this.visible ? false : true;
           
           var result = {};
           
           var updateVal= new Array(2);
           updateVal[0]=new Array(7);
           updateVal[1]=new Array(7);
           for (j=0; j<14;j++)
           {
               updateVal[0][j] = 0;
               updateVal[1][j] = 0;
           }
           
           
           for (i=0; i< this.chart.series.length; i++)
           {
               vis = this.chart.series[i].visible;
                  if( i == this.index)
                  {
                       vis = visible;
                  }
                  
                //console.log('NAME', this.chart.series[i].name);
                var dataListMature = """ + str(dataListMature) + """;
                var dataListMatureName = """ + str(dataListMatureName) + """;
               
               
               var chart1 = $('#container_""" + str(pL)+'-'+'val01' + """').highcharts();
               var nn = this.chart.series[i].name;
               var nnInd = parseInt(dataListMatureName.indexOf(nn));
               
               var mismatch = document.getElementById("selectMismatcheslist").checked;
               var misNewName= false;
               
               if (mismatch == true && nnInd == -1)
                {
                   oldName = nn
                   newName = oldName.substring(0, oldName.indexOf(" - "));
                   newName2 = oldName.substring(oldName.indexOf(" - ")+3);
                   if (newName2 == 'match&mismatch')
                   {
                       nnInd=-1;
                   }
                   else
                   {
                       var nnInd = parseInt(dataListMatureName.indexOf(newName));
                   }
                   var misNewName=true;
                   //console.log('OLDNAME', oldName, 'NEWNAME', newName, 'NEWNAME2',newName2, nnInd);
                }
               
               
               
               
               if (vis == true)
               {
                       result[this.chart.series[i].name] = 1;
                       //console.log('1', this.chart.series[i].name);
                       
                       
                       if (nnInd >= 0)
                        {
                            for (var w=0; w<2; w++)
                            {
                                var kon = dataListMature[nnInd][w].length;
                                for (var j=0; j<kon; j++)
                                {  
                                   if (mismatch == false)
                                   {
                                       //console.log(1, w, j, kon, nn, mismatch, misNewName, dataListMature[nnInd][w]);
                                       //chart1.series[w].data[j].update(dataListMature[nnInd][w][j]);
                                       updateVal[w][j] += dataListMature[nnInd][w][j];
                                    }
                                    else
                                    {   
                                        
                                        if (misNewName == true)
                                        {
                                            if (j==0)
                                            {
                                                j = dataListMature[nnInd][w].length/2;
                                            }
                                            updateVal[w][j] += dataListMature[nnInd][w][j];
                                            //chart1.series[w].data[j].update(dataListMature[nnInd][w][j]);
                                        }
                                        else
                                        { 
                                           if (j==0)
                                            {
                                                kon = dataListMature[nnInd][w].length/2;
                                            }
                                           updateVal[w][j] += dataListMature[nnInd][w][j];
                                           //chart1.series[w].data[j].update(dataListMature[nnInd][w][j]);
                                        }
                                        //console.log(2, w, j, kon, nn, mismatch, misNewName,dataListMature[nnInd][w][j],  dataListMature[nnInd][w]);
                                    }
                                    
                                }
                            }
                        }
                       
               }
               else
               {    
                       result[this.chart.series[i].name] = 0;
                       //console.log('0', this.chart.series[i].name, nnInd);
                       
                        
                        
                        if (nnInd >= 0)
                        {
                            for (var w=0; w<2; w++)
                            {
                                var kon = dataListMature[nnInd][w].length;
                                for (var j=0; j<kon; j++)
                                {  
                                   if (mismatch == false)
                                   {
                                       //console.log(3, w, j, kon, mismatch, misNewName, nn, dataListMature[nnInd][w]);
                                       //chart1.series[w].data[j].update(0);
                                       updateVal[w][j] += 0;
                                    }
                                    else
                                    {
                                        
                                        if (misNewName == true)
                                        {
                                            if (j==0)
                                            {
                                                j = dataListMature[nnInd][w].length/2;
                                            }
                                            //chart1.series[w].data[j].update(0);
                                            updateVal[w][j] += 0;
                                        }
                                        else
                                        {
                                           if (j==0)
                                           {
                                               kon = dataListMature[nnInd][w].length/2;
                                           }
                                           //chart1.series[w].data[j].update(0);
                                           updateVal[w][j] += 0;
                                        }
                                    }
                                }
                            }
                        }
               }
           }
           
           for (var w=0; w<2; w++)
            {
                for (var j=0; j<14; j++)
                {
                chart1.series[w].data[j].update(updateVal[w][j]);
                }
            }
           
           \n
        """
        
        
        
        
        for elNpR in range(0, len(plotLRes[elPl]['dataY'])):
            changePlot += self.calcPlotband(plotLRes[elPl]['seriesName'][elNpR], plotLRes[elPl]['dataY'][elNpR])
        
        
        
        for elNpR in range(0, len(plotLRes[elPl]['dataM'])):
            if ' - mismatch' in  plotLRes[elPl]['seriesNameM'][elNpR]:
                newdataM=[x+y for x, y in zip(plotLRes[elPl]['dataM'][elNpR+1], plotLRes[elPl]['dataM'][elNpR])]
                changePlot += self.calcPlotband(plotLRes[elPl]['seriesNameM'][elNpR], newdataM)
        
        colorPackage = self.checkColor(plotLRes[elPl]['seriesName'], colorDictRes)
        
        
        
#         writeFile.write(''.join(hist.drawColumnChart( 
#                     dataY = plotLRes[elPl]['dataY'],                               
#                      yAxisTitle='reads/million',
#                      containerName =  str(0),
#                      seriesName=plotLRes[elPl]['seriesName'], 
#                      tickInterval =1,
#                      label= '<b>{series.name}: </b>{point.y} <br \>',
#                      stacking = True,
#                      titleText = pL,
#                      useColors=False,
#                      tickMinValue=0,
#                      plotLines=True,
#                      itemMarginBottom=1,
#                      script=script,
#                      extraOptions=True,
#                      changePlot=changePlot,
#                      addLegendFake=True,
#                      colorPackage=colorPackage)))
#         
        
        colorPackage = self.checkColor(plotLRes[elPl]['seriesNameM'], colorDictRes)
        
        
#         writeFile.write(''.join(hist.drawColumnChart(dataY=plotLRes[elPl]['dataM'], 
#                           yAxisTitle='reads/million',
#                           containerName = str(1),
#                           seriesName=plotLRes[elPl]['seriesNameM'], 
#                           tickInterval=1,
#                           label= '<b>{series.name}: </b>{point.y} <br \>',
#                           stacking = True,
#                           titleText = pL,
#                           plotLines=True,
#                           useColors=True,
#                           extraArg=True,
#                           linkedSeries=3,
#                           tickMinValue=0,
#                           itemMarginBottom=1,
#                           script=script,
#                           extraOptions=True,
#                           changePlot=changePlot,
#                           addLegendFake=True,
#                           colorPackage=colorPackage)))
        
        
#         self.visualizateTableWithout(writeFile, plotLRes[elPl]['seriesName'])
#         writeFile.write('</div>')
        
        
        
        
        
        extraSc = """
            ,function(chart) {
                        $(chart.series[0].data).each(function(i, e) {
                            e.legendItem.on('click', function(event) {
                            
                            
                                var legendItem=e.name;
                                
                                event.stopPropagation();
                                
                                $(chart.series).each(function(j,f){
                                       $(this.data).each(function(k,z){
                                           if(z.name==legendItem)
                                           {
                                               if(z.visible)
                                               {
                                                   z.setVisible(false);
                                               }
                                               else
                                               {
                                                   z.setVisible(true);
                                               }
                                           }
                                       });
                                });
                                
                            });
                        });
                    }
                    """
        
        
#         writeFile.write("""
#         <script>
#         
#         (function (Highcharts) {
#     Highcharts.seriesTypes.pie.prototype.setTitle = function (titleOption) {
#         var chart = this.chart,
#             center = this.center || (this.yAxis && this.yAxis.center),
#             labelBox,
#             box,
#             format;
#         
#         if (center && titleOption) {
#             box = {
#                 x: chart.plotLeft + center[0] - 0.5 * center[2],
#                 y: chart.plotTop + center[1] - 0.5 * center[2],
#                 width: center[2],
#                 height: center[2]
#             };
#             
#             format = titleOption.text || titleOption.format;
#             format = Highcharts.format(format, this);
# 
#             if (this.title) {
#                 this.title.attr({
#                     text: format
#                 });
#                 
#             } else {
#                 this.title = this.chart.renderer.label(format)
#                     .css(titleOption.style)
#                     .add()
#             }
#             labelBBox = this.title.getBBox();
#             titleOption.width = labelBBox.width;
#             titleOption.height = labelBBox.height;
#             this.title.align(titleOption, null, box);
#         }
#     };
#     
#     Highcharts.wrap(Highcharts.seriesTypes.pie.prototype, 'render', function (proceed) {
#         proceed.call(this);
#         this.setTitle(this.options.title);
#     });
# 
# } (Highcharts));</script>
#         
#         
#         """)
        

        
        for key0 in mature.keys():
            seriesNameMature=[]
            seriesNameMatureNew=[]
            for key1 in ['mature', 'star', 'co-mature']:
                if key1 in mature[key0][pL].keys():
                    listMaturePart=[]
                    for key2 in mature[key0][pL][key1].keys():
                        if key2!= 'values' and key2!= 'non-templated-readsLetterNot' and key2!='non-templated-readsLetter':
                            if key2 == 'non-templated-reads':
                                seriesNameMatureNew=[]
                                for el in mature[key0][pL][key1][key2].keys():
                                    seriesNameMatureNew.append(str(el)  + ' mismatch')
                            
                            seriesNameMature = mature[key0][pL][key1][key2].keys() + seriesNameMatureNew
        
                            
#         self.visualizateTableLegend(writeFile, seriesNameMature)
        
        
        
        
        if len(listMatureGlobal) > 0:
#             writeFile.write('<div style="display:none" id = "containerPieChart' + '" class="containerPieChart'   + '">')
#             writeFile.write('<div class="statistic">')
#             
#             
            
            
            for key1 in titleText:
                
                extraSc2=''
                for sNM in range(0, len(seriesNameMature)):
                        extraSc2 +=""" $('#""" + str(sNM) + """').click(function () {
                        var chart = $('#container_""" + str(pL)+'-'+'val01' + """').highcharts();
                        //console.log(""" + str(sNM) + """);
                        for (var i=0; i<2; i++)
                        {
                            //console.log(chart.series[i].data[""" + str(sNM) + """]);
                            if (chart.series[i].data[""" + str(sNM) + """].visible) 
                            {
                                chart.series[i].data[""" + str(sNM) + """].setVisible(false, false);
                                document.getElementById(""" + str(sNM) + """).style.color = "#FCFCFC";
                                //console.log(0, i, chart.series[i]);
                                
                            } 
                            else 
                            {
                                chart.series[i].data[""" + str(sNM) + """].setVisible(true, true);
                                document.getElementById(""" + str(sNM) + """).style.color = "#000000";
                                //console.log(1, i, chart.series[i]);
                            }
                        }
                        chart.redraw();
                    });   
        
            """
            
#             writeFile.write(''.join(hist.drawPieChartWithSingleLegend(listMatureGlobal,
#                                                                       seriesName=seriesNameMature,
#                                                                       containerName= str(pL)+'-'+'val01',
#                                                                       addOptions='width: 100%; float:right; margin: 0 auto; ',
#                                                                       titleText = titleText,
#                                                                       label='Value: {point.name} {point.y}  - <b>{point.percentage:.1f}%</b>',
#                                                                       itemMarginBottom=2,
#                                                                       extraScript=script,
#                                                                       extraSc2 = extraSc2,
#                                                                       size=300,
#                                                                       useColors=False
#                                                                       )))
#             
#             writeFile.write('</div>')
#             writeFile.write('</div>')  
#         
#         
#         writeFile.write(str(self.addReads(readsDict, precursorDict, colorBoth)))
#         
#         
#         writeFile.write('</BODY></HTML>')
#         writeFile.close()
        
        print 'done doPlot for: ' + str(pL)
        return sampleRes, heatmapResultsV3  
    
    def doPlotCopy(self, combinationsFileList, plotLRes, pL, newFileList, mature, letterDict, outputResults, precursorDict, colorDictRes, sampleRes, readsDict, heatmapResultsV3 ):
        
        
        printData=''
        writeFile = open(outputResults + '/' + str(pL)  + '.html', 'w')
        writeFile.write('<HTML><HEAD>')
        writeFile.write(""" 
         <script src="http://www.kryogenix.org/code/browser/sorttable/sorttable.js" type="text/javascript"></script> 
        """)
        
        
        writeFile.write('<link href="https://fonts.googleapis.com/css?family=Roboto+Condensed:300" rel="stylesheet" type="text/css"></HEAD><BODY onLoad="loadPage()" style="font-family: Roboto Condensed;font-size:1.5em"><div id ="plot">')
        hist = vis()
        
        script = '' 
        dictName ={}
        dictNameM ={}
        countHow=0
        countHow2=0
        
        for nF in newFileList:
            script += self.addScriptExtra(nF)
            
        m=-1000
        elM=''
        for k in plotLRes.keys():
            if len(k) > m:
                m=len(k)
                elM = k
        
        
        elPl = elM
        
        for name in plotLRes[elPl]['seriesName']:
            dictName[name] = countHow
            countHow+=1
        for name in plotLRes[elPl]['seriesNameM']:
            dictNameM[name] = countHow2
            countHow2+=1
        
        
        writeFile.write('<script>' + 'var myMap0 = ' + str(dictName) + '; </script>\n')
        writeFile.write('<script>' + 'var myMap1 = ' + str(dictNameM) + '; </script>\n')  
        
        
        
        writeFile.write(hist.addLoadPage())
        writeFile.write(hist._addLib())
        writeFile.write(hist._addStyle())
        writeFile.write(hist.addShowHide())

        
        countHow = 0
        titleText=[]
        
        colorBoth={}
        for elPl in plotLRes:
            
            if countHow == 0:
                for k in plotLRes.keys():
                    if k in mature.keys():
                        blueTF = False
                        
                        if 'star' in mature[k][pL].keys():
                            writeFile.write('<script> var blue = ' + str(mature[k][pL]['star']['values']) + '; </script>\n')
                            printData += '<script> var blue = ' + str(mature[k][pL]['star']['values']) + '; </script>\n'
                            colorBoth['blue'] = mature[k][pL]['star']['values']
                            blueTF = True
                            titleText.append('star')
                        if blueTF == False:
                            writeFile.write('<script>var blue=[]; </script>\n')
                            printData += '<script>var blue=[]; </script>\n'
                        
                        #combain mature and co-mature
                        refTF = False
                        if 'mature' in mature[k][pL].keys() or 'co-mature' in mature[k][pL].keys():
                            if blueTF == False:
                                writeFile.write('<script> var red = ' + str(mature[k][pL]['mature']['values']+mature[k][pL]['co-mature']['values']) + '; </script>\n')
                                printData += '<script> var red = ' + str(mature[k][pL]['mature']['values']+mature[k][pL]['co-mature']['values']) + '; </script>\n'
                                colorBoth['red'] = mature[k][pL]['mature']['values']+mature[k][pL]['co-mature']['values']
                                
                            else:
                                if 'mature' in mature[k][pL].keys():
                                    writeFile.write('<script> var red = ' + str(mature[k][pL]['mature']['values']) + '; </script>\n')
                                    printData += '<script> var red = ' + str(mature[k][pL]['mature']['values']) + '; </script>\n'
                                    if 'red' not in colorBoth:
                                        colorBoth['red'] = mature[k][pL]['mature']['values']
                                    else:
                                        colorBoth['red'] += mature[k][pL]['mature']['values']
                                    
                                if 'co-mature' in mature[k][pL].keys():
                                    writeFile.write('<script> var red = ' + str(mature[k][pL]['co-mature']['values']) + '; </script>\n')
                                    printData += '<script> var red = ' + str(mature[k][pL]['co-mature']['values']) + '; </script>\n'
                                    if 'red' not in colorBoth:
                                        colorBoth['red'] = mature[k][pL]['co-mature']['values']
                                    else:
                                        colorBoth['red'] += mature[k][pL]['co-mature']['values']
                            
                            if 'mature' in mature[k][pL].keys() and 'co-mature' in mature[k][pL].keys():   
                                if  min(mature[k][pL]['mature']['values']) <= mature[k][pL]['co-mature']['values']:
                                    titleText.append('mature')
                                    titleText.append('co-mature')
                                else:
                                    titleText.append('co-mature')
                                    titleText.append('mature')
                            elif 'mature' in mature[k][pL].keys() and 'co-mature' not in mature[k][pL].keys():
                                titleText.append('mature')
                            elif 'co-mature' in mature[k][pL].keys() and 'mature' not in mature[k][pL].keys():
                                titleText.append('co-mature')
                                
                            refTF = True
                        if refTF == False:
                            writeFile.write('<script>var red=[]; </script>\n')
                            printData += '<script>var red=[]; </script>\n'
                        break
                
                #categories from precursor File
                #writeFile.write('<script> var categories = ' + str([] + plotLRes[elPl]['categories']) + '; </script>\n')
                writeFile.write('<script> var categories = ' + str([] + precursorDict) + '; </script>\n')
                printData += '<script> var categories = ' + str([] + precursorDict) + '; </script>\n'
                
                ffl =[]
                for val in newFileList:
                    ffl.append(val + str(' - mismatch') )
                writeFile.write('<script> var folderFileList = ' + str(ffl) + '; </script>\n')
                
                printData += """
                 <script>
                function inArray(myArray,myValue){
                    var inArray = false;
                    myArray.map(function(key){
                        if (key === myValue){
                            inArray=true;
                        }
                    });
                    return inArray;
                };
                </script>
                """
                writeFile.write("""
                <script>
                function inArray(myArray,myValue){
                    var inArray = false;
                    myArray.map(function(key){
                        if (key === myValue){
                            inArray=true;
                        }
                    });
                    return inArray;
                };
                </script>
                """)
              
                #matches
                writeFile.write('<script>mismatch = Array(10000);</script>\n');
                elIndx=0
                
                
                
                for el in newFileList:
                    if pL in  letterDict[el].keys():
                        letterResList = []
                        for i in range(0, len(plotLRes[elPl]['categories'])):
                            if i in letterDict[el][pL].keys():
                                strLetter=''
                                for j in range(0, len(letterDict[el][pL][i])):
                                    for key, value in letterDict[el][pL][i][j].items():
                                        strLetter += '<b>' + str(key) + '</b>: ' + str(value) + ', '
                                letterResList.append(strLetter)
                            else:
                                letterResList.append('')
                        writeFile.write('<script> mismatch[' + str(elIndx) + '] = ' + str(letterResList) + '; </script>\n')
                    else:
                        writeFile.write('<script> mismatch[' + str(elIndx) + '] = [0]; </script>\n')
                    elIndx+=1
                    
            countHow+=1 
            
        
        m=-1000
        elM=''
        for k in plotLRes.keys():
            if len(k) > m:
                m=len(k)
                elM = k
        
         
        elPl = elM
        
        changePlot=''
        changePlot += "this.chart.xAxis[0].removePlotBand('all');"
        for nelNpR in plotLRes[elPl]['seriesName']:
            changePlot += "this.chart.xAxis[0].removePlotBand('" + str(nelNpR) + "');\n"
        for elNpR in plotLRes[elPl]['seriesNameM']:
            changePlot += "this.chart.xAxis[0].removePlotBand('" + str(elNpR) + "');\n"
        
        changePlot += """
        
           var visible = this.visible ? false : true;
           
           var result = {};
           for (i=0; i< this.chart.series.length; i++)
           {
               vis = this.chart.series[i].visible;
                  if( i == this.index)
                  {
                       vis = visible;
                  }
               
               if (vis == true)
               {
                       result[this.chart.series[i].name] = 1;
                       console.log('1', this.chart.series[i].name);
               }
               else
               {    
                       result[this.chart.series[i].name] = 0;
                       console.log('0', this.chart.series[i].name);
               }
           }\n
        """
        
        for elNpR in range(0, len(plotLRes[elPl]['dataY'])):
            changePlot += self.calcPlotband(plotLRes[elPl]['seriesName'][elNpR], plotLRes[elPl]['dataY'][elNpR])
        
        
        
        for elNpR in range(0, len(plotLRes[elPl]['dataM'])):
            if ' - mismatch' in  plotLRes[elPl]['seriesNameM'][elNpR]:
                newdataM=[x+y for x, y in zip(plotLRes[elPl]['dataM'][elNpR+1], plotLRes[elPl]['dataM'][elNpR])]
                changePlot += self.calcPlotband(plotLRes[elPl]['seriesNameM'][elNpR], newdataM)
        
        colorPackage = self.checkColor(plotLRes[elPl]['seriesName'], colorDictRes)
        
        
        
        writeFile.write(''.join(hist.drawColumnChart( 
                    dataY = plotLRes[elPl]['dataY'],                               
                     yAxisTitle='reads/million',
                     containerName =  str(0),
                     seriesName=plotLRes[elPl]['seriesName'], 
                     tickInterval =1,
                     label= '<b>{series.name}: </b>{point.y} <br \>',
                     stacking = True,
                     titleText = pL,
                     useColors=False,
                     tickMinValue=0,
                     plotLines=True,
                     itemMarginBottom=1,
                     script=script,
                     extraOptions=True,
                     changePlot=changePlot,
                     addLegendFake=True,
                     colorPackage=colorPackage)))
        
        
        colorPackage = self.checkColor(plotLRes[elPl]['seriesNameM'], colorDictRes)
        
        
        writeFile.write(''.join(hist.drawColumnChart(dataY=plotLRes[elPl]['dataM'], 
                          yAxisTitle='reads/million',
                          containerName = str(1),
                          seriesName=plotLRes[elPl]['seriesNameM'], 
                          tickInterval=1,
                          label= '<b>{series.name}: </b>{point.y} <br \>',
                          stacking = True,
                          titleText = pL,
                          plotLines=True,
                          useColors=True,
                          extraArg=True,
                          linkedSeries=3,
                          tickMinValue=0,
                          itemMarginBottom=1,
                          script=script,
                          extraOptions=True,
                          changePlot=changePlot,
                          addLegendFake=True,
                          colorPackage=colorPackage)))
        
        self.doImage(pL, plotLRes[elPl]['dataY'], plotLRes[elPl]['seriesName'], script, changePlot, plotLRes[elPl]['dataM'], plotLRes[elPl]['seriesNameM'], printData)
        
        self.visualizateTable(writeFile, plotLRes[elPl]['seriesName'])
        writeFile.write('</div>')
        
        
        writeFile.write(str(self.addReads(readsDict, precursorDict, colorBoth)))
        
        
        
        extraSc = """
            ,function(chart) {
                        $(chart.series[0].data).each(function(i, e) {
                            e.legendItem.on('click', function(event) {
                                var legendItem=e.name;
                                
                                event.stopPropagation();
                                
                                $(chart.series).each(function(j,f){
                                       $(this.data).each(function(k,z){
                                           if(z.name==legendItem)
                                           {
                                               if(z.visible)
                                               {
                                                   z.setVisible(false);
                                               }
                                               else
                                               {
                                                   z.setVisible(true);
                                               }
                                           }
                                       });
                                });
                                
                            });
                        });
                    }
                    """
        
        
        writeFile.write("""
        <script>
        
        (function (Highcharts) {
    Highcharts.seriesTypes.pie.prototype.setTitle = function (titleOption) {
        var chart = this.chart,
            center = this.center || (this.yAxis && this.yAxis.center),
            labelBox,
            box,
            format;
        
        if (center && titleOption) {
            box = {
                x: chart.plotLeft + center[0] - 0.5 * center[2],
                y: chart.plotTop + center[1] - 0.5 * center[2],
                width: center[2],
                height: center[2]
            };
            
            format = titleOption.text || titleOption.format;
            format = Highcharts.format(format, this);

            if (this.title) {
                this.title.attr({
                    text: format
                });
                
            } else {
                this.title = this.chart.renderer.label(format)
                    .css(titleOption.style)
                    .add()
            }
            labelBBox = this.title.getBBox();
            titleOption.width = labelBBox.width;
            titleOption.height = labelBBox.height;
            this.title.align(titleOption, null, box);
        }
    };
    
    Highcharts.wrap(Highcharts.seriesTypes.pie.prototype, 'render', function (proceed) {
        proceed.call(this);
        this.setTitle(this.options.title);
    });

} (Highcharts));</script>
        
        
        """)
        

        
        for key0 in mature.keys():
            seriesNameMature=[]
            seriesNameMatureNew=[]
            for key1 in ['mature', 'star', 'co-mature']:
                if key1 in mature[key0][pL].keys():
                    listMaturePart=[]
                    for key2 in mature[key0][pL][key1].keys():
                        if key2!= 'values' and key2!= 'non-templated-readsLetterNot' and key2!='non-templated-readsLetter':
                            if key2 == 'non-templated-reads':
                                seriesNameMatureNew=[]
                                for el in mature[key0][pL][key1][key2].keys():
                                    seriesNameMatureNew.append(str(el)  + ' mismatch')
                            
                            seriesNameMature = mature[key0][pL][key1][key2].keys() + seriesNameMatureNew
        
                            
        self.visualizateTableLegend(writeFile, seriesNameMature)
        
        
        
     
        for key0 in mature.keys():
            
            
            
            listMature=[]
            seriesNameMature=[]
            seriesNameMatureNew=[]
            
            
            titleText = sorted(titleText)
            
            
            for key1 in titleText:
                if key1 in mature[key0][pL].keys():
                    listMaturePart=[]
                    for key2 in mature[key0][pL][key1].keys():
                        if key2!= 'values' and key2!= 'non-templated-readsLetterNot' and key2!='non-templated-readsLetter':
                            
                            listMaturePart = listMaturePart + mature[key0][pL][key1][key2].values()
                            
                            script =''
                            if key2 == 'non-templated-reads':
                                seriesNameMatureNew=[]
                                for el in mature[key0][pL][key1][key2].keys():
                                    seriesNameMatureNew.append(str(el)  + ' mismatch')
                                
                                scriptList={}
                                if 'non-templated-readsLetter' in mature[key0][pL][key1].keys():
                                    script += ' var resMisLetter =' 
                                    for el in mature[key0][pL][key1]['non-templated-readsLetter'].items():
                                        scriptList[str(el[0]) + ' mismatch'] = el[1]
                                    script += str(scriptList) + ' ;'
                                    #script += ' var resMisLetter =' + str( mature[key0][pL][key1]['non-templated-readsLetter']) + '; \n'
                                if 'non-templated-readsLetterNot' in mature[key0][pL][key1].keys():
                                    script += '\n var resMisLetterNot =' 
                                    for el in mature[key0][pL][key1]['non-templated-readsLetterNot'].items():
                                        scriptList[str(el[0]) + ' mismatch'] = el[1]
                                    script += str(scriptList) + ' ;'
                                    #script += ' var resMisLetterNot =' + str( mature[key0][pL][key1]['non-templated-readsLetterNot']) + '; \n'
                                
                                
                                
#                             if key2 == 'template-reads':
#                                 script += ' var resMisLetter = ""; var resMisLetterNot = ""; \n'
                            
                            seriesNameMature = mature[key0][pL][key1][key2].keys() + seriesNameMatureNew
                            containerNameMature = str(key0) + '-' + str(key1) + '-' + str(key2)
                            
                    listMature.append(listMaturePart)
            
            extraSc2=''
            for sNM in range(0, len(seriesNameMature)):
                extraSc2 +=""" $('#""" + str(sNM) + """').click(function () {
                        var chart = $('#container_""" + str(containerNameMature) + """').highcharts();
                            
                        for (var i=0; i<2; i++)
                        {
                            if (chart.series[i].data[""" + str(sNM) + """].visible) 
                            {
                                chart.series[i].data[""" + str(sNM) + """].setVisible(false, false);
                                document.getElementById(""" + str(sNM) + """).style.color = "#FCFCFC";
                                
                            } 
                            else 
                            {
                                chart.series[i].data[""" + str(sNM) + """].setVisible(true, true);
                                document.getElementById(""" + str(sNM) + """).style.color = "#000000";
                            }
                        }
                        chart.redraw();
                    });   
        
            """
            ratioDesc = self.calcRatioDesc(listMature, titleText)  
            heteroHomoDesc, ratioHH, ratioHHAll = self.calcHeteroHomoDesc(listMature, titleText)
          
            
            if not key0 in sampleRes:
                sampleRes[key0]={}
                heatmapResultsV3[key0]={}
                
            if not pL in sampleRes[key0]:
                sampleRes[key0][pL] = {}
                heatmapResultsV3[key0][pL]={}
                heatmapResultsV3[key0][pL]={}
                
            sampleRes[key0][pL]['values'] = listMature
            sampleRes[key0][pL]['seriesNameMature'] = seriesNameMature
            
            
            sampleRes[key0][pL]['isoform'] = ratioHH
            sampleRes[key0][pL]['isoformAll'] = ratioHHAll
            
            scriptPartMiddle=''
            if (sum(listMature[0]) + sum(listMature[1])) > 0:
                writeFile.write('<div style="display:none" id = "containerPieChart_' + str(key0) + '" class="containerPieChart_' + str(key0)  + '">')
                writeFile.write('<div class="statistic">')
                writeFile.write('<div class="statisticTitle">' + str(key0) + '</div>')
                writeFile.write('<div class="statisticTitleDesc">' + str(ratioDesc)  + '</div>' )
                writeFile.write('<div class="statisticTitleDesc">' + str(heteroHomoDesc)  + '</div>' )
                
                
                for elN in range(0, len(listMature)):
                    el=listMature[elN]
                    heatmapResultsV3[key0][pL][elN]=sum(el[0:14])
                
                writeFile.write(''.join(hist.drawPieChartWithSingleLegend(listMature,
                                                                      seriesName=seriesNameMature,
                                                                      containerName= containerNameMature,
                                                                      addOptions='width: 100%; float:right; margin: 0 auto; ',
                                                                      titleText = titleText,
                                                                      label='Value: {point.name} {point.y}  - <b>{point.percentage:.1f}%</b>',
                                                                      itemMarginBottom=2,
                                                                      extraScript=script,
                                                                      extraSc2 = extraSc2,
                                                                      size=300,
                                                                      useColors=False
                                                                      )))
                
                 
                writeFile.write('</div>')
                writeFile.write('</div>')    
            
            else:
                scriptPartMiddle += ("""
                
                
                if (chboxs[i].id == '""" + str(key0) + """')
                {   
                    chboxs[i].disabled = true;  
                }
                
                 """)
                
        
            if scriptPartMiddle!= '':
                scriptPartStart = """
                <script>
                var chboxs = document.getElementsByName("fileListPieChart");
                        
                        var j=0;
                        for(var i=0;i<chboxs.length;i++) { 
                """
                
                scriptPartEnd = """
                }
                </script>
                """
            
                writeFile.write( scriptPartStart + scriptPartMiddle +  scriptPartEnd)
        
        
        
        writeFile.write('</BODY></HTML>')
        writeFile.close()
        
        print 'done doPlot for: ' + str(pL)
        return sampleRes, heatmapResultsV3
    
    def doImage(self, outputResults, pL, dataY, seriesNameY, script, changePlot, dataM, seriesNameM, printData):  
        
        
        writeFile = open(outputResults + '/image/' + str(pL)  + '.html', 'w')
        writeFile.write('<HTML><HEAD>')
        
        hist = vis(height=150)
        writeFile.write(hist.addLoadPage())
        writeFile.write(hist._addLib())
        writeFile.write(hist._addStyle())
        writeFile.write(hist.addShowHide())

        writeFile.write(printData)
        
            
        
        writeFile.write("""<button id='save_btn'>Save Chart</button>
        <script>
        
            EXPORT_WIDTH = 900;
function download(data, filename) {



  var a = document.createElement('a');
  a.download = filename;
  a.href = data
  document.body.appendChild(a);
  a.click();
  a.remove();
}

function save_chart(chart) {
  render_width = EXPORT_WIDTH;
  render_height = 150; //render_width * chart.chartHeight / chart.chartWidth

  // Get the cart's SVG code
  var svg = chart.getSVG({
    exporting: {
      sourceWidth: chart.chartWidth,
      sourceHeight: chart.chartHeight
    }
  });

  // Create a canvas
  var canvas = document.createElement('canvas');
  canvas.height = render_height;
  canvas.width = render_width;
  document.body.appendChild(canvas);

  // Create an image and draw the SVG onto the canvas
  var image = new Image;
  image.onload = function() {
    canvas.getContext('2d').drawImage(this, 0, 0, render_width, render_height);
    
    var data = canvas.toDataURL("image/png")
    download(data, '""" + str(pL) + """' + '.png')
  };
    
    image.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svg)));
    
    
    
}


            </script>
        """)
        writeFile.write("""
        <script>
     

        
        </script>
        """)
        
#         writeFile.write(''.join(hist.drawColumnChart( 
#                     dataY = dataY,                               
#                      yAxisTitle='reads/million',
#                      containerName =  str(0),
#                      seriesName=seriesNameY, 
#                      tickInterval =1,
#                      label= '<b>{series.name}: </b>{point.y} <br \>',
#                      stacking = True,
#                      titleText = pL,
#                      useColors=False,
#                      tickMinValue=0,
#                      plotLines=True,
#                      itemMarginBottom=1,
#                      script=script,
#                      extraOptions=True,
#                      changePlot=None,
#                      addLegendFake=True)))
        
        dataMM=[[sum(i) for i in zip(*dataM)]]
      
        
        writeFile.write(''.join(hist.drawColumnChart(dataY=dataMM, 
                          #yAxisTitle='reads/million',
                          containerName = str(1),
                          addOptions='display:block;width:900px;',
                          height=50,
                          seriesName=seriesNameM, 
                          tickInterval=1,
                          label= '<b>{series.name}: </b>{point.y} <br \>',
                          stacking = True,
                          #titleText = pL,
                          plotLines=True,
                          useColors='onlyRed',
                          extraArg='onlyRed',
                          linkedSeries=3,
                          tickMinValue=0,
                          itemMarginBottom=1,
                          script=script,
                          extraOptions=True,
                          changePlot=None,
                          addLegendFake=True,
                          legend='img',
                          visibleY=False,
                          addPlotOptExtra="series: { borderWidth: 1, borderColor: '#ff3232', }, ",
                          addLegendFakeColor='#d8d8d8 ')))
 
        
        
        writeFile.write('</BODY></HTML>')
        writeFile.close()
        
        print 'done doPlot IMAGE for: ' + str(pL)
    
    def doPie(self, plotList, mature, outputPie, fileTotal):
        
        
        
        
        read={}
        readGlobal=mature.keys()
        for fL in readGlobal:
            read[fL]={}
            for name in ['mature', 'star']:
                read[fL][name]={}
                    
                if not 'template-reads' in read[fL][name]:
                    read[fL][name]['template-reads']={}
                if not 'non-templated-reads' in read[fL][name]:
                    read[fL][name]['non-templated-reads']={}
                    
                    for el in ["5' elongated", "5' truncated", "3' elongated", "3' truncated", 'both elongated', 'both truncated', 'canonical']:
                        read[fL][name]['template-reads'][el]=0
                        read[fL][name]['non-templated-reads'][el]=0
        
        
        for key0 in mature.keys():
            titleText=['mature', 'star']
            seriesNameMature=[]
            seriesNameMatureNew=[]
            for pL in plotList.keys():
                for key1 in ['mature', 'star']:
                    if key1 in mature[key0][pL].keys():
                        for key2 in mature[key0][pL][key1].keys():
                            
                            if key2!= 'values' and key2!= 'non-templated-readsLetterNot' and key2!='non-templated-readsLetter':
                                
                                for el in mature[key0][pL][key1][key2].items():
                                    read[key0][key1][key2][el[0]] += el[1]
                                    
                              
                                script =''
                                if key2 == 'non-templated-reads':
                                    seriesNameMatureNew=[]
                                    for el in mature[key0][pL][key1][key2].keys():
                                        seriesNameMatureNew.append(str(el)  + ' mismatch')
                                    
                                    scriptList={}
                                    if 'non-templated-readsLetter' in mature[key0][pL][key1].keys():
                                        script += ' var resMisLetter =' 
                                        for el in mature[key0][pL][key1]['non-templated-readsLetter'].items():
                                            scriptList[str(el[0]) + ' mismatch'] = el[1]
                                        script += str(scriptList) + ' ;'
                                    if 'non-templated-readsLetterNot' in mature[key0][pL][key1].keys():
                                        script += '\n var resMisLetterNot =' 
                                        for el in mature[key0][pL][key1]['non-templated-readsLetterNot'].items():
                                            scriptList[str(el[0]) + ' mismatch'] = el[1]
                                        script += str(scriptList) + ' ;'
                                
                                seriesNameMature = mature[key0][pL][key1][key2].keys() + seriesNameMatureNew
                                containerNameMature = str(key0) + '-' + str(key1) + '-' + str(key2)
                            
       
        writeFile = open(outputPie +'/' + 'global'  + '.html', 'w')
        writeFile.write('<HTML><HEAD><link href="https://fonts.googleapis.com/css?family=Roboto+Condensed:300" rel="stylesheet" type="text/css"></HEAD><BODY   onLoad="loadPagePie()"  style="font-family: Roboto Condensed;font-size:1.5em"><div id ="plot">')
        self.visualizateTableGlobal(writeFile, read.keys())
           
       
        hist = vis()
        writeFile.write(hist.addLoadPagePie())
        writeFile.write(hist._addLib())
        writeFile.write(hist._addStyle())
        writeFile.write(hist.addShowHidePie())
        
        self.visualizateTableLegend(writeFile, seriesNameMature)
        
        iVis=0
        
        fileTot={}
        for fL, flV in fileTotal.items():
            fileTot[fL.split('.')[0]] = flV
        
        
        for r in read:
            
            extraSc2=''
            
            for sNM in range(0, len(seriesNameMature)):
                extraSc2 +=""" $('#""" + str(sNM) + """').click(function () {
                        var chart = $('#container_""" + str(containerNameMature + str(r)) + """').highcharts();
                            
                        for (var i=0; i<2; i++)
                        {
                            if (chart.series[i].data[""" + str(sNM) + """].visible) 
                            {
                                chart.series[i].data[""" + str(sNM) + """].setVisible(false, false);
                                document.getElementById(""" + str(sNM) + """).style.color = "#FCFCFC";
                            } 
                            else 
                            {
                                chart.series[i].data[""" + str(sNM) + """].setVisible(true, true);
                                document.getElementById(""" + str(sNM) + """).style.color = "#000000";
                            }
                        }
                        chart.redraw();
                    });   
        
        """
            
            
            writeFile.write('<div style="display:none" id = "containerPieChart_' + str(r) + '" class="containerPieChart_' + str(r)  + '">')
        
            
            
            
            
            

            if iVis==0:
                writeFile.write("""
                <script>
                
                (function (Highcharts) {
            Highcharts.seriesTypes.pie.prototype.setTitle = function (titleOption) {
                var chart = this.chart,
                    center = this.center || (this.yAxis && this.yAxis.center),
                    labelBox,
                    box,
                    format;
                
                if (center && titleOption) {
                    box = {
                        x: chart.plotLeft + center[0] - 0.5 * center[2],
                        y: chart.plotTop + center[1] - 0.5 * center[2],
                        width: center[2],
                        height: center[2]
                    };
                    
                    format = titleOption.text || titleOption.format;
                    format = Highcharts.format(format, this);
        
                    if (this.title) {
                        this.title.attr({
                            text: format
                        });
                        
                    } else {
                        this.title = this.chart.renderer.label(format)
                            .css(titleOption.style)
                            .add()
                    }
                    labelBBox = this.title.getBBox();
                    titleOption.width = labelBBox.width;
                    titleOption.height = labelBBox.height;
                    this.title.align(titleOption, null, box);
                }
            };
            
            Highcharts.wrap(Highcharts.seriesTypes.pie.prototype, 'render', function (proceed) {
                proceed.call(this);
                this.setTitle(this.options.title);
            });
        
        } (Highcharts));</script>
                
        
        """)
            
#             sumVal =  sum(read[r][rD]['template-reads'].values() + read[r][rD]['non-templated-reads'].values())
#                 print sumVal
#                 if sumVal!=0:
#                     templateReads = [val/sumVal for val in read[r][rD]['template-reads'].values()]
#                 else:
#                     templateReads = read[r][rD]['template-reads'].values()
#                 listMaturePart.append(templateReads + read[r][rD]['non-templated-reads'].values())
            
            
            
            
            listMaturePart=[]
            
            for rD in titleText:
                #sumVal = float(sum(read[r][rD]['template-reads'].values() + read[r][rD]['non-templated-reads'].values()))
                
                
                lF = [round(float(el)/(float(fileTot[r])),2) for el in read[r][rD]['template-reads'].values()]
                rF = [round(float(el)/(float(fileTot[r])),2) for el in read[r][rD]['non-templated-reads'].values()]
                
                listMaturePart.append(lF + rF)
            
            
            
            ratioDesc=self.calcRatioDesc(listMaturePart, titleText)
            heteroHomoDesc, ratioHH, ratioHHAll = self.calcHeteroHomoDesc(listMaturePart, titleText)
            
            writeFile.write('<div class="statistic">')
            writeFile.write('<div class="statisticTitle">' + str(r) + '( Relative error [RPM])' +  '</div>')
            writeFile.write('<div class="statisticTitleDesc">' + str(ratioDesc)  + '</div>')
            writeFile.write('<div class="statisticTitleDesc">' + str(heteroHomoDesc)  + '</div>' )
            
            
            writeFile.write(''.join(hist.drawPieChartWithSingleLegend(listMaturePart,
                                                                  seriesName=seriesNameMature,
                                                                  containerName= containerNameMature + str(r),
                                                                  addOptions='width: 100%; float:right; margin: 0 auto; ',
                                                                  titleText = titleText,
                                                                  label='Value: {point.name} {point.y}  - <b>{point.percentage:.1f}%</b>',
                                                                  itemMarginBottom=2,
                                                                  extraScript=script,
                                                                  extraSc2 = extraSc2,
                                                                  size=300,
                                                                  useColors=False
                                                                  )))
             
            writeFile.write('</div>')
            writeFile.write('</div>')  
            
            iVis+=1  
        
        writeFile.write('</BODY></HTML>')
        writeFile.close()
        print 'done doPie for: global'
    
    def calcHeteroHomoDesc(self, listMaturePart, titleText):
        
        ratioAllHH={}
        ratioAllHH['all']=0
        ratioAllHH['all (mismatch)'] =0
        ratioHH = []
        ratioList=[]
        for title in titleText:
            ratioList.append(title)
            ratioList.append(str(title) + ' (mismatch)')
        
        
        ratioDict={}
        i=0
        for el in listMaturePart:
            ratioDict[ratioList[i]] = sum(el[0:7])
            i+=1
            ratioDict[ratioList[i]] = sum(el[7:14])
            i+=1
        
        for key, it in ratioDict.iteritems():
            if ' (mismatch)' in key:
                ratioAllHH['all (mismatch)'] += it
            else:
                ratioAllHH['all'] += it
        
        ratioDesc = ''
        for elN in range(0, len(titleText)):
            ratioDesc+= '<b> ' + str(str(titleText[elN]) + ' (isoform content)') + '</b>: '
            if (ratioDict[str(titleText[elN]) + ' (mismatch)']+ratioDict[titleText[elN]]) == 0:
                ratioDesc += 'None'
                ratioHH.append('None')
            else:
                val = (float(ratioDict[str(titleText[elN]) + ' (mismatch)']) / (float(ratioDict[str(titleText[elN]) + ' (mismatch)']+ratioDict[titleText[elN]])) * 100)
                ratioDesc += ' ' + str(round(val, 2)) + '% ' 
                if val >= 0:
                    if val >= 10:
                        ratioDesc+= '(<span class="statDescColor1">' + 'heterogeneous' + '</span>)' 
                        ratioHH.append('heterogeneous')
                    else:
                        ratioDesc+= '(<span class="statDescColor2">' + 'homogeneous' + '</span>)'     
                        ratioHH.append('homogeneous')
                else:
                    
                    ratioHH.append('None')
            ratioDesc += '<br \>'
        
        
        if (ratioAllHH['all (mismatch)']+ratioAllHH['all']) == 0:
            ratioAllHH['allRes'] = 'None'
        else:
            val = (float(ratioAllHH['all (mismatch)']) / (float(ratioAllHH['all (mismatch)']+ratioAllHH['all'])) * 100) 
            if val >= 0:
                if val >= 10:
                    ratioAllHH['allRes'] = 'heterogeneous'
                else:
                    ratioAllHH['allRes'] = 'homogeneous'
            else:
                ratioAllHH['allRes'] = 'None'
         
        return ratioDesc, ratioHH, ratioAllHH['allRes']
        
    def calcRatioDesc(self, listMaturePart, titleText):
     
        ratioList=[]
        for title in titleText:
            ratioList.append(title)
            ratioList.append(str(title) + ' (mismatch)')
                    
        ratioDict={}
        i=0
        for el in listMaturePart:
            ratioDict[ratioList[i]] = sum(el[0:7])
            i+=1
            ratioDict[ratioList[i]] = sum(el[7:14])
            i+=1
            
        
        ratioDesc = ''
        for elN in range(0, len(titleText)):
            ratioDesc+= '<b>ratio ' + str(ratioList[0+elN]) + '/' + str(ratioList[2+elN]) +'</b>: ' + str(ratioDict[ratioList[0+elN]]) +'/' + str(ratioDict[ratioList[2+elN]]) + ' = '
            if ratioDict[ratioList[2+elN]] == 0:
                ratioDesc += 'None'
            else:
                ratioDesc+= str(round(float(ratioDict[ratioList[0+elN]])/float(ratioDict[ratioList[2+elN]]), 2))
            ratioDesc += '<br \>'
            
        
#         ratioDesc = ''
#         if 'star' in ratioDict:
#             if 'mature' in ratioDict:
#                 ratioDesc+= 'ratio mature/star: ' + str(ratioDict['mature']) +'/' + str(ratioDict['star']) + ' = '
#                 if ratioDict['star'] == 0:
#                     ratioDesc+= 'None'
#                 else:
#                     ratioDesc+= str(round(float(ratioDict['mature'])/float(ratioDict['star']), 2))
#         else:
#             ratioDesc+= 'ratio mature/star: ' + str(ratioDict['mature']) +'/' + 'None' + ' = None'
#             
#         ratioDesc+= ' <br \>'
#         
#         if 'starMis' in ratioDict:
#             ratioDesc+= 'ratio mature/star (mismatch): ' + str(ratioDict['matureMis']) +'/' + str(ratioDict['starMis']) + ' = '
#             if ratioDict['starMis'] == 0:
#                 ratioDesc+= 'None'
#             else:
#                 ratioDesc+= str(round(float(ratioDict['matureMis'])/float(ratioDict['starMis']),2))
#         else:
#             ratioDesc+= 'ratio mature/star (mismatch): ' + str(ratioDict['matureMis']) +'/' + 'None' + ' = None'
#             
        return ratioDesc
    
    def duplicates(self, lst, item):
        return [i for i, x in enumerate(lst) if x == item]

    
    def doHistograms(self, plotList, mature, outputHistogram):
        
        
        
        read={}
        for p in mature.keys():
            read[p]={}
            for el in ["5' elongated", "5' truncated", "3' elongated", "3' truncated", 'both elongated', 'both truncated', 'canonical']:
                read[p][el]={}
                for col in ['mature', 'star']:
                    read[p][el][col]={}
                    for fl in ['template-reads', 'non-templated-reads']:
                        read[p][el][col][fl]={}
                        for pL in plotList.keys():
                            read[p][el][col][fl][pL]=None
        
        
        for key0 in mature.keys():
            for pL in plotList.keys():
                for key1 in ['mature', 'star']:
                    if key1 in mature[key0][pL].keys():
                        for key2 in mature[key0][pL][key1].keys():
                            for val in mature[key0][pL][key1][key2]:
                                if key2!= 'values' and key2!= 'non-templated-readsLetterNot' and key2!='non-templated-readsLetter':
                                    read[key0][val][key1][key2][pL] = mature[key0][pL][key1][key2][val]
        
        
        
        for key0 in read.keys():
            hist = vis()
            writeFile = open(outputHistogram +'/' + str(key0)  + '.html', 'w')
            writeFile.write(hist._addLib())
            writeFile.write(hist._addStyle())
            writeFile.write('<HTML><HEAD><link href="https://fonts.googleapis.com/css?family=Roboto+Condensed:300" rel="stylesheet" type="text/css"></HEAD><BODY  onLoad="loadPageHistogram()"  style="font-family: Roboto Condensed;font-size:1.5em"><div id ="plot">')                
            self.visualizateTableHistogram(writeFile, read.keys())
            writeFile.write(hist.addShowHideHistogram())
            writeFile.write(hist.addLoadPageHistogram())
            
            
            writeFile.write('<div class="statistic">')
            writeFile.write('<div class="statisticTitle">' + str(key0) + '</div>')
            writeFile.write('<div style="display:block" id = "containerHistogram_' + str(key0)+ '" class="containerHistogram_' + str(key0)  + '">')
            writeFile.write("""<input type="button" class="but" name='1' id='changestar""" + str(key0)   + """' value='Change ordering for star'  ></input>""")
            writeFile.write("""<input type="button" class="but" name ='1' id='changemature""" + str(key0)   + """' value='Change ordering for mature'></input>""")
            categories=[]
            data=[]
            
            seriesName=[]
            for key1 in read[key0].keys():
                for key2 in read[key0][key1].keys():
                    for key3 in read[key0][key1][key2].keys():
                        dataPart=[]
                        for key4 in read[key0][key1][key2][key3].keys():
                            val = read[key0][key1][key2][key3][key4]
#                         if read[key0][key1][key2][key3]['template-reads']==None:
#                             if read[key0][key1][key2][key3]['non-templated-reads']==None:
#                                 val = None
#                             else:
#                                 val = read[key0][key1][key2][key3]['non-templated-reads']
#                         elif read[key0][key1][key2][key3]['non-templated-reads']==None:
#                             if read[key0][key1][key2][key3]['template-reads']==None:
#                                 val = None
#                             else:
#                                 val = read[key0][key1][key2][key3]['template-reads']
#                         else:
#                             val = read[key0][key1][key2][key3]['template-reads'] + read[key0][key1][key2][key3]['non-templated-reads']
                            dataPart.append(val)
                            if not key4 in categories:
                                categories.append(key4)
                            if not str(key1) + ' ' + str(key2)+ ' ' + str(key3) in seriesName:
                                seriesName.append(str(key1) + ' ' + str(key2)+ ' ' + str(key3))
                        data.append(dataPart)
                        
          
            
            stackingListNames=[]
            for elSeriesName in seriesName:
                if 'mature' in elSeriesName:
                    stackingListNames.append('mature')
                else:
                    stackingListNames.append('star')
            
                  
#             highValDict={}
#             highValDict2={}
#             for elD in range(0, len(data)):
#                 if not stackingListNames[elD] in highValDict:
#                     highValDict[stackingListNames[elD]] = [0 for i in data[elD]]
#                     highValDict2[stackingListNames[elD]] = [0 for i in data[elD]]
#                 data[elD] = [0 if x==None else x for x in data[elD]]
#                 highValDict[stackingListNames[elD]] = [x + y for x, y in zip(highValDict[stackingListNames[elD]], data[elD])]
#             
#             for el, key in highValDict.iteritems():
#                 highValDict2[el] = [i[0] for i in sorted(enumerate(highValDict[el]), key=lambda x:x[1],  reverse = True)]   
            
            
            
            highValDict={}
            highValDict2={}
            
            for elD in range(0, len(data)):
                if not stackingListNames[elD] in highValDict:
                    highValDict[stackingListNames[elD]] = [0 for i in data[elD]]
                    highValDict2[stackingListNames[elD]] = [0 for i in data[elD]]
                data[elD] = [0 if x==None else x for x in data[elD]]
                highValDict[stackingListNames[elD]] = [x + y for x, y in zip(highValDict[stackingListNames[elD]], data[elD])]
            
            duplicats={}
            for key, item in highValDict.iteritems():
                dictTemp = dict((x, self.duplicates(highValDict[key], x)) for x in set(highValDict[key]))
                duplicats[key]={}
                for key1, item1 in dictTemp.iteritems():
                    if len(item1) > 1:
                        duplicats[key][key1] = item1
            
            
            newList={}
            for key, item in highValDict.iteritems():
                if not key in newList:
                    newList[key]={}
                if key == 'mature':
                    keyOp = 'star'
                else:
                    keyOp = 'mature'
                for key1, item1 in duplicats[key].items():
                    for el in highValDict[key]:
                        if el == key1:
                            for it in item1:
                                newList[key][it] = el+highValDict[keyOp][it]
             
            for key, item in highValDict.iteritems():
                for key1, item1 in newList[key].iteritems():
                    highValDict[key][key1] = item1
                    
             
            for el, key in highValDict.iteritems():
                highValDict2[el] = [i[0] for i in sorted(enumerate(highValDict[el]), key=lambda x:x[1],  reverse = True)]   
                        
            
            extraSc2=''
            for sm in ['star', 'mature']:
                extraSc2 +="""\n
                 $('#change""" + str(sm) + str(key0)   + """').click(function(e) {
                 
                 var chart = $('#container_""" + str(key0) + """').highcharts();
                 
                 
                 
                 
                 if(document.getElementById('change""" + str(sm) + str(key0)   + """').name == 1)
                 {
                 document.getElementById('change""" + str(sm) + str(key0)   + """').value = 'Back """ + str(sm) + """ to previous ordering';
                 """
                #chart.xAxis[0].setCategories(""" + str( [x for (y,x) in sorted(zip(highValDict2[sm], categories), reverse = True)]) + """)\n;
                 
                 
                extraSc2 +="""\n chart.xAxis[0].setCategories("""
                 
                catNew=[]
                for elHV in highValDict2[sm]:
                    catNew.append(categories[elHV])
                extraSc2 +="""\n """ + str( catNew ) + """)\n; """ 
                 
                 
                 
                for elN in range(0, len(data)):
                    dataNew=[]
                    for elHV in highValDict2[sm]:
                        dataNew.append(data[elN][elHV])
                    
                    extraSc2 += "try { chart.series[" + str(elN) +"].setData(" + str(dataNew) + "); } catch (e) { alert(e); }\n"
             
                 
                 
#                 for elN in range(0, len(data)):
#                     extraSc2 += "chart.series[" + str(elN) +"].setData(" + str([x for (y,x) in sorted(zip(highValDict2[sm], data[elN]), reverse = True)]) + ");\n"
#                 
                
                extraSc2+="""
                document.getElementById('change""" + str(sm) + str(key0)   + """').name=0;
                }
                else
                {
                
                chart.xAxis[0].setCategories(""" + str(categories) + """)\n;
                 
                """
                
                for elN in range(0, len(data)):
                    extraSc2 += "try { chart.series[" + str(elN) +"].setData(" + str(data[elN]) + "); } catch (e) { alert(e); }\n"
                
                for sm1 in ['star', 'mature']:
                    extraSc2+="""
                    
                    document.getElementById('change""" + str(sm1) + str(key0)   + """').name=1;
                    document.getElementById('change""" + str(sm1) + str(key0)   + """').value = 'Change ordering for """ + str(sm1) + """';
                    
                    """
                
                extraSc2 +="""
              }
             });
             
             """
            
            
#             inx=0
#             for elSn in seriesName:
#                 if 'mature' in elSn:
#                     data[inx] = [el*(-1) for el in data[inx]]
#                 inx +=1
                     
                    
            
            
            writeFile.write(''.join(hist.drawColumnChart(dataY=data,
                  containerName = str(key0),
                  seriesName=seriesName,
                  categories=categories, 
                  xAxisRotation=90,
                  stacking=True,
                  stackingListNames=stackingListNames,
                  yAxisTitle='reads/million [log10]', 
                  axisYType='logarithmic',
                  addOptions='width: 96%; margin: 0 auto;display:block',
                  extraSc2 = extraSc2,
                  sumEl=False
                  )))
            
            writeFile.write('</div>')
            writeFile.write('</div>')  
                
            writeFile.write('</BODY></HTML>')
            writeFile.close()
        
        #self.visualizateTableLegend(writeFile, seriesNameMature)
    
            print 'done doHistogram for: ' + str(key0)
    
    def doExcel(self, outputExcel, sampleRes):
        
        tableResults = {}
        
        heatmapResults={}
        heatmapResults['name']=[]
        heatmapResults['maxVal']=0
        heatmapResults['howMany']=0
        
        heatmapResultsIsomform={}
        heatmapResultsIsomform['name']=[]
        heatmapResultsIsomform['namePrecursor']=[]
        
        import xlsxwriter
        for key0, val0 in sampleRes.items():
            
            if not key0 in tableResults:
                tableResults[key0]=[]
                
                heatmapResults[key0]={}
                heatmapResults[key0][0]=[]
                heatmapResults[key0][1]=[]
    
                heatmapResultsIsomform[key0]={}
                heatmapResultsIsomform[key0][0]=[]
                heatmapResultsIsomform[key0][1]=[]
                
                heatmapResults['howMany'] = len(val0.keys())
                
            
            workbook = xlsxwriter.Workbook(str(outputExcel) + '/' + str(key0) + '.xlsx')
            worksheet = workbook.add_worksheet()
            
            formatAlignCenter = workbook.add_format();
            formatAlignCenter.set_align( 'center' );
            
            formatAlignCenterGreen = workbook.add_format();
            formatAlignCenterGreen.set_align( 'center' );
            formatAlignCenterGreen.set_bg_color( '#007f00' );
            formatAlignCenterGreen.set_color( 'white' );
            
            formatAlignCenterRed = workbook.add_format();
            formatAlignCenterRed.set_align( 'center' );
            formatAlignCenterRed.set_bg_color( 'red' );
            
            formatAlignCenterBlue= workbook.add_format();
            formatAlignCenterBlue.set_align( 'center' );
            formatAlignCenterBlue.set_bg_color( 'blue' );
            
            formatAlignCenterGreen2= workbook.add_format();
            formatAlignCenterGreen2.set_align( 'center' );
            formatAlignCenterGreen2.set_bg_color( '#00cc00' );
            
            formatRotation= workbook.add_format();
            formatRotation.set_rotation(45)
            
            formatRotationGrey= workbook.add_format();
            formatRotationGrey.set_rotation(45)
            formatRotationGrey.set_bg_color( '#D3D3D3' );
            
            formatRotationBold= workbook.add_format();
            formatRotationBold.set_rotation(45)
            formatRotationBold.set_bold();
            
            totalRPM={}
            totalRPM[0]={}
            totalRPM[1]={}
            for el in range(0,2):
                if not el in totalRPM[el]:
                    totalRPM[el][0]=0
                    totalRPM[el][1]=0
            for key2 in sampleRes[key0]:
                for el in range(0,2):
                    val = sum(sampleRes[key0][key2]['values'][el][0:14])
                    if val > 0:
                        totalRPM[el][0] +=1
                    totalRPM[el][1] +=1
               
            
            
            
            row=0
            for key1, val1 in sampleRes[key0].items():
                
                heatmapResultsIsomform['name']=val1['seriesNameMature']
                    
                
                col=1
                if row == 0:
                    worksheet.merge_range(row, col, row, 38, key0, formatAlignCenterGreen)
                    tableResults[key0].append([key0])
                    row+=1
                if row == 1:
                    elList=['3p', '5p']
                    start=0
                    end=0
                    for el in range(0, len(elList)):
                        start =  el + 1 + end
                        end =  16*el +16
                        if el==1:
                            end+=1
                        
#                         print str(start) + ' ' + str(end)
                        format = formatAlignCenterRed
                        if el==1:
                            format = formatAlignCenterBlue
                        worksheet.merge_range(row, start, row, end, elList[el], format)
                        worksheet.write(row, end+1, '', format)
                    
                    
                    worksheet.merge_range(row, 36, row, 38, 'Total', formatAlignCenterGreen2)
                    tableResults[key0].append(['', elList, '', 'Total'])
                    row+=1
                    
#                     worksheet.set_column('D:Q', None, None, {'hidden': 1})
#                     worksheet.set_column('T:AG', None, None, {'hidden': 1})
                    
                if row == 2:
                    tableResultsPart1=[]
                    
                    tableResultsPart1.append('')
                    tableResultsPart1.append('')
                    tableResultsPart1.append('RPM'  + '<br \>' + str(totalRPM[0][0]) + ' / ' + str(totalRPM[0][1]) )
                    tableResultsPart1.append('canonical / non-canonical')
                    
                    worksheet.write(row, col, 'RPM ' + str(totalRPM[0][0]) + ' / ' + str(totalRPM[0][1]) , formatRotationBold)
                    col+=1
                    worksheet.write(row, col, 'canonical / non-canonical', formatRotationBold)
                    col+=1
                    
                    
                    
                    for x in val1['seriesNameMature']:
                        worksheet.write(row, col, x, formatRotationGrey)
                        tableResultsPart1.append(x)
                        col+=1
                    
                    tableResultsPart1.append('Type')
                    worksheet.write(row, col, 'Type', formatRotation)
                    col+=1
                    
                    tableResultsPart1.append('')
                    tableResultsPart1.append('RPM' + '<br \>' +  str(totalRPM[1][0]) + ' / ' + str(totalRPM[1][1]) )
                    tableResultsPart1.append('canonical / non-canonical')    
                        
                    worksheet.write(row, col, 'RPM ' + str(totalRPM[1][0]) + ' / ' + str(totalRPM[1][1]), formatRotationBold)
                    col+=1
                    worksheet.write(row, col, 'canonical / non-canonical', formatRotationBold)
                    col+=1
                    for x in val1['seriesNameMature']:
                        worksheet.write(row, col, x, formatRotationGrey)
                        tableResultsPart1.append(x)
                        col+=1
                    
                    
                    tableResultsPart1.append('Type')
                    worksheet.write(row, col, 'Type', formatRotation)
                    col+=2
                    
                    tableResultsPart1.append('')
                    tableResultsPart1.append('mature/star')
                    tableResultsPart1.append('mature/star (mismatches)')
                    tableResultsPart1.append('canonical / non-canonical')
                    tableResultsPart1.append('Type')
                    
                    
                    
                    worksheet.write(row, col, 'mature/star', formatRotation)
                    col+=1
                    worksheet.write(row, col, 'mature/star (mismatches)', formatRotation)
                    col+=1
                    worksheet.write(row, col, 'canonical / non-canonical', formatRotation)
                    col+=1
                    worksheet.write(row, col, 'Type', formatRotation)
                    row+=1
                    
                    
                    
                    tableResults[key0].append(tableResultsPart1)
                    
                if row >= 3:
                    
                    tableResultsPart3=[]
                    
                    col=3
                    sumNonCanonical1 = 0
                    
                    
                    tableResultsPart3.append(key1)  
                    if not key1 in heatmapResults['name']:
                        heatmapResults['name'].append(key1)
                        heatmapResultsIsomform['namePrecursor'].append(key1)
                    
                    tableResultsPart3.append('X')  
                    worksheet.write(row, col - 3, key1)
                    
                    
                    worksheet.write(row, col-2, sum(val1['values'][0][0:14]))
                    
                    if heatmapResults['maxVal'] < sum(val1['values'][0][0:14]):
                        heatmapResults['maxVal']=sum(val1['values'][0][0:14])
                    
                    heatmapResults[key0][0].append(sum(val1['values'][0][0:14]))
                    heatmapResultsIsomform[key0][0].append(val1['values'][0][0:14])
                    
                    
                    tableResultsPart2=[]
                    i=0
                    for x in val1['values'][0]:
                        if i<13:
                            sumNonCanonical1+=x
                        worksheet.write(row, col, x)
                        tableResultsPart2.append(x)
                        col+=1
                        i+=1
                    col+=1
                    worksheet.write(row, col-1, val1['isoform'][0])
                    col+=1
                    if sumNonCanonical1!=0:
                        tot1=float(val1['values'][0][13])/float(sumNonCanonical1)
                        worksheet.write(row, 2, tot1)
                    else:
                        tot1='None'
                        worksheet.write(row, 2, 'None')
                    col+=1
                    
                    
                    tableResultsPart3.append(sum(val1['values'][0][0:14]))
                    
                    tableResultsPart3.append(tot1)
                    tableResultsPart3.append(tableResultsPart2)
                    
                    tableResultsPart3.append(val1['isoform'][0])
                    tableResultsPart3.append('X') 
                    
                    heatmapResults[key0][1].append(sum(val1['values'][1][0:14]))
                    heatmapResultsIsomform[key0][1].append(val1['values'][1][0:14])
                    
                    if heatmapResults['maxVal'] < sum(val1['values'][1][0:14]):
                        heatmapResults['maxVal']=sum(val1['values'][1][0:14])
                    
                    worksheet.write(row, col-2, sum(val1['values'][1][0:14]))
                    
                    tableResultsPart2=[]
                    sumNonCanonical2 = 0
                    i=0
                    for x in val1['values'][1]:
                        if i<13:
                            sumNonCanonical2+=x
                        worksheet.write(row, col, x)
                        tableResultsPart2.append(x)
                        i+=1
                        col+=1
                    col+=1
                    
                    
                    if sumNonCanonical2!=0:
                        tot2=float(val1['values'][1][13])/float(sumNonCanonical2)
                        worksheet.write(row, 19, tot2)
                    else:
                        tot2='None'
                        worksheet.write(row, 19, 'None')
                    
                    tableResultsPart3.append(sum(val1['values'][1][0:14]))
                    tableResultsPart3.append(tot2)
                    tableResultsPart3.append(tableResultsPart2)
                    
                    worksheet.write(row, col-1, val1['isoform'][1])
                    
                    tableResultsPart3.append(val1['isoform'][1])
                    col+=1
                    
                    
                    tableResultsPart3.append('')
                    
                    totalVal=0
                    for el in range(0, 2):
                        totalVal += sum(val1['values'][el][0:7])
                    worksheet.write(row, col, totalVal)
                    tableResultsPart3.append(totalVal)
                    
                    col+=1
                    totalVal=0
                    for el in range(0, 2):
                        totalVal = sum(val1['values'][0][7:14])
                    worksheet.write(row, col, totalVal)
                    tableResultsPart3.append(totalVal)
                    
                    
                    tot3='aa'
                    col+=1
                    if sumNonCanonical1!=0 or sumNonCanonical2!=0:
                        tot3 = (float(val1['values'][0][13]+val1['values'][1][13])/float(sumNonCanonical1+sumNonCanonical2))
                        
                    else:
                        tot3='None'
                    
                    worksheet.write(row, col, tot3)
                    tableResultsPart3.append(tot3)
                    
                    col+=1
                    worksheet.write(row, col, val1['isoformAll'])
                    tableResultsPart3.append(val1['isoformAll'])
                    
                    
                    
                tableResults[key0].append(tableResultsPart3)
                row+=1
                    
            #print tableResults[key0]    
            
            workbook.close()
        print 'done Excel'
        return tableResults, heatmapResults, heatmapResultsIsomform
    
    
    def printHeatmapResults(self, outputHeatmap, heatmapResults, newFileList):
        
        
        writeFile = open(outputHeatmap +'/' + 'global'  + '.html', 'w')
        writeFile.write('<HTML><HEAD></HEAD><BODY>')
        
        #self.visualizateTableForTable(writeFile, newFileList, heatmapResults['howMany'])
        
        hist1 = vis(height=str(180*heatmapResults['howMany']))
        writeFile.write(hist1._addLib())
        writeFile.write(hist1._addStyle())
        
        writeFile.write('<table class="tab">')
        writeFile.write('<tr>')
        
        data=[]
        kk=[]
        for key0, it0 in  heatmapResults.items():
            if key0 == 'name' or key0 == 'maxVal' or key0=='howMany':
                pass
            else:
                for key1, it1 in it0.items():
                    kk.append(key0)
                    
                    data.append(heatmapResults[key0][key1])
                    writeFile.write('<td>')
        
        writeFile.write(
                    hist1.drawHeatmap(data, 
                                      addOptions='width: 90%; margin: 0;',
                                      categoriesY=heatmapResults['name'],
                                      categories=kk,
                                      xAxisRotation=90,
                                      containerName='container_heatmap_'+str(key0)+str(key1),
                                      #colorAxis=heatmapResults['maxVal'],
                                      getColor=key1
                                     ))
        writeFile.write('</td>')
        writeFile.write('</tr>')
        writeFile.write('</BODY></HTML>')
        
    
    
    def printHeatmapResults2(self, outputHeatmapV2, heatmapResults, newFileList):
        
        
        data=[]
        kk=[]
        
        for key0, it0 in  heatmapResults.items():
            if key0 == 'name' or key0 == 'maxVal' or key0=='howMany':
                pass
            else:
                for key1, it1 in it0.items():
                    kk.append(key0)
                    data.append(heatmapResults[key0][key1])
        
        dataRes=[]
        dataResName=[]
            
        dataResPart=['Data']
        dataResName.append(['Data', 'Data'])
        for d in range(0, len(kk)):
            if d%2==0:
                dataResPart.append(kk[d] + " mature")
            else:
                dataResPart.append(kk[d] + " star")
        dataRes.append(dataResPart)
        
        
        i=0
        for dd in map(list, zip(*data)):
            dataResPart=[]
            dataResPart.append(heatmapResults['name'][i])
            dataResName.append([heatmapResults['name'][i], heatmapResults['name'][i]])
            for d in range(0, len(dd)): 
                if dd[d] >0:
                    dd[d]=round(math.log(dd[d], 2), 2)
                dataResPart.append(dd[d])
            i+=1
            dataRes.append(dataResPart)
        
        
        import inchlib_clust

        #instantiate the Cluster object
        c = inchlib_clust.Cluster()
        
        # read csv data file with specified delimiter, also specify whether there is a header row, the type of the data (numeric/binary) and the string representation of missing/unknown values
        #c.read_csv(filename=outputHeatmap +'/' + "example.csv", delimiter=",", header=True, missing_value=False, datatype="numeric")
        c.read_data(dataRes, header=True, missing_value=False, datatype="numeric") #use read_data() for list of lists instead of a data file
        
        # normalize data to (0,1) scale, but after clustering write the original data to the heatmap
        c.normalize_data(feature_range=(0,1), write_original=bool)
        
        # cluster data according to the parameters
        c.cluster_data(row_distance="euclidean", row_linkage="single", axis="both", column_distance="euclidean", column_linkage="ward")
        
        # instantiate the Dendrogram class with the Cluster instance as an input
        d = inchlib_clust.Dendrogram(c)
        
        
        # create the cluster heatmap representation and define whether you want to compress the data by defining the maximum number of heatmap rows, the resulted value of compressed (merged) rows and whether you want to write the features
        d.create_cluster_heatmap(compress=int, compressed_value="median", write_data=True)
        
        # read metadata file with specified delimiter, also specify whether there is a header row
        #d.add_metadata_from_file(metadata_file=outputHeatmap +'/' + "metadata.csv", delimiter=",", header=True, metadata_compressed_value="frequency")
        d.add_metadata(dataResName, header=True, metadata_compressed_value="median")
        
        # read column metadata file with specified delimiter, also specify whether there is a 'header' column
        #d.add_column_metadata_from_file(column_metadata_file=outputHeatmap +'/' + "file.csv", delimiter=",", header=bool)
        
        # export the cluster heatmap on the standard output or to the file if filename specified
        d.export_cluster_heatmap_as_json(outputHeatmapV2 +'/' +"data.json")
        #d.export_cluster_heatmap_as_html(outputHeatmap +'/' + 'global'  + '.html') #function exports simple HTML page with embedded cluster heatmap and dependencies to given directory
        
        json=''
        with open(str(outputHeatmapV2 +'/' +"data.json"), 'r') as f:
            for line in f:
                json+=line
        
        
       
        writeFile = open(outputHeatmapV2 +'/' + 'global'  + '.html', 'w')
        writeFile.write('<HTML><head>')
        

#       <script src="jquery-2.0.3.min.js"></script>
#          <script src="kinetic-v5.1.0.min.js"></script>
#          <script src="inchlib-1.2.0.js"></script>
#          
   

#draw_row_ids: true,
        writeFile.write("""
         <script src="http://openscreen.cz/software/inchlib/static/js/jquery-2.0.3.min.js"></script>
         <script src="http://openscreen.cz/software/inchlib/static/js/kinetic-v5.1.0.min.js"></script>
         <script src="http://openscreen.cz/software/inchlib/static/js/inchlib-1.2.0.js"></script>
        """)
        
        
        writeFile.write("""
         <script>
        $(document).ready(function() {
            var inchlib = new InCHlib({
                target: "dendrogram",
                dendrogram: true,
                metadata:true,
                column_metadata: false,
                column_dendrogram: true,
                unified_dendrogram_distance: false,
                heatmap_colors: 'RdLrBu',
                independent_columns: false
            });

            inchlib.read_data(""" + str(json) + """);
            inchlib.draw();
            
            
            
        });
        </script>
         
         """)
        writeFile.write('</head>')
        #http://www.ncbi.nlm.nih.gov/pmc/articles/PMC4173117/pdf/13321_2014_Article_44.pdf
        writeFile.write('<body> <div id="dendrogram"></div>')
        writeFile.write('</body>')
        writeFile.write('</HTML>')
        
    
    def calculateHedaerForHeatmap(self, start=0, end=7, allEl=2, prime=2, sumEl=0):
        
        header=''
        
        if allEl==2:
            header += 'mature+stars'
        elif allEl==1:
            header += 'stars'
        elif allEl==0:
            header += 'mature'
            
        if start==0 and end==7:
            header += '-noMismatch'
        if start==7 and end==14:
            header += '-Mismatch'
        if start==0 and end==14:
            header += '-noMismatch + Mismatch'
            
        if prime==0:
            header += "-5prime"
        elif prime==1:
            header += "-3prime"
        else:
            header += "-bothprime"
            
        if sumEl==1:
            header += "-sumData"
        else:
            header += "-allData"
            
        return header
    
    
    
    def calculateDataForHeatmap(self, heatmapResults, start=0, end=7, allEl=2, prime=2, sumEl=0):
        
        #prime=2 - 3prime and 5prime
        #prime=0 - 5prime
        #prime=1 - 3prime
        
        #all=2 - mature + mismatch
        #all=1 - star
        #all=0 - mature
        
        
#         print heatmapResults
       
        
        dataRes={}
        dataRes['res']=[]
        dataRes['metadata']=[]
        
        dataResFinal={}
        dataResFinal['res']=[]
        dataResFinal['metadata']=[]
        
        
        matN=['mature', 'stars']
        if allEl==2:
            mat=[0,1]
        elif allEl==1:
            mat=[1]
        elif allEl==0:
            mat=[0]
        
        heatmapResultsNameVal=[]
        prime =1
        if prime==2:
            heatmapResultsName = heatmapResults['name']
        else:
            if prime == 0:
                otherPrime = "3'"
            elif prime ==1:
                otherPrime = "5'"
            heatmapResultsName=[]
            for elNum in range(0, len(heatmapResults['name'])):
                if otherPrime not in heatmapResults['name'][elNum]:
                    heatmapResultsName.append(heatmapResults['name'][elNum])
                    heatmapResultsNameVal.append(elNum)
            
#         print heatmapResultsNameVal
#         print allEl
#         print start
#         print end

        allListR = [i for i in range(0, 14) if i not in range(start, end)]
        
 
        for elN in allListR:
            if elN in heatmapResultsNameVal:
                heatmapResultsNameVal.remove(elN)
            
#         print heatmapResultsNameVal
        
        dataResEl={}
        for pr in heatmapResults['namePrecursor']:
            dataResEl[pr]={}
            for nn in heatmapResultsName:
                dataResEl[pr][nn]={}
                for nnH in matN:
                    dataResEl[pr][nn][nnH]=[]
                    dataResEl[pr][nn]['name']=[]
                for nnH in heatmapResults.keys():
                    if nnH !=  'name' and nnH != 'namePrecursor':
                        dataResEl[pr][nn]['name'].append(nnH)
        
        
#         print dataResEl
        
        for key1, it1 in heatmapResults.iteritems():
            if key1 != 'name' and key1 != 'namePrecursor':
                elNum1=0
                for key2, it2 in it1.iteritems():
                    for elNum in range(0, len(it2)):
                        #tL = [el if el!=0 else 0 for el in it2[elNum][start:end]]
                        for elN in heatmapResultsNameVal:
                            if key2 in mat:
#                                 print str(heatmapResults['namePrecursor'][elNum])
#                                 print heatmapResults['name'][elN]
#                                 print str(key2) 
#                                 print mat
#                                 print matN[key2]
#                                 
#                                 print str(elN) 
#                                 print it2[elNum][elN]
                                val=0
                                if it2[elNum][elN]!=0:
                                    val = round(math.log(it2[elNum][elN], 2),2)
                                dataResEl[heatmapResults['namePrecursor'][elNum]][heatmapResults['name'][elN]][matN[key2]].append(val)
                            
                    elNum1 +=1
        
#         print dataResEl
        
        #remove rows with sum = 0
        iVal=0
        sumLineTF=False
        for key1, it1 in dataResEl.iteritems():
            for key2, it2 in it1.iteritems():
                for key3, it3 in it2.iteritems():
                    if iVal == 0:
                        dataRes['res'].append(['Data'] + it2['name'])
                        dataRes['metadata'].append(['Data', 'Data'])
                    if key3 != 'name':
                        line=[]
                        if len(it3) != 0:
                            line.append(str(key1) + ' ' + str(key2) + ' ' + str(key3))
                            sumLine=0
                            for el in it3:
                                line.append(el)
                                sumLine+=el
                            if sumLineTF == False:
                                line1=line
                                sumLineTF=True
                            if sumLine != 0:
                                
                                dataRes['res'].append(line)
                                dataRes['metadata'].append([str(key1) + ' ' + str(key2) + ' ' + str(key3), str(key1) + ' ' + str(key2) + ' ' + str(key3)])
                                
                    iVal+=1
        
        
        # take 100 the best scores for each row
        num=100
        inxList=[dataRes['res'][0]]
        for elCol in range(1, len(dataRes['res'][1:][0])):
            #print sorted(dataRes['res'][1:], key=operator.itemgetter(elCol), reverse=True)
            indXColTemp = sorted(dataRes['res'][1:], key=operator.itemgetter(elCol), reverse=True)
            indXCol=[]
            for el in indXColTemp[0:num]:
                if el[elCol] != 0:
                    indXCol.append(el)
            inxList += indXCol
                
        
       
        #remove duplicates
        b = list()
        for sublist in inxList:
            if sublist not in b:
                b.append(sublist)
        
        inxList=b
       
        dataResFinal['res'] = inxList
        dataResFinal['metadata'].append(['Data', 'Data'])
        for elN in range(1, len(inxList)):
            dataResFinal['metadata'].append([inxList[elN][0], inxList[elN][0]])
        
       
        if len(dataResFinal['metadata']) == 2:
            dataResFinal['metadata'].append([line1[0], line1[0]])
            dataResFinal['res'].append(line1)
        
        
        
        return dataResFinal
    
    def calculateDataForHeatmapCopy(self, heatmapResults, start=0, end=7, allEl=2, prime=2, sumEl=0):
        
        #prime=2 - 3prime and 5prime
        #prime=0 - 5prime
        #prime=1 - 3prime
        
        #all=2 - mature + mismatch
        #all=1 - star
        #all=0 - mature
        
        print heatmapResults
        
        dataRes={}
        dataRes['res']=[]
        dataRes['metadata']=[]
        
        if prime !=2:
            if prime == 0:
                otherPrime = "3'"
            elif prime ==1:
                otherPrime = "5'"
            indxList=[]
            tempList=['Data']
            for elNum in range(0, len(heatmapResults['name'][start:end])):
                if otherPrime not in heatmapResults['name'][start:end][elNum]:
                    indxList.append(elNum)
                    tempList.append(heatmapResults['name'][start:end][elNum])
            
            if sumEl == 1:
                dataRes['res'].append(['Data', 'Sum'])
            else:
                dataRes['res'].append(tempList)
        else:
            if sumEl == 1:
                dataRes['res'].append(['Data', 'Sum'])
            else:
                dataRes['res'].append(['Data'] + heatmapResults['name'][start:end])   
        
        
        oneMoreForClustering=[]
        oneMoreForClusteringTF=False
        dataRes['metadata'].append(['Data', 'Data'])
        for key1, it1 in heatmapResults.iteritems():
            if key1 != 'name' and key1 != 'namePrecursor':
                for key2, it2 in it1.iteritems():
                    
                    if allEl==2:
                        if key2 == 0:
                            name = ' mature'
                        else:
                            name = ' star'
                            
                        
                        for elNum in range(0, len(it2)):
                            if prime==2:
                                
                                tL = [round(math.log(el, 2),2) if el!=0 else 0 for el in it2[elNum][start:end]]
                                
                                if sum(tL)!=0:
                                    if sumEl == 1:
                                        dataRes['res'].append([key1 + name + ' ' + heatmapResults['namePrecursor'][elNum], sum(tL[0:len(tL)])])
                                        dataRes['metadata'].append([key1 + name + ' ' + heatmapResults['namePrecursor'][elNum], key1 + name + ' ' + heatmapResults['namePrecursor'][elNum]])
                                    else:
                                       
                                        tlS = [key1 + name + ' ' + heatmapResults['namePrecursor'][elNum]]
                                        dataRes['res'].append(tlS + tL)
                                        dataRes['metadata'].append([key1 + name + ' ' + heatmapResults['namePrecursor'][elNum], key1 + ' ' + heatmapResults['namePrecursor'][elNum]])
                                    
                                    dataRes['metadata'].append([key1 + name + ' ' + heatmapResults['namePrecursor'][elNum], key1 + name + ' ' + heatmapResults['namePrecursor'][elNum]])
                                else:
                                    if oneMoreForClusteringTF==False:
                                        oneMoreForClustering.append(key1 + name + ' ' + heatmapResults['namePrecursor'][elNum])
                                        oneMoreForClusteringTF=True
                                
                            else:
                                
                                tL=[]
                                for en in range(0, len(it2[elNum][start:end])):
                                    if en in indxList:
                                        if it2[elNum][start:end][en] !=0:
                                            tL.append(round(math.log(it2[elNum][start:end][en], 2), 2))
                                        else:
                                            tL.append(0)
                                
                                if sum(tL)!=0:     
                                
                                    if sumEl == 1:
                                        dataRes['res'].append([key1 + name + ' ' + heatmapResults['namePrecursor'][elNum], sum(tL[0:len(tL)])])
                                        dataRes['metadata'].append([key1 + name + ' ' + heatmapResults['namePrecursor'][elNum], key1 + ' ' + heatmapResults['namePrecursor'][elNum]])
                                    else:
                                        tlS = [key1 + name + ' ' + heatmapResults['namePrecursor'][elNum]]
                                        dataRes['res'].append(tlS + tL)
                                        dataRes['metadata'].append([key1 + name + ' ' + heatmapResults['namePrecursor'][elNum], key1 + ' ' + heatmapResults['namePrecursor'][elNum]])
                                    
                                    dataRes['metadata'].append([key1 + name + ' ' + heatmapResults['namePrecursor'][elNum], key1 + name + ' ' + heatmapResults['namePrecursor'][elNum]])
                                else:
                                    if oneMoreForClusteringTF==False:
                                        oneMoreForClustering.append(key1 + name + ' ' + heatmapResults['namePrecursor'][elNum])
                                        oneMoreForClusteringTF=True

                    elif key2 == allEl:
                        
                        for elNum in range(0, len(it2)):
                            if prime==2:
                                
                                
                                tL = [round(math.log(el, 2), 2) if el!=0 else 0 for el in it2[elNum][start:end]]
                                
                                if sum(tL)!=0:
                                    if sumEl == 1:
                                        dataRes['res'].append([key1 + ' ' + heatmapResults['namePrecursor'][elNum], sum(tL[0:len(tL)])])
                                        dataRes['metadata'].append([key1 + ' ' + heatmapResults['namePrecursor'][elNum], key1 + ' ' + heatmapResults['namePrecursor'][elNum]])
                                    else:
                                        
                                        tlS = [key1 + ' ' + heatmapResults['namePrecursor'][elNum]]
                                        dataRes['res'].append(tlS + tL)
                                        dataRes['metadata'].append([key1 + ' ' + heatmapResults['namePrecursor'][elNum], key1 + ' ' + heatmapResults['namePrecursor'][elNum]])
                                else:
                                    if oneMoreForClusteringTF==False:
                                        oneMoreForClustering.append(key1 + ' ' + heatmapResults['namePrecursor'][elNum])
                                        oneMoreForClusteringTF=True
                            else:
                               
                                #if indxList and elNum in indxList
                                tL=[]
                                for en in range(0, len(it2[elNum][start:end])):
                                    if en in indxList:
                                        if it2[elNum][start:end][en]!=0:
                                            tL.append(round(math.log(it2[elNum][start:end][en], 2), 2))
                                        else:
                                            tL.append(0)
   
                                if sum(tL)!=0:
                                    if sumEl == 1:
                                        dataRes['res'].append([key1 + ' ' + heatmapResults['namePrecursor'][elNum], sum(tL[0:len(tL)])])
                                        dataRes['metadata'].append([key1 + ' ' + heatmapResults['namePrecursor'][elNum], key1 + ' ' + heatmapResults['namePrecursor'][elNum]])
                                    else:
                                        tlS = [key1 + ' ' + heatmapResults['namePrecursor'][elNum]]
                                        dataRes['res'].append(tlS + tL)
                                        dataRes['metadata'].append([key1 + ' ' + heatmapResults['namePrecursor'][elNum], key1 + ' ' + heatmapResults['namePrecursor'][elNum]])
                                else:
                                    if oneMoreForClusteringTF==False:
                                        oneMoreForClustering.append(key1 + ' ' + heatmapResults['namePrecursor'][elNum])
                                        oneMoreForClusteringTF=True
        if len(dataRes['res']) == 2:
            dataRes['res'].append([oneMoreForClustering[0]] + [0 for el in range(0, len(dataRes['res'][1])-1)])
            dataRes['metadata'].append([oneMoreForClustering[0], oneMoreForClustering[0]])
        
       
        return dataRes
     
    def printHeatmapResults4(self, outputHeatmapV2, heatmapResults, newFileList):
        
        
        with open('results/tempData/outputHeatmapV2.pkl','wb') as fp:
            pickle.dump(outputHeatmapV2,fp)  
        with open('results/tempData/outputHeatmapV2.pkl','rb') as fp:
            outputHeatmapV2=pickle.load(fp)
            
        with open('results/tempData/newFileList.pkl','wb') as fp:
            pickle.dump(newFileList,fp)  
        with open('results/tempData/newFileList.pkl','rb') as fp:
            newFileList=pickle.load(fp)
            
        with open('results/tempData/heatmapResults.pkl','wb') as fp:
            pickle.dump(heatmapResults,fp)  
        with open('results/tempData/heatmapResults.pkl','rb') as fp:
            heatmapResults=pickle.load(fp)
            
        
        
        i=0
        possibilityList= []
        for st in [0, 7]:
            for en in [7, 14]:
                for allEl in [0,1,2]:
                    for prime in [0, 1, 2]:
                        #for elSum in [0, 1]:
                        if st !=en:
                            possibilityList.append([st, en, allEl, prime, 0])
                            i+=1
        
        
        import inchlib_clust
        for el in possibilityList:
            
            
            fileName  = self.calculateHedaerForHeatmap(start=el[0], end=el[1], allEl=el[2], prime=el[3], sumEl=el[4])
            print fileName
            dataRes = self.calculateDataForHeatmap(heatmapResults, start=el[0], end=el[1], allEl=el[2], prime=el[3], sumEl=el[4])
            
            c = inchlib_clust.Cluster()
            c.read_data(dataRes['res'], header=True, missing_value=False, datatype="numeric") #use read_data() for list of lists instead of a data file
            c.normalize_data(feature_range=(0,1), write_original=bool)
            c.cluster_data(row_distance="euclidean", row_linkage="average", axis="both", column_distance="euclidean", column_linkage="average")
            d = inchlib_clust.Dendrogram(c)
            d.create_cluster_heatmap(compress=int, compressed_value="median", write_data=True)
            d.add_metadata(dataRes['metadata'], header=True, metadata_compressed_value="median")
            d.export_cluster_heatmap_as_json(outputHeatmapV2 +'/' +"data.json")
            
            json=''
            with open(str(outputHeatmapV2 +'/' +"data.json"), 'r') as f:
                for line in f:
                    json+=line
            
            
           
            writeFile = open(outputHeatmapV2 +'/' + str(fileName)  + '.html', 'w')
            writeFile.write('<HTML><head>')
            
    
            writeFile.write("""
             <script src="http://openscreen.cz/software/inchlib/static/js/jquery-2.0.3.min.js"></script>
             <script src="http://openscreen.cz/software/inchlib/static/js/kinetic-v5.1.0.min.js"></script>
             <script src="http://openscreen.cz/software/inchlib/static/js/inchlib-1.2.0.js"></script>
            """)
            
            
            writeFile.write("""
             <script>
            $(document).ready(function() {
                var inchlib = new InCHlib({
                    target: "dendrogram",
                    dendrogram: true,
                    metadata:true,
                    column_metadata: false,
                    column_dendrogram: true,
                    unified_dendrogram_distance: false,
                    heatmap_colors: 'RdLrBu',
                    independent_columns: false
                });
    
                inchlib.read_data(""" + str(json) + """);
                inchlib.draw();
                
                
                
            });
            </script>
             
             """)
            writeFile.write('</head>')
            #http://www.ncbi.nlm.nih.gov/pmc/articles/PMC4173117/pdf/13321_2014_Article_44.pdf
            writeFile.write('<body> <div id="dendrogram"></div>')
            writeFile.write('</body>')
            writeFile.write('</HTML>')
    
    def printHeatmapResults3(self, outputHeatmapV2, heatmapResultsT, newFileList):
        
        heatmapResults={}
        
        inX=0
        for key1, it1 in heatmapResultsT.items():
            if inX ==0:
                heatmapResults['name'] = it1.keys() 
            heatmapResults[key1] = {}
            heatmapResults[key1][0]=[]
            heatmapResults[key1][1]=[]
            for key2, it2 in it1.items():
                if len(it2) == 2:
                    for key3, it3 in it2.items():
                        heatmapResults[key1][key3].append(it3)
                else:
                    if len(it2) == 0:
                        for elN in range(0,2):
                            heatmapResults[key1][elN].append(0)

        
        data=[]
        kk=[]
        
        for key0, it0 in  heatmapResults.items():
            if key0 == 'name' or key0 == 'maxVal' or key0=='howMany':
                pass
            else:
                for key1, it1 in it0.items():
                    kk.append(key0)
                    data.append(heatmapResults[key0][key1])
        
        dataRes=[]
        dataResName=[]
            
        dataResPart=['Data']
        dataResName.append(['Data', 'Data'])
        for d in range(0, len(kk)):
            if d%2==0:
                dataResPart.append(kk[d] + " mature ")
            else:
                dataResPart.append(kk[d] + " star ")
        dataRes.append(dataResPart)
        
        
        i=0
        for dd in map(list, zip(*data)):
            dataResPart=[]
            dataResPart.append(heatmapResults['name'][i])
            dataResName.append([heatmapResults['name'][i], heatmapResults['name'][i]])
            for d in range(0, len(dd)): 
                if dd[d] >0:
                    dd[d]=round(math.log(dd[d], 2), 2)
                dataResPart.append(dd[d])
            i+=1
            dataRes.append(dataResPart)
        
        
        import inchlib_clust

        #instantiate the Cluster object
        c = inchlib_clust.Cluster()
        
        # read csv data file with specified delimiter, also specify whether there is a header row, the type of the data (numeric/binary) and the string representation of missing/unknown values
        #c.read_csv(filename=outputHeatmap +'/' + "example.csv", delimiter=",", header=True, missing_value=False, datatype="numeric")
        c.read_data(dataRes, header=True, missing_value=False, datatype="numeric") #use read_data() for list of lists instead of a data file
        
        # normalize data to (0,1) scale, but after clustering write the original data to the heatmap
        c.normalize_data(feature_range=(0,1), write_original=bool)
        
        # cluster data according to the parameters
        c.cluster_data(row_distance="euclidean", row_linkage="single", axis="both", column_distance="euclidean", column_linkage="ward")
        
        # instantiate the Dendrogram class with the Cluster instance as an input
        d = inchlib_clust.Dendrogram(c)
        
        
        # create the cluster heatmap representation and define whether you want to compress the data by defining the maximum number of heatmap rows, the resulted value of compressed (merged) rows and whether you want to write the features
        d.create_cluster_heatmap(compress=int, compressed_value="median", write_data=True)
        
        # read metadata file with specified delimiter, also specify whether there is a header row
        #d.add_metadata_from_file(metadata_file=outputHeatmap +'/' + "metadata.csv", delimiter=",", header=True, metadata_compressed_value="frequency")
        d.add_metadata(dataResName, header=True, metadata_compressed_value="median")
        
        # read column metadata file with specified delimiter, also specify whether there is a 'header' column
        #d.add_column_metadata_from_file(column_metadata_file=outputHeatmap +'/' + "file.csv", delimiter=",", header=bool)
        
        # export the cluster heatmap on the standard output or to the file if filename specified
        d.export_cluster_heatmap_as_json(outputHeatmapV2 +'/' +"data.json")
        #d.export_cluster_heatmap_as_html(outputHeatmap +'/' + 'global'  + '.html') #function exports simple HTML page with embedded cluster heatmap and dependencies to given directory
        
        json=''
        with open(str(outputHeatmapV2 +'/' +"data.json"), 'r') as f:
            for line in f:
                json+=line
        
        
       
        writeFile = open(outputHeatmapV2 +'/' + 'global'  + '.html', 'w')
        writeFile.write('<HTML><head>')
        

#       <script src="jquery-2.0.3.min.js"></script>
#          <script src="kinetic-v5.1.0.min.js"></script>
#          <script src="inchlib-1.2.0.js"></script>
#          
   

#draw_row_ids: true,
        writeFile.write("""
         <script src="http://openscreen.cz/software/inchlib/static/js/jquery-2.0.3.min.js"></script>
         <script src="http://openscreen.cz/software/inchlib/static/js/kinetic-v5.1.0.min.js"></script>
         <script src="http://openscreen.cz/software/inchlib/static/js/inchlib-1.2.0.js"></script>
        """)
        
        
        writeFile.write("""
         <script>
        $(document).ready(function() {
            var inchlib = new InCHlib({
                target: "dendrogram",
                dendrogram: true,
                metadata:true,
                column_metadata: false,
                column_dendrogram: true,
                unified_dendrogram_distance: false,
                heatmap_colors: 'RdLrBu',
                independent_columns: false
            });

            inchlib.read_data(""" + str(json) + """);
            inchlib.draw();
            
            
            
        });
        </script>
         
         """)
        writeFile.write('</head>')
        #http://www.ncbi.nlm.nih.gov/pmc/articles/PMC4173117/pdf/13321_2014_Article_44.pdf
        writeFile.write('<body> <div id="dendrogram"></div>')
        writeFile.write('</body>')
        writeFile.write('</HTML>')
    
    def printTableResults(self, outputTable, tableResults, newFileList):
        
        
        writeFile = open(outputTable +'/' + 'global'  + '.html', 'w')
        writeFile.write('<HTML><HEAD>')
        
        
        writeFile.write(""" 
         <script src="http://www.kryogenix.org/code/browser/sorttable/sorttable.js" type="text/javascript"></script> 
        """)
        
        writeFile.write('<link href="https://fonts.googleapis.com/css?family=Roboto+Condensed:300" rel="stylesheet" type="text/css"></HEAD><BODY  onLoad="loadTable()" style="font-family: Roboto Condensed;font-size:1.5em">')
        
        writeFile.write("""
        <style>
        .sortable {
            display: table;
            width: 100%; 
            background: #fff;
            margin: 0;
            box-sizing: border-box;
        }
        .sortable1 {
            display: table;
            width: 100%; 
            background: #fff;
            margin: 0;
            box-sizing: border-box;
        }
        .sortable1 .th  {
            background-color: #31BC86;
            font-weight: bold;
            color: #FFF;
            white-space: nowrap;
            
        }
        .sortable1 th, .sortable1 td {
            padding: 0.50em 1.0em;
            text-align: left;
            border:  1px dotted #010101;
            text-align:left;
            background-color: #31BC86;
        }
        
        .tableDiv{
            float:left;
        }
        .sortable th  {
            padding: 0.50em 1.0em;
            border:  1px dotted #010101;
            text-align:center;
            background-color:#efefef;
        }
        .sortable td {
            padding: 0.50em 1.0em;
            text-align: left;
            border:  1px dotted #010101;
        }
        
        .tab td{
        }
        
        
        </style>""")
        
        self.visualizateTableForTable(writeFile, newFileList)
        
        
        writeFile.write("""
        <script>   
        
        
        
        function loadTable() 
        {   
            document.getElementById("data").checked = false;
            
            var chboxs = document.getElementsByName("fileList");
            
            var j=0;
            for(var i=0;i<chboxs.length;i++) { 
            chboxs[i].checked = false;
            }    
            
        }    
        </script>
    
        <script>
        
        function showMe(box)
        {
            
             var chboxs = document.getElementsByName("fileList");
             
            
            for(var i=0;i<chboxs.length;i++) {
                
            
             
                if(chboxs[i].checked){
                    
                 newBox='';
                 newBox = newBox.concat('table_', chboxs[i].value);
                 document.getElementById(newBox).style.display = "block";
                }
                else
                {
                newBox='';
                 newBox = newBox.concat('table_', chboxs[i].value);
                 document.getElementById(newBox).style.display = "none";
                
                }
                }
          
                

            }
            
            
        function check(howMany)
        {
            
            var oRows = document.getElementById('tablesResults').getElementsByTagName('tr');
            var iRowCount = oRows.length;
            
            
            var chboxs = document.getElementsByName("fileList");
            for(var i=0;i<chboxs.length;i++) 
            {
              for(var col=0; col<28*(iRowCount); col++)
              {
                  //console.log(chboxs[i].value);
                  newBox1=''
                  newBox1 = newBox1.concat( chboxs[i].value, 'AA', col);
                  
                  if (document.getElementById(newBox1)!=null)
                  {
                      if(document.getElementById(newBox1).style.display == "table-cell")
                      {
                       document.getElementById(newBox1).style.display = "none";
                       }
                      else
                      {
                       document.getElementById(newBox1).style.display = "table-cell";
                       }
                    }
              }
            
            }
          
          
        
        }
        
        </script>""")
        
        
        
#         hist1 = vis(height=str(120*heatmapResults['howMany']))
#         writeFile.write(hist1._addLib())
#         writeFile.write(hist1._addStyle())
        
        writeFile.write('<table class="tab">')
        writeFile.write('<tr>')
        for key0, val0 in tableResults.items():
            writeFile.write('<td>')
            i=0
            
            writeFile.write('<div id="table_' + str(key0) +'" style="display:none" >')
            writeFile.write('<table class="sortable1">')
            tableTF=False
#             heatmapTF=True
            
            
            ll=0
            llk=0
            for val1 in tableResults[key0]:
                k=0
                
                j=10
                addColspan=''
                if i==0:
                    addColspan = 'colspan = "37"'
                elif i==1:
                    j=0
                
                writeFile.write('<tr >')
                for val2 in val1:
                    
                    if(type(val2) is list):
                        
                        
                        
                        for val3 in val2:
                            if j==1 or j==2:
                                addColspan = ' colspan="16" '
                            elif i==0:
                                addColspan = 'colspan = "37"'
                            else:
                                addColspan = ''
                                
                            
                            #print str(i) + ' ' + str(j) + ' ' + str(k) +  ' - ' + str(val2)
                            if val3!='X':
                                if i>=3:
                                    writeFile.write('<td  id = "' + str(key0) + 'AA' + str(llk+ll)  + '" style = "display:none;" > ')
                                    llk+=1
                                    
                                else:
                                    if i==1:
                                        pass
                                    else:
                                        writeFile.write('<td ')
                            
                                
                                #str(addColspan) + '> '  + str(i) + " " + str(j) + " " + str(k) + "<br />" 
                                if i==1:
                                    pass
                                else:
                                    #print str(i) + ' ' + str(j) + ' ' + str(k) +  ' - ' + str(val3)
                                    writeFile.write(str(val3))
                                    writeFile.write('</td>\n')
                                
                                
                                
                            j+=1
                        j+=1
                    else:
                        if j==5:
                            #addColspan = 'colspan = "3"'
                            addColspan = ' width="380px" '
                        elif i==0:
                                addColspan = 'colspan = "37"'
                        else:
                            addColspan = ''
                        
                        if i==2:
                            if tableTF == False:
                                writeFile.write('</table>')
                                writeFile.write('<table id="tablesResults" class="sortable">')
                                tableTF+=True
                            
                            
                            if k==1 or k==19:
                                pass
#                                 writeFile.write('<th  class="sorttable_nosort" >')
                            elif j>=14 and j<=27 :
                                writeFile.write('<th id = "' + str(key0) + 'AA' + str(ll)  + '" style = "display:none; background-color:red; padding: 0.50em 1.0e; border:  1px dotted #010101;" >\n')
                                ll+=1
                            elif j>=32 and j<=45 :
                                writeFile.write('<th id = "' + str(key0) + 'AA' + str(ll)  + '" style = "display:none; background-color:blue; padding: 0.50em 1.0e; border:  1px dotted #010101;" >\n')
                                ll+=1
                            else:
                                writeFile.write('<th ' + str(addColspan) + '> \n')
                        else:
                            
                            
                            
                            if k==1 or k==6:
                                
                                if k==1:
#                                     data= heatmapResults[key0][0]
                                    if i==3:
                                        pass
#                                         writeFile.write('<td class="sorttable_nosort"  rowspan="' + str(heatmapResults['howMany']) + '">')
                                  
#                                         writeFile.write(
#                                                     hist1.drawHeatmap(data, 
#                                                                       addOptions='width: 16%; margin: 0;',
#                                                                       categoriesY=heatmapResults['name'],
#                                                                       categories=['HSA'],
#                                                                       containerName='container_heatmap_'+str(key0)+str(k),
#                                                                       colorAxis=heatmapResults['maxVal'],
#                                                                       getColor=0
#                                                                      ))
#                                         writeFile.write('</td>')
                                if k==6:
#                                     data = heatmapResults[key0][1]
                                    if i==3:
                                        pass
#                                         writeFile.write('<td  class="sorttable_nosort" rowspan="' + str(heatmapResults['howMany']) + '">')
                                   
#                                         writeFile.write(
#                                                     hist1.drawHeatmap(data, 
#                                                                       addOptions='width: 16%; margin: 0;',
#                                                                       categoriesY=heatmapResults['name'],
#                                                                       categories=['HSA'],
#                                                                       containerName='container_heatmap_'+str(key0)+str(k),
#                                                                       colorAxis=heatmapResults['maxVal'],
#                                                                       getColor=3
#                                                                     ))
#                                         writeFile.write('</td>')
                                
                            else:    
                                
                                if i==1:
                                    pass
                                else:
                                    writeFile.write('<td ' + str(addColspan) + '> ')
                                
                        if k==1 or k==6:
                            if i==3:
                                pass
                            if k==6 and val2!='X':
                                writeFile.write(str(val2))
                        else:
                            if val2=='X':
                                print k
                            
                            if i!=1:
                                writeFile.write(str(val2))
                        
                        
                        if i==2:
                            writeFile.write('</th>\n')
                        else:
                            if k==1 or k==6:
                                if i==3:
                                    pass
                            else:
                                if i==1:
                                    pass
                                else:
                                    writeFile.write('</td>\n')    
                        
                        j+=1
                    k+=1
                writeFile.write('</tr >\n')
                
                i+=1
            writeFile.write('</div>')
            
            writeFile.write('</table>')
            writeFile.write('</td>')
          
        writeFile.write('</tr>')
        writeFile.write('</table>')
        
        
        writeFile.write('</BODY></HTML>')
        
            
        print 'done printed Results'
    
    def calcRes(self, outputResults, outputPie, outputHistogram, outputExcel, outputTable, outputHeatmapV3):
        
        print 'start'
        start_time = time.time()
          
        fileTotal = self.readFilesPre(os.listdir(self._folderFileList))
        fileList = fileTotal.keys()
          
        newFileList =[]
        for fL in fileList:
            newFileList.append(fL.split('.')[0])
          
        fileMatureList = os.listdir(self._matureFile)
        mature = self.readFileMatures(fileMatureList, newFileList)
        filePrecList = os.listdir(self._precursorFile)
        precursor, precursorDict, readsDict = self.readFile( filePrecList)
        samFiles = self.readFiles(fileList,  mature, readsDict, fileTotal)
          
          
        self.calcValues(precursor, samFiles)
        precursor=[]
        samFiles=[]
          
        newcombinationsFileList=[]
        elList=[]
        for el in newFileList:
            newcombinationsFileList.append([el])
            elList.append(el)
        newcombinationsFileList.append(elList)        
          
        colorDictRes = self.getColorList(newFileList)
          
          
        with open('results/tempData/letterDict.pkl','rb') as fp:
            letterDict=pickle.load(fp)
              
        with open('results/tempData/precursor.pkl','rb') as fp:
            precursor=pickle.load(fp)
              
        plotList, heatmapResultsV3 = self.visualizateResults(precursor, outputResults, letterDict, newcombinationsFileList, newFileList, mature, precursorDict, colorDictRes, readsDict)
          
          
        precursor=[]
          
        #sampleRes = self.doSeries(plotList, newcombinationsFileList, newFileList, mature, letterDict, outputResults, precursorDict, colorDictRes, readsDict)
          
        precursorDict=[]
        readsDict=[]
        letterDict=[]
        colorDictRes=[]
          
        #globalPie
        self.doPie(plotList, mature, outputPie, fileTotal)
          
        fileTotal=[]
          
        #globalHistograms
        self.doHistograms(plotList, mature, outputHistogram)
        mature=[]
          
        with open('results/tempData/sampleRes.pkl','rb') as fp:
            sampleRes=pickle.load(fp)
              
        tableResults, heatmapResults, heatmapResultsIsomform = self.doExcel(outputExcel, sampleRes)
        sampleRes=[]
            
        self.printTableResults(outputTable, tableResults, newFileList)
        #self.printHeatmapResults(outputHeatmapV1, heatmapResults, newFileList)
          
        #mature/stars
#         heatmapResultsIsomform=[]
#         newFileList=[]
        self.printHeatmapResults4(outputHeatmapV3, heatmapResultsIsomform, newFileList)
        
        
        #newone
        #self.printHeatmapResults2(outputHeatmapV1, heatmapResults, newFileList)
        #self.printHeatmapResults3(outputHeatmapV2, heatmapResultsV3, newFileList)
        
        elapsed_time = time.time() - start_time
        print 'Calculation time: ' + str(elapsed_time)
    