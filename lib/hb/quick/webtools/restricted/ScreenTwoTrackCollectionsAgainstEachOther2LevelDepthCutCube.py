from proto.hyperbrowser.HtmlCore import HtmlCore

'''
Created on 

@author: Diana
'''

FIELD_NAME1 = 'folder-value 0 of first GSuite' #genome
FIELD_NAME2 = 'folder-value 1 of first GSuite' #2 - level depth gSuite
FIELD_NAME3 = 'folder-value 2 of first GSuite' #2 - level depth gSuite
FIELD_NAME4 = 'folder-value 1 of second GSuite' #2 - level depth gSuite

def calculateFor111(results, folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, statIndex, fV1):
    partTransposedProcessedResults=[]
    for dataDetail1 in results:
        for dataDetail2 in dataDetail1['dataFolderValue1']:
            partRes=[]
            partRes.append(dataDetail2['targetTrackName'])
            partRes.append(dataDetail2['folderName2'])
            partRes.append(dataDetail1['folderName1'])
            for dataDetail3 in dataDetail2['dataFolderValue2']:
                if dataDetail3['refTrackName'] == feature:
                    partRes.append(dataDetail3['data'][statIndex])
                    
            partTransposedProcessedResults.append(partRes)
    return partTransposedProcessedResults

def calculateForFeatureFolderName2Dim1(results, folderValue2Unique, statIndex, feature):
    partTransposedProcessedResults=[]
    for dataDetail1 in results:
        for dataDetail2 in dataDetail1['dataFolderValue1']:
            partRes=[]
            partRes.append(dataDetail2['targetTrackName'])
            partRes.append(dataDetail2['folderName2'])
            partRes.append(dataDetail1['folderName1'])
            for dataDetail3 in dataDetail2['dataFolderValue2']:
                if dataDetail3['refTrackName'] == feature:
                    partRes.append(dataDetail3['data'][statIndex])
                    
            partTransposedProcessedResults.append(partRes) #wiersze
    
    transposedProcessedResults=[]
    for fv2 in folderValue2Unique:
        resu=[]
        for tr in partTransposedProcessedResults:
            if fv2 == tr[1]:
                if tr[0]+ ' (' + tr[1] + ')' not in resu:
                    resu.append(tr[0]+ ' (' + tr[1] + ')')
                for trRow in range(3, len(tr)):
                    resu.append(tr[trRow])
        transposedProcessedResults.append(resu)
    return transposedProcessedResults

def calculateForFeatureFolderName1Dim3(results, folderValue1Unique, statIndex, feature):
    partTransposedProcessedResults=[]
    for dataDetail1 in results:
        for dataDetail2 in dataDetail1['dataFolderValue1']:
            partRes=[]
            partRes.append(dataDetail2['targetTrackName'])
            partRes.append(dataDetail2['folderName2'])
            partRes.append(dataDetail1['folderName1'])
            for dataDetail3 in dataDetail2['dataFolderValue2']:
                if dataDetail3['refTrackName'] == feature:
                    partRes.append(dataDetail3['data'][statIndex])
                    
            partTransposedProcessedResults.append(partRes) #wiersze
    
    transposedProcessedResults=[]
    for fv2 in folderValue1Unique:
        resu=[]
        for tr in partTransposedProcessedResults:
            if fv2 == tr[2]:
                if tr[0]+ ' (' + tr[2] + ')' not in resu:
                    resu.append(tr[0]+ ' (' + tr[2] + ')')
                for trRow in range(3, len(tr)):
                    resu.append(tr[trRow])
        transposedProcessedResults.append(resu)
    return transposedProcessedResults


def calculateForFolderValue1NameDim1(results, folderValue1Unique,statIndex, folderName1):
    partRes=[]
    partTransposedProcessedResults=[]
    for dataDetail1 in results:
        for dataDetail2 in dataDetail1['dataFolderValue1']:
            partRes=[]
            partRes.append(dataDetail2['targetTrackName'])
            partRes.append(dataDetail2['folderName2'])
            partRes.append(dataDetail1['folderName1'])
            for dataDetail3 in dataDetail2['dataFolderValue2']:
                partRes.append(dataDetail3['data'][statIndex])
            partTransposedProcessedResults.append(partRes)
            
    transposedProcessedResults=[]
    for tr in partTransposedProcessedResults:
        resu=[]
        if tr[2] == folderName1:
            if tr[0] + " " + tr[1] not in resu:
                resu.append(tr[0] + " " + tr[1])
            for trRow in range(3, len(tr)):
                resu.append(tr[trRow])
            transposedProcessedResults.append(resu)
    return transposedProcessedResults

def calculateForFolderValue2NameDim2(results, folderValue2Unique,statIndex,  folderName2):
    partRes=[]
    partTransposedProcessedResults=[]
    for dataDetail1 in results:
        for dataDetail2 in dataDetail1['dataFolderValue1']:
            partRes=[]
            partRes.append(dataDetail2['targetTrackName'])
            partRes.append(dataDetail2['folderName2'])
            partRes.append(dataDetail1['folderName1'])
            for dataDetail3 in dataDetail2['dataFolderValue2']:
                partRes.append(dataDetail3['data'][statIndex])
            partTransposedProcessedResults.append(partRes)
            
    transposedProcessedResults=[]
    for tr in partTransposedProcessedResults:
        resu=[]
        if tr[1] == folderName2:
            if tr[0] + " " + tr[2] not in resu:
                resu.append(tr[0] + " " + tr[2])
            for trRow in range(3, len(tr)):
                resu.append(tr[trRow])
            transposedProcessedResults.append(resu)

    return transposedProcessedResults

def calculateSum(transposedProcessedResults):
    sumRes=[]
    i=0
    for tr in transposedProcessedResults:
        if i>0:
            sumRes = sumValList(tr, sumRes)
        else:
            sumRes=tr
        i+=1
    return sumRes

def sumValList(listA, listB):
    sumRes=[(listA[i] + listB[i]) for i in range(1, len(listA))]
    sumRes.insert(0, 'Sum')
    return sumRes

def calculateForTrackFolder2NameDim3(results, targetTrackTitles,statIndex, folderName2):
   
    partTransposedProcessedResults=[]
    for dataDetail1 in results:
        for dataDetail2 in dataDetail1['dataFolderValue1']:
            if dataDetail2['folderName2'] == folderName2:    
                for dataDetail3 in dataDetail2['dataFolderValue2']:
                    partRes=[]
                    partRes.append(dataDetail1['folderName1'])
                    partRes.append(dataDetail2['folderName2'])
                    partRes.append(dataDetail3['refTrackName'])
                    partRes.append(dataDetail3['data'][statIndex])   
                    partTransposedProcessedResults.append(partRes)
    
    transposedProcessedResults=[]
    for ttt in targetTrackTitles:
        resu=[]
        for tr in partTransposedProcessedResults:
            if ttt == tr[2]:
                if tr[2] not in resu:
                    resu.append(tr[2])
                for trRow in range(3, len(tr)):
                    resu.append(tr[trRow])
        transposedProcessedResults.append(resu)            
    return transposedProcessedResults

def calculateForTrackFolder1NameDim2(results, targetTrackTitles,statIndex, folderName1):
   
    partTransposedProcessedResults=[]
    for dataDetail1 in results:
        if dataDetail1['folderName1'] == folderName1:    
            for dataDetail2 in dataDetail1['dataFolderValue1']:
                for dataDetail3 in dataDetail2['dataFolderValue2']:
                    partRes=[]
                    partRes.append(dataDetail1['folderName1'])
                    partRes.append(dataDetail2['folderName2'])
                    partRes.append(dataDetail3['refTrackName'])
                    partRes.append(dataDetail3['data'][statIndex])   
                    partTransposedProcessedResults.append(partRes)
    
    transposedProcessedResults=[]
    for ttt in targetTrackTitles:
        resu=[]
        for tr in partTransposedProcessedResults:
            if ttt == tr[2]:
                if tr[2] not in resu:
                    resu.append(tr[2])
                for trRow in range(3, len(tr)):
                    resu.append(tr[trRow])
        transposedProcessedResults.append(resu)            
    return transposedProcessedResults


'''
def addJS2levelOptionList(folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, targetTrackNameList):
    
    js = """
    <form name="classic">
    <select name="dimensions" id="dimensions" size="1" onChange="updateChoices(this.selectedIndex)" style="width: 150px">
    <option value="0">Select a dimenison</option>
    <option value="1">Dim 1</option>
    <option value="2">Dim 2</option>
    <option value="3">Dim 3</option>
    </select>
    <br \>
    <br \>
    <select name="choices" id="choices" size="1" style="width: 100px" onChange="updateChoicesRowColumn(this.selectedIndex, dimensions.selectedIndex)">
    </select>
    <br \>
    <br \>
    <select name="choicesRowColumn" id="choicesRowColumn" size="1"  onClick="onClickChoicesRowColumn(dimensions.selectedIndex, choices.selectedIndex, this.options.selectedIndex)">
    </select>
    </form>


    
    <script type="text/javascript">
    
    document.getElementById("choices").style.visibility = "hidden";
    document.getElementById("choicesRowColumn").style.visibility = "hidden";
    """
    
    js += """ folderValue1Unique =""" + str(folderValue1Unique) + ";"
    js += """
    var fV1U = new Array(folderValue1Unique.length)
    fV1U[0] = "Select|0"
    for(i=0;i<folderValue1Unique.length;i++)
    {
        j=i+1
        fV1U[j] = folderValue1Unique[i] +'|' + j
    }
    j=j+1
    fV1U[j] = "All|" + j
    """
    
    js += """ folderValue2Unique =""" + str(folderValue2Unique) + ";"
    js += """
    var fV2U = new Array(folderValue2Unique.length)
    fV2U[0] = "Select|0"
    for(i=0;i<folderValue2Unique.length;i++)
    {
        j=i+1
        fV2U[j] = folderValue2Unique[i] +'|' + j
    }
    j=j+1
    fV2U[j] = "All|" + j
    """
    
    js += """ targetTrackFeatureTitles =""" + str(targetTrackFeatureTitles) + ";"
    js += """
    var tTfT = new Array(targetTrackFeatureTitles.length)
    tTfT[0] = "Select|0"
    for(i=0;i<targetTrackFeatureTitles.length;i++)
    {
        j=i+1
        tTfT[j] = targetTrackFeatureTitles[i] +'|' + j
    }
    j=j+1
    tTfT[j] = "All|" + j
    """
    
    js += """ targetTrackNameList =""" + str(targetTrackNameList) + ";"
    js += """
    var tTnL = new Array(targetTrackNameList.length)
    tTnL[0] = "Select|0"
    for(i=0;i<targetTrackNameList.length;i++)
    {
        j=i+1
        tTnL[j] = targetTrackNameList[i] +'|' + j
    }
    j=j+1
    tTnL[j] = "All|" + j
    """
   
    js += """
    var dimensionslist=document.classic.dimensions
    var choiceslist=document.classic.choices
    var chocieslistRowColumn=document.classic.choicesRowColumn
    
    var choices=new Array()
    choices[0]=""
    choices[1]=["Select|0", "Row|1", "Column|2", "All|3"]
    choices[2]=["Select|0", "Row|1", "Column|2", "All|3"]
    choices[3]=["Select|0", "Row|1", "Column|2", "All|3"]
    
    var choicesRowColumn=new Array(3)
    for (i=0; i<4; i++)
    {
        choicesRowColumn[i]=new Array(4)
    }
    choicesRowColumn[0][0]=""
    choicesRowColumn[0][1]=fV1U
    choicesRowColumn[0][2]=tTfT
    choicesRowColumn[0][3]=[]
    choicesRowColumn[1][0]=""
    choicesRowColumn[1][1]=fV1U
    choicesRowColumn[1][2]=fV2U
    choicesRowColumn[1][3]=[]
    choicesRowColumn[2][0]=""
    choicesRowColumn[2][1]=fV2U
    choicesRowColumn[2][2]=tTfT
    choicesRowColumn[2][3]=[]
    
    function updateChoices(selectedChoicesGroup)
    {
        hideTable()
        document.getElementById("choices").style.visibility = "hidden";
        document.getElementById("choicesRowColumn").style.visibility = "hidden";   
        if(selectedChoicesGroup  != 0)
        {
            document.getElementById("choices").style.visibility = "visible";   
        }
        
        choiceslist.options.length=0
        if (selectedChoicesGroup>0)
        {
            for (i=0; i<choices[selectedChoicesGroup].length; i++)
                choiceslist.options[choiceslist.options.length]=new Option(choices[selectedChoicesGroup][i].split("|")[0], choices[selectedChoicesGroup][i].split("|")[1])
        }
        var dimensions = document.getElementById("dimensions");
        dimensions.options[selectedChoicesGroup].setAttribute("selected", "selected");
    }

    
    function updateChoicesRowColumn(selectedChoicesGroupRowColumn, selDim)
    {
        hideTable()
        
        var ch = document.getElementById("choices");
        var selCh = ch.selectedIndex
        selDim=selDim-1
        
        if(selCh != 0 && selCh != 3)
        {
            document.getElementById("choicesRowColumn").style.visibility = "visible";
            
            chocieslistRowColumn.options.length=0
            if (selectedChoicesGroupRowColumn>0)
            {
                for (j=0; j<choicesRowColumn.length; j++)
                {
                    if(j == selDim)
                    {
                        for (i=0; i<choicesRowColumn[selDim][selectedChoicesGroupRowColumn].length; i++)
                        {
                            chocieslistRowColumn.options[chocieslistRowColumn.options.length]=new Option(choicesRowColumn[j][selectedChoicesGroupRowColumn][i].split("|")[0], choicesRowColumn[j][selectedChoicesGroupRowColumn][i].split("|")[1])
                        }
                    }
                }
            }
        }
        else
        {
            document.getElementById("choicesRowColumn").style.visibility = "hidden";
            if(selCh == 3)
            {
                showAllTables(selDim)
            }
        }
    }
    
    function hideTable()
    {
        var childDivs = document.getElementById('results').getElementsByTagName('div');
        for( i=0; i< childDivs.length; i++ )
        {
            var childDiv = childDivs[i];
            var resultsDiv = document.getElementById(childDiv.id);
            resultsDiv.setAttribute('class', 'hidden');
        }
    }
    function showAllTables(selDim)
    {
        selDim = selDim +1
        var childDivs = document.getElementById('results').getElementsByTagName('div');
        for( i=0; i< childDivs.length; i++ )
        {
            var childDiv = childDivs[i];
            temp = childDiv.id
            temp = temp.replace("[", "");
            temp = temp.replace("]", "");
            var tab = new Array();
            tab = temp.split(",");
            
            if(tab[0] == selDim)
            {
                var resultsDiv = document.getElementById(childDiv.id);
                resultsDiv.setAttribute('class', 'visible');
            }
        }
    }
    function showAllRowsColumn(selDim, selCh)
    {
        var childDivs = document.getElementById('results').getElementsByTagName('div');
        for( i=0; i< childDivs.length; i++ )
        {
            var childDiv = childDivs[i];
            temp = childDiv.id
            temp = temp.replace("[", "");
            temp = temp.replace("]", "");
            var tab = new Array();
            tab = temp.split(",");
            
            
            if(tab[0] == selDim && tab[1] == selCh)
            {
                var resultsDiv = document.getElementById(childDiv.id);
                resultsDiv.setAttribute('class', 'visible');
            }
        }
    }
    
    function onClickChoicesRowColumn(dimensions, choices, choicesRowColumnIndex)
    {
        if(choicesRowColumnIndex>0)
        {
            numEl=choicesRowColumn[dimensions-1][choices].length
            numEl=numEl-1
            
            if(choicesRowColumnIndex!=numEl)
            {
                choicesRowColumnIndex = choicesRowColumnIndex - 1
                var divName = '[' + dimensions + ', ' + choices + ', ' + choicesRowColumnIndex + ']'
                var resultsDiv = document.getElementById(divName);
                resultsDiv.setAttribute('class', 'visible');
                
                var childDivs = document.getElementById('results').getElementsByTagName('div');
                for( i=0; i< childDivs.length; i++ )
                {
                    var childDiv = childDivs[i];
                    if(childDiv.id != divName)
                    {
                        var resultsDiv = document.getElementById(childDiv.id);
                        resultsDiv.setAttribute('class', 'hidden');
                    }          
                }
            }
            else
            {
                showAllRowsColumn(dimensions, choices)
            }
        }
    }
    
    </script>
    """
    return js
    
'''

def calculateTextToCube(folderValue1Unique, divNum):
    divFolderValue1Unique=""
    i=0
    for cutFv1U in folderValue1Unique:
        if i < 4:
            divFolderValue1Unique+="<div class='face"+str(divNum) + "'>"+ str(cutFv1U[:12]).replace(" ",'&nbsp;') + "..." + "</div>"
            if len(folderValue1Unique)<4:
                if i != len(folderValue1Unique)-1:
                    divFolderValue1Unique+="<div class='line"+str(divNum) + "'></div>"
            else:
                if i != 3:
                    divFolderValue1Unique+="<div class='line"+str(divNum) + "'></div>"
        i+=1
    return str(divFolderValue1Unique)

def calculateTextToExCube(folderValue1Unique, divNum, divExNum, ifFirst=0, divNumEx=0):
    divFolderValue1Unique=""
    i=0
    for cutFv1U in folderValue1Unique:
        if i < 4:
            if i==0 and ifFirst == 1:
                divFolderValue1Unique+="<div class='face"+str(divNumEx) + "'>"+ str(cutFv1U[:15]).replace(" ",'&nbsp;') + "..." + "</div>"
            else:
                divFolderValue1Unique+="<div class='face"+str(divNum) + "'>"+ str(cutFv1U[:15]).replace(" ",'&nbsp;') + "..." + "</div>"
            if len(folderValue1Unique)<4:
                if i != len(folderValue1Unique)-1:
                    divFolderValue1Unique+="<div class='line"+str(divNum) + "'></div>"
            else:
                if i != 3:
                    divFolderValue1Unique+="<div class='line"+str(divNum) + "'></div>"
        i+=1
    if ifFirst == 0:
        divFolderValue1Unique+="<div class='line"+str(divExNum) + "'></div>"
    return str(divFolderValue1Unique)
    
def createTableTextToExCube(folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles):
    divFolderValue2Unique=""
    i=0
    divFolderValue2Unique+= ' <div class="table">'
    divFolderValue2Unique+= '<div class="tr"> '
    divFolderValue2Unique+= '<div class="td">' + 'Track names' + '</div>'
    for cutFv2U in folderValue2Unique:
        if i < 2:
            divFolderValue2Unique+= '<div class="td">' + str(cutFv2U[:15])+ "..." + '</div>'
        i+=1
    divFolderValue2Unique+= '</div>'
    i=0
    for cutFv2U in targetTrackFeatureTitles:
        if i < 2:
            divFolderValue2Unique+= '<div class="tr"> '
            divFolderValue2Unique+= '<div class="td">' + str(cutFv2U[:15])+ "..." + '</div>'
            divFolderValue2Unique+= '<div class="td">' + 'value' + '</div>'
            divFolderValue2Unique+= '<div class="td">' + 'value' + '</div>'
            divFolderValue2Unique+= '</div>'
        i+=1
    divFolderValue2Unique+= '</div>'
    return divFolderValue2Unique

def showExCube(folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, targetTrackNameList):

    js = """<script language="javascript"> 
           function toggle3(showHideDiv1, switchTextDiv1) {
                var ele = document.getElementById(showHideDiv1);
                var text = document.getElementById(switchTextDiv1);
                if(ele.style.display == "block") {
                        ele.style.display = "none";
                        text.innerHTML = "Show example";
                }
                else {
                        ele.style.display = "block";
                        text.innerHTML = "Hide example";
                }
        }
        </script>
        """
    js += """
        <style>
          .line13{
            border-bottom:20px solid rgba( 153, 205, 201,.8);
            padding:0px 2px;
            padding;
            width:155px;
            height:1px;
            }
            .face13{
            height:20px;
            color:#6E6E6E;
            background-color:rgba( 153, 205, 201,.8);
            margin-left:2px;
            font-size:14px;
            }
          .ex{
          margin-bottom:10px;
          }
          .exDesc{
          }
          #contentDiv{
            height:240px;
          }
          .left{
          float:left;
          width:320px;
          }
          .smallLeft{
            float:left;
          width:70px;
          }
        .arrow-right {
            width: 0; 
            height: 0;
            margin-top:70px;
            border-top: 10px solid transparent;
            border-bottom: 10px solid transparent;
            border-left: 10px solid #99cdc9;
        }
        .arrow-left {
            width: 0; 
            height: 0;
            margin-top:100px;
            border-top: 10px solid transparent;
            border-bottom: 10px solid transparent;
            border-right: 10px solid #99cdc9;
        }
          div.table {display: table; }
            div.tr {display: table-row; }
            div.td {
            border: 1px dotted #99cdc9; 
            display: table-cell;
            padding:5px;
            }
        .steps{
            color:#3E766D;
            margin-bottom:10px;
        }
        .steps2{
            color:#3E766D;
            margin:30px 0px;
        }
          </style>
        """
    js+="""
    
            <div id="headerDiv">
                <a id="myHeader1" href="javascript:toggle3('myContent1','myHeader1');" >Show example</a>
           </div>
           <div style="clear:both;"></div>
           <div id="contentDiv">
                <div id="myContent1" style="display: none;padding:50px 50px 80px 50px;">
                
                
                    <div class="left">
                        <div class="ex">Example:</div>
                        <div class="exDesc">
                            <div class="steps">
                            [1 step] Look at the input data
                            </div>
                            <span style="font-weight:bold">Input:</span><br />
                            selected: Dim1
                            <br />
                            selected: Row
                            <br />
                            selected: """ + folderValue1Unique[0] +  """
                            <br />
                            <br />
                                <div class="steps">
                                [3 step] Look at the output data
                                </div>
                            <span style="font-weight:bold">Output:</span>
                            <br />
                            table:
                            <br />
                            """ + str(createTableTextToExCube(folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)) + """
                        </div>
                    </div>
                    <div class="smallLeft">
                        <div class="arrow-right"></div>
                        <div class="arrow-left"></div>
                    </div>
                    <div class="left">
                    <div class="steps2">
                            [2 step] Compare the input data to the associated row/column in the cube
                    </div>
                
                    <div class="stage" style="width: 120px; height: 120px;">
                    <div class="cubespinner">
                    <div id="cub" class="face1">
                    Dim 1
                            <div class="bothFace">
                                    """ + calculateTextToExCube(targetTrackFeatureTitles, '11', '13') + """
                            </div>
                    </div>
                    <div id="cub" class="face2">
                    Dim 2
                            <div class="bothFace">
                                    """ + calculateTextToExCube(folderValue2Unique, '11', '13') + """
                            </div>
                    </div>
                    <div id="cub" class="face3">
                    Dim 3
                    <div class="bothFace">
                                    """ + calculateTextToExCube(folderValue1Unique, '12', '13', 1, '13') + """
                            </div>
                    </div>
                    <div id="cub" class="face4">Dim1
                    <div class="bothFace">
                                    """ + calculateTextToExCube(targetTrackFeatureTitles, '11', '13') + """
                            </div>
                    </div>
                    <div id="cub" class="face5">
                    Dim2
                    <div class="bothFace">
                                    """ + calculateTextToExCube(folderValue2Unique, '11', '13') + """
                            </div>
                    </div>
                    <div id="cub" class="face6">
                    Dim 3
                    <div class="bothFace">
                                    """ + calculateTextToExCube(folderValue1Unique,  '12', '13', 1, '13') + """
                            </div>
                    </div>
                    </div>
                    </div>
                </div>
           </div>
           <div style="clear:both">
"""
    return js

def showCube(folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, targetTrackNameList):

    
    js = """<script language="javascript"> 
           function toggle2(showHideDiv, switchTextDiv) {
                var ele = document.getElementById(showHideDiv);
                var text = document.getElementById(switchTextDiv);
                if(ele.style.display == "block") {
                        ele.style.display = "none";
                        text.innerHTML = "Show cube";
                }
                else {
                        ele.style.display = "block";
                        text.innerHTML = "Hide cube";
                }
        }
        </script>
        """
    js+= """
    <style type="text/css">@-webkit-keyframes spincube {
    from,to  { -webkit-transform: rotateX(0deg) rotateY(0deg) rotateZ(0deg); }
    16%      { -webkit-transform: rotateY(-90deg);                           }
    33%      { -webkit-transform: rotateY(-90deg) rotateZ(90deg);            }
    50%      { -webkit-transform: rotateY(-180deg) rotateZ(90deg);           }
    66%      { -webkit-transform: rotateY(-270deg) rotateX(90deg);           }
    83%      { -webkit-transform: rotateX(90deg);                            }
  }@keyframes spincube {
    from,to {
      -moz-transform: rotateX(0deg) rotateY(0deg) rotateZ(0deg);
      -ms-transform: rotateX(0deg) rotateY(0deg) rotateZ(0deg);
      transform: rotateX(0deg) rotateY(0deg) rotateZ(0deg);
    }
    16% {
      -moz-transform: rotateY(-90deg);
      -ms-transform: rotateY(-90deg);
      transform: rotateY(-90deg);
    }
    33% {
      -moz-transform: rotateY(-90deg) rotateZ(90deg);
      -ms-transform: rotateY(-90deg) rotateZ(90deg);
      transform: rotateY(-90deg) rotateZ(90deg);
    }
    50% {
      -moz-transform: rotateY(-180deg) rotateZ(90deg);
      -ms-transform: rotateY(-180deg) rotateZ(90deg);
      transform: rotateY(-180deg) rotateZ(90deg);
    }
    66% {
      -moz-transform: rotateY(-270deg) rotateX(90deg);
      -ms-transform: rotateY(-270deg) rotateX(90deg);
      transform: rotateY(-270deg) rotateX(90deg);
    }
    83% {
      -moz-transform: rotateX(90deg);
      -ms-transform: rotateX(90deg);
      transform: rotateX(90deg);
    }
  }.cubespinner{
  -webkit-animation-name:spincube;-webkit-animation-timing-function:ease-in-out;
  -webkit-animation-iteration-count:infinite;
  -webkit-animation-duration:12s;
  animation-name:spincube;
  animation-timing-function:ease-in-out;
  animation-iteration-count:infinite;
  animation-duration:12s;
  -webkit-transform-style:preserve-3d;
  -moz-transform-style:preserve-3d;
  -ms-transform-style:preserve-3d;
  transform-style:preserve-3d;
  -webkit-transform-origin:60px 60px 0;
  -moz-transform-origin:60px 60px 0;
  -ms-transform-origin:60px 60px 0;
  transform-origin:60px 60px 0
  }
  .cubespinner div#cub{
  position:absolute;
  width:160px;
  height:160px;
  border:1px solid #ccc;
  background:rgba(255,255,255,.8);
  box-shadow:inset 0 0 20px rgba(0,0,0,.2);
  text-align:center;font-size:16px
  }
  .cubespinner .face1{
  -webkit-transform:translateZ(60px);
  -moz-transform:translateZ(60px);
  -ms-transform:translateZ(60px);
  transform:translateZ(60px)
  }
  .cubespinner .face2{
  -webkit-transform:rotateY(90deg) translateZ(60px);
  -moz-transform:rotateY(90deg) translateZ(60px);
  -ms-transform:rotateY(90deg) translateZ(60px);
  transform:rotateY(90deg) translateZ(60px)
  }
  .cubespinner .face3{
  -webkit-transform:rotateY(90deg) rotateX(90deg) translateZ(60px);
  -moz-transform:rotateY(90deg) rotateX(90deg) translateZ(60px);
  -ms-transform:rotateY(90deg) rotateX(90deg) translateZ(60px);
  transform:rotateY(90deg) rotateX(90deg) translateZ(60px)
  }
  .cubespinner .face4{
  -webkit-transform:rotateY(180deg) rotateZ(90deg) translateZ(60px);
  -moz-transform:rotateY(180deg) rotateZ(90deg) translateZ(60px);
  -ms-transform:rotateY(180deg) rotateZ(90deg) translateZ(60px);
  transform:rotateY(180deg) rotateZ(90deg) translateZ(60px)
  }
  .cubespinner .face5{
  -webkit-transform:rotateY(-90deg) rotateZ(90deg) translateZ(60px);
  -moz-transform:rotateY(-90deg) rotateZ(90deg) translateZ(60px);
  -ms-transform:rotateY(-90deg) rotateZ(90deg) translateZ(60px);
  transform:rotateY(-90deg) rotateZ(90deg) translateZ(60px)
  }
  .cubespinner .face6{-webkit-transform:rotateX(-90deg) translateZ(60px);
  -moz-transform:rotateX(-90deg) translateZ(60px);
  -ms-transform:rotateX(-90deg) translateZ(60px);
  transform:rotateX(-90deg) translateZ(60px)
  }
  
  .bothFace{
   display:block;
  }
  .face11{
   float:left;
   width:20px;
  -webkit-transform: rotate(90deg);
  -moz-transform: rotate(90deg);
  -ms-transform: rotate(90deg);
  -o-transform: rotate(90deg);
  transform: rotate(90deg);
    color:#6E6E6E;
  padding-left:2px;
  margin-left:2px;
  font-size:14px;
  }
   .line11{
  float:left;
  border-right:1px solid black;
  padding:0px 2px;
  padding;
  width:1px;
  height:120px;
  }
  .face12{
   height:20px;
   color:#6E6E6E;
   padding-left:2px;
   margin-left:2px;
   font-size:14px;
  }
  .line12{
  border-bottom:1px solid black;
  padding:0px 2px;
  padding;
  width:156px;
  height:1px;
  }
  .face13{
    height:20px;
    color:#6E6E6E;
    background-color:#78AB46;
    padding-left:2px;
    margin-left:2px;
    font-size:14px;
    }
  .ex{
  margin-bottom:10px;
  }
  .exDesc{
  }
  .left{
  float:left;
  width:200px;
  }
  </style>
  """

    js+="""         
            <div id="headerDiv">
                <a id="myHeader" href="javascript:toggle2('myContent','myHeader');" >Show cube</a>
           </div>
           <div style="clear:both;"></div>
           <div id="contentDiv">
                <div id="myContent" style="display: none;padding:50px 50px 80px 50px;">
                    <div class="stage" style="width: 120px; height: 120px;">
                    <div class="cubespinner">
                    <div id="cub" class="face1">
                    folder-value 1 of second GSuite
                            <div class="bothFace">
                                    """ + calculateTextToCube(targetTrackFeatureTitles, '11') + """
                            </div>
                    </div>
                    <div id="cub" class="face2">
                    folder-value 2 of first GSuite
                            <div class="bothFace">
                                    """ + calculateTextToCube(folderValue2Unique, '11') + """
                            </div>
                    </div>
                    <div id="cub" class="face3">
                    folder-value 1 of first GSuite
                    <div class="bothFace">
                                    """ + calculateTextToCube(folderValue1Unique, '11') + """
                            </div>
                    </div>
                    <div id="cub" class="face4">
                    folder-value 1 of second GSuite
                    <div class="bothFace">
                                    """ + calculateTextToCube(targetTrackFeatureTitles, '12') + """
                            </div>
                    </div>
                    <div id="cub" class="face5">
                    folder-value 2 of first GSuite
                    <div class="bothFace">
                                    """ + calculateTextToCube(folderValue2Unique, '12') + """
                            </div>
                    </div>
                    <div id="cub" class="face6">
                    folder-value 1 of first GSuite
                    <div class="bothFace">
                                    """ + calculateTextToCube(folderValue1Unique, '12') + """
                            </div>
                    </div>
                    </div>
                </div>
           </div>
"""
    
    return js


def addHtml(divName, headerName, tableHeader, transposedProcessedResults, sumRes):
    
    htmlCore = HtmlCore()
    htmlCore.divBegin(divName, 'hidden')
    htmlCore.header(headerName) 
    htmlCore.tableHeader(tableHeader, sortable=True, tableId=divName)
    for row in transposedProcessedResults:
        htmlCore.tableLine(list(row))
    htmlCore.tableLine(list(sumRes))
    htmlCore.tableFooter()
    htmlCore.divEnd()
    return str(htmlCore)



#new version 17.04.2015

def fillFirstSelect(firstSelectTitle, idNum):
    js = firstSelectTitle + '''
    <select name="dimensions''' + str(idNum) + '''" id="dimensions''' + str(idNum) + '''" size="1" onClick="onClickChoices()" onChange="updateChoices''' + str(idNum) + '''(this.selectedIndex)" style="width: 150px">
    <option value="0">---Select---</option>
    <option value="1">Select one value</option>
    <option value="2">Show results for each value</option>
    <option value="3">Sum across this dimension</option>
    </select>
    '''
    return js

def fillSecondSelect(secondSelectTitle, idNum):
    js = '''
    <select name="choices''' + str(idNum) + '''" id="choices''' + str(idNum) + '''" size="1" style="width: 100px"  onClick="onClickChoices()">
    </select>'''
    return js

def addSecondSelectInfo(idNum):
    js = '''document.getElementById("choices''' + str(idNum) + '''").style.visibility = "hidden";
    var dimensionslist''' + str(idNum) + '''=document.classic.dimensions''' + str(idNum) + ''';
    var choiceslist''' + str(idNum) + '''=document.classic.choices''' + str(idNum) + ''';
    
    '''
    return js

def fillSecondSelectOption(idNum, data):
    js = '''
    var choices''' + str(idNum) + '''=new Array()
    choices''' + str(idNum) + '''[1]=''' + data
    return js

def updateChoices(idNum):
    js = '''
    function updateChoices''' + str(idNum) + '''(selectedChoicesGroup)
    {
        hideTable()
        document.getElementById("choices''' + str(idNum) + '''").style.visibility = "hidden";        
        if(selectedChoicesGroup  == 1)
        {
            document.getElementById("choices''' + str(idNum) + '''").style.visibility = "visible";       
            
            choiceslist''' + str(idNum) + '''.options.length=0
            if (selectedChoicesGroup>0)
            {
                for (i=0; i<choices''' + str(idNum) + '''[selectedChoicesGroup].length; i++)
                {
                    choiceslist''' + str(idNum) + '''.options[choiceslist''' + str(idNum) + '''.options.length]=new Option(choices''' + str(idNum) + '''[selectedChoicesGroup][i].split("|")[0], choices''' + str(idNum) + '''[selectedChoicesGroup][i].split("|")[1])
                }
            }
            var dimensions''' + str(idNum) + ''' = document.getElementById("dimensions''' + str(idNum) + '''");
            dimensions''' + str(idNum) + '''.options[selectedChoicesGroup].setAttribute("selected", "selected");
        }
    }
    '''
    return js

def addJS2levelOptionList(folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, targetTrackNameList):
    
    js = """
    <form name="classic">
    """ 
    js += fillFirstSelect("How to treat folder-value 1 of first GSuite", 1)
    js += fillSecondSelect("Selected value", 1)
    js += "<br \><br \>"
    js += fillFirstSelect("How to treat folder-value 2 of first GSuite", 2)
    js += fillSecondSelect("Selected value", 2)
    js += "<br \><br \>"
    js += fillFirstSelect("How to treat folder-value 1 of second GSuite", 3)
    js += fillSecondSelect("Selected value", 3)
    
    js += """
    </form>

    <script type="text/javascript">    
    """
    js += addSecondSelectInfo(1)
    js += addSecondSelectInfo(2)
    js += addSecondSelectInfo(3)
     
    js += """ folderValue1Unique =""" + str(folderValue1Unique) + ";"
    js += """
    var fV1U = new Array(folderValue1Unique.length)
    fV1U[0] = "Select value|0"
    for(i=0;i<folderValue1Unique.length;i++)
    {
        j=i+1
        fV1U[j] = folderValue1Unique[i] +'|' + j
    }
    j=j+1
    """
    
    js += """ folderValue2Unique =""" + str(folderValue2Unique) + ";"
    js += """
    var fV2U = new Array(folderValue2Unique.length)
    fV2U[0] = "Select value|0"
    for(i=0;i<folderValue2Unique.length;i++)
    {
        j=i+1
        fV2U[j] = folderValue2Unique[i] +'|' + j
    }
    """
    
    js += """ targetTrackFeatureTitles =""" + str(targetTrackFeatureTitles) + ";"
    js += """
    var tTfT = new Array(targetTrackFeatureTitles.length)
    tTfT[0] = "Select value|0"
    for(i=0;i<targetTrackFeatureTitles.length;i++)
    {
        j=i+1
        tTfT[j] = targetTrackFeatureTitles[i] +'|' + j
    }
    j=j+1
    """
    
    js += """ targetTrackNameList =""" + str(targetTrackNameList) + ";"
    js += """
    var tTnL = new Array(targetTrackNameList.length)
    tTnL[0] = "Select value|0"
    for(i=0;i<targetTrackNameList.length;i++)
    {
        j=i+1
        tTnL[j] = targetTrackNameList[i] +'|' + j
    }
    j=j+1
    """
   
    js += """
    
    var chocieslistRowColumn=document.classic.choicesRowColumn
    """
    
    js += fillSecondSelectOption(1, 'fV1U')
    js += fillSecondSelectOption(2, 'fV2U')
    js += fillSecondSelectOption(3, 'tTfT')
    
    js += updateChoices(1)
    js += updateChoices(2)
    js += updateChoices(3)
    
    js += """
    function updateChoicesRowColumn(selectedChoicesGroupRowColumn, selDim)
    {
        hideTable()
        
        var ch = document.getElementById("choices1");
        var selCh = ch.selectedIndex
        selDim=selDim-1
        
        if(selCh != 0 && selCh != 3)
        {
            document.getElementById("choicesRowColumn").style.visibility = "visible";
            
            chocieslistRowColumn.options.length=0
            if (selectedChoicesGroupRowColumn>0)
            {
                for (j=0; j<choicesRowColumn.length; j++)
                {
                    if(j == selDim)
                    {
                        for (i=0; i<choicesRowColumn[selDim][selectedChoicesGroupRowColumn].length; i++)
                        {
                            chocieslistRowColumn.options[chocieslistRowColumn.options.length]=new Option(choicesRowColumn[j][selectedChoicesGroupRowColumn][i].split("|")[0], choicesRowColumn[j][selectedChoicesGroupRowColumn][i].split("|")[1])
                        }
                    }
                }
            }
        }
        else
        {
            document.getElementById("choicesRowColumn").style.visibility = "hidden";
            if(selCh == 3)
            {
                showAllTables(selDim)
            }
        }
    }
    
    function hideTable()
    {
        var childDivs = document.getElementById('results').getElementsByTagName('div');
        for( i=0; i< childDivs.length; i++ )
        {
            var childDiv = childDivs[i];
            var resultsDiv = document.getElementById(childDiv.id);
            resultsDiv.setAttribute('class', 'hidden');
        }
    }
    function showAllTables(selDim)
    {
        selDim = selDim +1
        var childDivs = document.getElementById('results').getElementsByTagName('div');
        for( i=0; i< childDivs.length; i++ )
        {
            var childDiv = childDivs[i];
            temp = childDiv.id
            temp = temp.replace("[", "");
            temp = temp.replace("]", "");
            var tab = new Array();
            tab = temp.split(",");
            
            if(tab[0] == selDim)
            {
                var resultsDiv = document.getElementById(childDiv.id);
                resultsDiv.setAttribute('class', 'visible');
            }
        }
    }
    function showAllRowsColumn(selDim, selCh)
    {
        var childDivs = document.getElementById('results').getElementsByTagName('div');
        for( i=0; i< childDivs.length; i++ )
        {
            var childDiv = childDivs[i];
            temp = childDiv.id
            temp = temp.replace("[", "");
            temp = temp.replace("]", "");
            var tab = new Array();
            tab = temp.split(",");
            
            
            if(tab[0] == selDim && tab[1] == selCh)
            {
                var resultsDiv = document.getElementById(childDiv.id);
                resultsDiv.setAttribute('class', 'visible');
            }
        }
    }
    function onClickChoices()
    {
        hideTable();
        
        var ch1 = document.getElementById("choices1");
        var selCh1 = ch1.selectedIndex
        var ch2 = document.getElementById("choices2");
        var selCh2 = ch2.selectedIndex
        var ch3 = document.getElementById("choices3");
        var selCh3 = ch3.selectedIndex
        
        var dim1 = document.getElementById("dimensions1");
        var selDim1 = dim1.selectedIndex
        var dim2 = document.getElementById("dimensions2");
        var selDim2 = dim2.selectedIndex
        var dim3 = document.getElementById("dimensions3");
        var selDim3 = dim3.selectedIndex
        
        if(selCh1!=-1)
        {
            selCh1 = selCh1-1;
        }
        if(selCh2!=-1)
        {
            selCh2 = selCh2-1;
        }
        if(selCh3!=-1)
        {
            selCh3 = selCh3-1;
        }
        
        if (selDim1 == 2 || selDim1 == 3)
        {
            selCh1=-1;
        }
        if (selDim2 == 2 || selDim2 == 3)
        {
            selCh2=-1;
        }
        if (selDim3 == 2 || selDim3 == 3)
        {
            selCh3=-1;
        }
        
        var divName = '[' + selDim1 + ', ' + selCh1 + ', ' + selDim2 + ', ' + selCh2 + ', ' + selDim3 + ', ' + selCh3 + ']';
        console.log(divName);
        var resultsDiv = document.getElementById(divName);
        resultsDiv.setAttribute('class', 'visible');
                
                
    }
    
    function onClickChoicesRowColumn(dimensions, choices, choicesRowColumnIndex)
    {
        if(choicesRowColumnIndex>0)
        {
            numEl=choicesRowColumn[dimensions-1][choices].length
            numEl=numEl-1
            
            if(choicesRowColumnIndex!=numEl)
            {
                choicesRowColumnIndex = choicesRowColumnIndex - 1
                var divName = '[' + dimensions + ', ' + choices + ', ' + choicesRowColumnIndex + ']'
                var resultsDiv = document.getElementById(divName);
                resultsDiv.setAttribute('class', 'visible');
                
                var childDivs = document.getElementById('results').getElementsByTagName('div');
                for( i=0; i< childDivs.length; i++ )
                {
                    var childDiv = childDivs[i];
                    if(childDiv.id != divName)
                    {
                        var resultsDiv = document.getElementById(childDiv.id);
                        resultsDiv.setAttribute('class', 'hidden');
                    }          
                }
            }
            else
            {
                showAllRowsColumn(dimensions, choices)
            }
        }
    }
    
    </script>
    """
    return js


def preporcessResults(results, folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, stat):
    data=[]
    allRes =''
    for dataDetail1 in results:
        for key1, val1 in dataDetail1.items():
            if isinstance(val1, (list)):
                for dataDetail2 in val1:
                        for key2, val2 in dataDetail2.items():
                            if isinstance(val2, (list)):
                                for dataDetail3 in val2:
                                    res1=[]
                                    header1=[]
                                    for tTf in range(0, len(targetTrackFeatureTitles)):
                                        if dataDetail3['refTrackName'] == targetTrackFeatureTitles[tTf]:
                                            tableNum1 = [1, folderValue1Unique.index(dataDetail1['folderName1']), 1, folderValue2Unique.index(dataDetail2['folderName2']), 1, targetTrackFeatureTitles.index(dataDetail3['refTrackName'])]
                                            tableTitle1 =[dataDetail1['folderName1'], dataDetail2['folderName2']]
                                            header1.append('Tracks') 
                                            header1.append('Values')
                                            res1.append(dataDetail3['refTrackName'])
                                            res1.append(dataDetail3['data'][stat])
                                            allRes += createResTable([tableNum1, tableTitle1, header1, [res1]], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
                                            data.append([dataDetail1['folderName1'], dataDetail2['folderName2'], dataDetail3['refTrackName'], dataDetail3['data'][stat]])
    
    allRes += createTables(data, folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)

    return allRes

def depth(l):
    if isinstance(l, list) and l:
        return 1 + max(depth(item) for item in l)
    else:
        return 0

def createTables(data, folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles):
    
    allRes=''
    
    sumAll =0
    res5=[]
    res6=[]
    res7=[]
    res10=[]
    for numfV1U in range(0, len(folderValue1Unique)):
        tableTitle1=[folderValue1Unique[numfV1U]]
        res1=[]
        sumVal=0
        res2=[]
        res3=[]
        for d in data:
            if d[0] == folderValue1Unique[numfV1U]:
                sumValCol4=0
                for tTfT in targetTrackFeatureTitles:
                    if d[2] == tTfT:
                        res1.append([[d[2], d[1]], d[3]])
                        sumVal += d[3]
                        sumValCol4 +=d[3]
                        res10.append([[d[2], d[0], d[1]], d[3]])
        for numfV2U in range(0, len(folderValue2Unique)):
                sumValCol=0
                res8=[]                
                for d in data:
                    if d[0] == folderValue1Unique[numfV1U]:
                        if d[1] == folderValue2Unique[numfV2U]:
                            for numtTfT in range(0, len(targetTrackFeatureTitles)):
                                header8=''
                                if d[2] == targetTrackFeatureTitles[numtTfT]:
                                    sumValCol += d[3]
                                    sumAll+=d[3]
                                    header8=targetTrackFeatureTitles[numtTfT]
                                    res8.append([header8, d[3]])
                #repair this one
                #allRes += createResTable([[1, numfV1U, 1, numfV2U, 2, -1], [folderValue1Unique[numfV1U], folderValue2Unique[numfV2U]], ['Tracks', 'Values'], res8], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
                res2.append([folderValue2Unique[numfV2U], sumValCol])
                res6.append([[folderValue2Unique[numfV2U], folderValue1Unique[numfV1U]], sumValCol])
                allRes += createResTable([[1, numfV1U, 1, numfV2U, 3, -1], [folderValue1Unique[numfV1U]], ['Sum', 'Values'], [[folderValue2Unique[numfV2U], sumValCol]]], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
        for numtTfT in range(0, len(targetTrackFeatureTitles)):
                sumValCol3=0
                res9=[]
                for d in data:
                    if d[2] == targetTrackFeatureTitles[numtTfT]:
                        if d[0] == folderValue1Unique[numfV1U]:
                            for numfV2U in range(0, len(folderValue2Unique)):
                                if d[1] == folderValue2Unique[numfV2U]:
                                    sumValCol3 += d[3]
                                    res9.append([folderValue2Unique[numfV2U], d[3]])
                allRes += createResTable([[1, numfV1U, 2, -1, 1, numtTfT], [targetTrackFeatureTitles[numtTfT], folderValue1Unique[numfV1U]], ['Tracks', 'Values'], res9], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
                res3.append([targetTrackFeatureTitles[numtTfT], sumValCol3])
                res7.append([[targetTrackFeatureTitles[numtTfT], folderValue1Unique[numfV1U]], sumValCol3])
        allRes += createResTable([[1, numfV1U, 3, -1, 2, -1], [folderValue1Unique[numfV1U]], ['Sum', 'Values'], res3], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
        allRes += createResTable([[1, numfV1U, 2, -1, 3, -1], [folderValue1Unique[numfV1U]], ['Sum', 'Values'], res2], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
        allRes += createResTable([[1, numfV1U, 2, -1, 2, -1], tableTitle1, ['Tracks'] + folderValue2Unique, res1], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
        allRes += createResTable([[1, numfV1U, 3, -1, 3, -1], [folderValue1Unique[numfV1U]], ['Sum', 'Values'], [[folderValue1Unique[numfV1U], sumVal]]], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
        res5.append([folderValue1Unique[numfV1U], sumVal])
    allRes += createResTable([[2, -1, 3, -1, 3, -1], ['All'], ['Sum', 'Values'], res5], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
    allRes += createResTable([[2, -1, 2, -1, 3, -1], ['All'], ['Tracks'] + folderValue1Unique, res6], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
    allRes += createResTable([[2, -1, 3, -1, 2, -1], ['All'],  ['Tracks'] + folderValue1Unique, res7], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
    allRes += createResTable([[3, -1, 3, -1, 3, -1], ['All'], ['Sum', 'Values'], [['Sum', sumAll]]], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
    allRes += createResTable([[2, -1, 2, -1, 2, -1], folderValue2Unique, ['Tracks'] + folderValue1Unique, res10], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
    
    res4=[]    
    res5=[]
    for numfV2U in range(0, len(folderValue2Unique)):
        tableTitle1=[folderValue2Unique[numfV2U]]
        res1=[]
        sumVal=0
        tableNum1 = [2, -1, 1, numfV2U, 2, -1]
        res2=[]
        res3=[]
        for d in data:
            if d[1] == folderValue2Unique[numfV2U]:
                for tTfT in targetTrackFeatureTitles:
                    if d[2] == tTfT:
                        res1.append([[d[2], d[0]], d[3]])
                        sumVal += d[3]
        res4.append([folderValue2Unique[numfV2U], sumVal])
        for numfV1U in range(0, len(folderValue1Unique)):
                sumValCol=0
                res9=[]
                for d in data:
                    if d[0] == folderValue1Unique[numfV1U]:
                        if d[1] == folderValue2Unique[numfV2U]:
                            for tTfT in targetTrackFeatureTitles:
                                if d[2] == tTfT:
                                    sumValCol += d[3]
                res2.append([folderValue1Unique[numfV1U], sumValCol])
                allRes += createResTable([[1, numfV1U, 1, numfV2U, 3, -1], [folderValue1Unique[numfV1U]], ['Sum', 'Values'], [[folderValue2Unique[numfV2U], sumValCol]]], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
        for numtTfT in range(0, len(targetTrackFeatureTitles)):
                sumValCol3=0
                for d in data:
                    if d[2] == targetTrackFeatureTitles[numtTfT]:
                        if d[1] == folderValue2Unique[numfV2U]:
                            for numfV1U in range(0, len(folderValue1Unique)):
                                if d[0] == folderValue1Unique[numfV1U]:
                                    sumValCol3 += d[3]
                res3.append([targetTrackFeatureTitles[numtTfT], sumValCol3])
                res5.append([[targetTrackFeatureTitles[numtTfT], folderValue2Unique[numfV2U]], sumValCol3])
        allRes += createResTable([[2, -1, 1, numfV2U, 3, -1], [folderValue2Unique[numfV2U]], ['Sum', 'Values'], res2], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
        allRes += createResTable([tableNum1, tableTitle1, ['Tracks'] + folderValue1Unique, res1], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
        allRes += createResTable([[3, -1, 1, numfV2U, 2, -1], [folderValue2Unique[numfV2U]], ['Sum', 'Values'], res3], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
        allRes += createResTable([[3, -1, 1, numfV2U, 3, -1], tableTitle1, ['Sum', 'Values'], [[folderValue2Unique[numfV2U], sumVal]]], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
    allRes += createResTable([[3, -1, 2, -1, 2, -1], ['All'], ['Tracks'] + folderValue2Unique, res5], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
    allRes += createResTable([[3, -1, 2, -1, 3, -1], ['All'], ['Sum', 'Values'], res4], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
    
    res4=[]
    for numtTft in range(0, len(targetTrackFeatureTitles)):
        tableTitle1=[targetTrackFeatureTitles[numtTft]]
        res1=[]
        sumVal=0
        tableNum1 = [2, -1, 2, -1, 1, numtTft]
        res2=[]
        res3=[]
        sumValCol4=0
        for d in data:
            if d[2] == targetTrackFeatureTitles[numtTft]:
                for fV1U in folderValue1Unique:
                    if d[0] == fV1U:
                        res1.append([[d[1], d[0]], d[3]])
                        sumVal += d[3]
        for numfV2U in range(0, len(folderValue2Unique)):
                sumValCol=0
                res9=[]
                header9=''
                headerNum9=''
                for d in data:
                    if d[1] == folderValue2Unique[numfV2U]:
                        if d[2] == targetTrackFeatureTitles[numtTft]:
                            for numfV1U in range(0, len(folderValue1Unique)):
                                if d[0] == folderValue1Unique[numfV1U]:
                                    sumValCol += d[3]
                                    sumValCol4 += d[3]
                                    res9.append([folderValue1Unique[numfV1U], d[3]])
                        header9=targetTrackFeatureTitles[numtTft]
                        headerNum9=numtTft
                allRes += createResTable([[2, -1, 1, numfV2U, 1, headerNum9], [header9, folderValue2Unique[numfV2U]], ['Tracks', 'Values'], res9], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
                res2.append([folderValue2Unique[numfV2U], sumValCol])
                allRes += createResTable([[3, -1, 1, numfV2U, 1, numtTft], [targetTrackFeatureTitles[numtTft]], ['Sum', 'Values'], [[folderValue2Unique[numfV2U], sumValCol]]], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
        res4.append([targetTrackFeatureTitles[numtTft], sumValCol4])
        for numfV1U in range(0, len(folderValue1Unique)):
                sumValCol3=0
                for d in data:
                    if d[0] == folderValue1Unique[numfV1U]:
                        if d[2] == targetTrackFeatureTitles[numtTft]:
                            for fV2U in folderValue2Unique:
                                if d[1] == fV2U:
                                    sumValCol3 += d[3]
                res3.append([folderValue1Unique[numfV1U], sumValCol3])
                allRes += createResTable([[1, numfV1U, 3, -1, 1, numtTft], [targetTrackFeatureTitles[numtTft]], ['Sum', 'Values'], [[folderValue1Unique[numfV1U], sumValCol3]]], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
        allRes += createResTable([[3, -1, 2, -1, 1, numtTft], [targetTrackFeatureTitles[numtTft]], ['Sum', 'Values'], res2], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
        allRes += createResTable([[2, -1, 3, -1, 1, numtTft], [targetTrackFeatureTitles[numtTft]], ['Sum', 'Values'], res3], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
        allRes += createResTable([tableNum1, tableTitle1, ['Tracks'] + folderValue1Unique, res1], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
        allRes += createResTable([[3, -1, 3, -1, 1, numtTft], tableTitle1, ['Sum', 'Values'], [[targetTrackFeatureTitles[numtTft], sumVal]]], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
    allRes += createResTable([[3, -1, 3, -1, 2, -1], ['All'], ['Sum', 'Values'], res4], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)



    return allRes



def changeResLevel2(res, folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles):
    
    name1 = res[3][0][0][0]
    listToUse1=[]
    if name1 in targetTrackFeatureTitles:
        listToUse1 = targetTrackFeatureTitles
    elif name1 in folderValue1Unique:
        listToUse1 = folderValue1Unique
    else:
        listToUse1 = folderValue2Unique
    
    listToUse2=[]
    name2 = res[3][0][0][1]
    if name2 in targetTrackFeatureTitles:
        listToUse2 = targetTrackFeatureTitles
    elif name2 in folderValue1Unique:
        listToUse2 = folderValue1Unique
    else:
        listToUse2 = folderValue2Unique
    
    newResList=[]
    for el1 in listToUse1:
        newRow=[]
        countEl=0
        for j in range(0, len(listToUse2)):
            was=False
            for i in range(0, len(res[3])):
                if el1 == res[3][i][0][0] and listToUse2[j] == res[3][i][0][1]:
                    if countEl ==0:
                        newRow += [res[3][i][0][0]]
                        newRow += [res[3][i][1]]
                    else:
                        newRow += [res[3][i][1]]
                    countEl+=1
                    was=True
            if was == False:
                if j==0:
                    newRow += [el1]
                    countEl=1
                newRow += ['-']
        newResList.append(newRow)
        
    
    res[3] = newResList
    
    return res
    
def changeResLevel3(res, folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles):
    
    name1 = res[3][0][0][0]
    listToUse1=[]
    if name1 in targetTrackFeatureTitles:
        listToUse1 = targetTrackFeatureTitles
    elif name1 in folderValue1Unique:
        listToUse1 = folderValue1Unique
    else:
        listToUse1 = folderValue2Unique
    
    listToUse2=[]
    name2 = res[3][0][0][1]
    if name2 in targetTrackFeatureTitles:
        listToUse2 = targetTrackFeatureTitles
    elif name2 in folderValue1Unique:
        listToUse2 = folderValue1Unique
    else:
        listToUse2 = folderValue2Unique
        
    listToUse3=[]
    name3 = res[3][0][0][2]
    if name3 in targetTrackFeatureTitles:
        listToUse3 = targetTrackFeatureTitles
    elif name3 in folderValue1Unique:
        listToUse3 = folderValue1Unique
    else:
        listToUse3 = folderValue2Unique
    
    newResList=[]
    for el3 in listToUse3:
        newResListParts=[]
        for el1 in listToUse1:
            newRow=[]
            countEl=0
            for j in range(0, len(listToUse2)):
                was=False
                for i in range(0, len(res[3])):
                    if el1 == res[3][i][0][0] and listToUse2[j] == res[3][i][0][1] and el3 == res[3][i][0][2]:
                        if countEl ==0:
                            newRow += [res[3][i][0][0]]
                            newRow += [res[3][i][1]]
                        else:
                            newRow += [res[3][i][1]]
                        countEl+=1
                        was=True
                if was == False:
                    if j==0:
                        newRow += [el1]
                        countEl=1
                    newRow += ['-']
            newResListParts.append(newRow)
        newResList.append(newResListParts)
    
    
    res[3] = newResList
    
    return res

def createResTable(res, folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles):

    htmlCore = HtmlCore()
    
    which=0
    if depth(res[3]) == 3 and len(res[3][0][0]) == 2:
        res = changeResLevel2(res, folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
    if depth(res[3]) == 3 and len(res[3][0][0]) == 3:
        res = changeResLevel3(res, folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles)
        which=1
   
    if which == 0:
        htmlCore.divBegin(res[0], 'hidden')
        if len(res[1])==1:
            header = 'For: ' + str(res[1][0])
        elif len(res[1])==2:
            header = 'For: ' + str(res[1][0]) + ' and ' + str(res[1][1])
        elif len(res[1])==3:
            header = 'For: ' + str(res[1][0]) + ', ' + str(res[1][1]) + ' and ' + str(res[1][1])
        else:
            header='All'
     
        
        htmlCore.header(header) 
        htmlCore.tableHeader(res[2], sortable=True, tableId=res[0])
        for row in res[3]:
            htmlCore.tableLine(row)
        htmlCore.tableFooter()
        htmlCore.divEnd()
        
    if which == 1:
        htmlCore.divBegin(res[0], 'hidden')
        j=0
        for row1 in res[3]:
            header='For: ' + str(res[1][j])
            htmlCore.header(header) 
            htmlCore.tableHeader(res[2], sortable=True, tableId=res[0])
            for row in row1:
                htmlCore.tableLine(row)
            htmlCore.tableFooter()
            j+=1
            
        htmlCore.divEnd()
        
        
    
    return str(htmlCore)

def addJS3levelOptionList(folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, targetTrackNameList, folderValue0Unique):
    
    js = """
    <form name="classic">
    """
    js += fillFirstSelect("How to treat " + str(FIELD_NAME1), 4)
    js += fillSecondSelect("Selected value", 4)
    js += "<br \><br \>"
    js += fillFirstSelect("How to treat " + str(FIELD_NAME2), 1)
    js += fillSecondSelect("Selected value", 1)
    js += "<br \><br \>"
    js += fillFirstSelect("How to treat " + str(FIELD_NAME3), 2)
    js += fillSecondSelect("Selected value", 2)
    js += "<br \><br \>"
    js += fillFirstSelect("How to treat " + str(FIELD_NAME4), 3)
    js += fillSecondSelect("Selected value", 3)
    
    js += """
    </form>

    <script type="text/javascript">    
    """
    js += addSecondSelectInfo(1)
    js += addSecondSelectInfo(2)
    js += addSecondSelectInfo(3)
    js += addSecondSelectInfo(4)
     
    js += """ folderValue1Unique =""" + str(folderValue1Unique) + ";"
    js += """
    var fV1U = new Array(folderValue1Unique.length)
    fV1U[0] = "Select value|0"
    for(i=0;i<folderValue1Unique.length;i++)
    {
        j=i+1
        fV1U[j] = folderValue1Unique[i] +'|' + j
    }
    j=j+1
    """
    
    js += """ folderValue0Unique =""" + str(folderValue0Unique) + ";"
    js += """
    var fV0U = new Array(folderValue0Unique.length)
    fV0U[0] = "Select value|0"
    for(i=0;i<folderValue0Unique.length;i++)
    {
        j=i+1
        fV0U[j] = folderValue0Unique[i] +'|' + j
    }
    j=j+1
    """
    
    js += """ folderValue2Unique =""" + str(folderValue2Unique) + ";"
    js += """
    var fV2U = new Array(folderValue2Unique.length)
    fV2U[0] = "Select value|0"
    for(i=0;i<folderValue2Unique.length;i++)
    {
        j=i+1
        fV2U[j] = folderValue2Unique[i] +'|' + j
    }
    """
    
    js += """ targetTrackFeatureTitles =""" + str(targetTrackFeatureTitles) + ";"
    js += """
    var tTfT = new Array(targetTrackFeatureTitles.length)
    tTfT[0] = "Select value|0"
    for(i=0;i<targetTrackFeatureTitles.length;i++)
    {
        j=i+1
        tTfT[j] = targetTrackFeatureTitles[i] +'|' + j
    }
    j=j+1
    """
    
    js += """ targetTrackNameList =""" + str(targetTrackNameList) + ";"
    js += """
    var tTnL = new Array(targetTrackNameList.length)
    tTnL[0] = "Select value|0"
    for(i=0;i<targetTrackNameList.length;i++)
    {
        j=i+1
        tTnL[j] = targetTrackNameList[i] +'|' + j
    }
    j=j+1
    """
   
    js += """
    
    var chocieslistRowColumn=document.classic.choicesRowColumn
    """
    
    js += fillSecondSelectOption(1, 'fV1U')
    js += fillSecondSelectOption(2, 'fV2U')
    js += fillSecondSelectOption(3, 'tTfT')
    js += fillSecondSelectOption(4, 'fV0U')
    
    js += updateChoices(1)
    js += updateChoices(2)
    js += updateChoices(3)
    js += updateChoices(4)
    
    js += """
    function updateChoicesRowColumn(selectedChoicesGroupRowColumn, selDim)
    {
        hideTable()
        
        var ch = document.getElementById("choices1");
        var selCh = ch.selectedIndex
        selDim=selDim-1
        
        if(selCh != 0 && selCh != 3)
        {
            document.getElementById("choicesRowColumn").style.visibility = "visible";
            
            chocieslistRowColumn.options.length=0
            if (selectedChoicesGroupRowColumn>0)
            {
                for (j=0; j<choicesRowColumn.length; j++)
                {
                    if(j == selDim)
                    {
                        for (i=0; i<choicesRowColumn[selDim][selectedChoicesGroupRowColumn].length; i++)
                        {
                            chocieslistRowColumn.options[chocieslistRowColumn.options.length]=new Option(choicesRowColumn[j][selectedChoicesGroupRowColumn][i].split("|")[0], choicesRowColumn[j][selectedChoicesGroupRowColumn][i].split("|")[1])
                        }
                    }
                }
            }
        }
        else
        {
            document.getElementById("choicesRowColumn").style.visibility = "hidden";
            if(selCh == 3)
            {
                showAllTables(selDim)
            }
        }
    }
    
    function hideTable()
    {
        var childDivs = document.getElementById('results').getElementsByTagName('div');
        for( i=0; i< childDivs.length; i++ )
        {
            var childDiv = childDivs[i];
            var resultsDiv = document.getElementById(childDiv.id);
            resultsDiv.setAttribute('class', 'hidden');
        }
    }
    function showAllTables(selDim)
    {
        selDim = selDim +1
        var childDivs = document.getElementById('results').getElementsByTagName('div');
        for( i=0; i< childDivs.length; i++ )
        {
            var childDiv = childDivs[i];
            temp = childDiv.id
            temp = temp.replace("[", "");
            temp = temp.replace("]", "");
            var tab = new Array();
            tab = temp.split(",");
            
            if(tab[0] == selDim)
            {
                var resultsDiv = document.getElementById(childDiv.id);
                resultsDiv.setAttribute('class', 'visible');
            }
        }
    }
    function showAllRowsColumn(selDim, selCh)
    {
        var childDivs = document.getElementById('results').getElementsByTagName('div');
        for( i=0; i< childDivs.length; i++ )
        {
            var childDiv = childDivs[i];
            temp = childDiv.id
            temp = temp.replace("[", "");
            temp = temp.replace("]", "");
            var tab = new Array();
            tab = temp.split(",");
            
            
            if(tab[0] == selDim && tab[1] == selCh)
            {
                var resultsDiv = document.getElementById(childDiv.id);
                resultsDiv.setAttribute('class', 'visible');
            }
        }
    }
    function onClickChoices()
    {
        hideTable();
        
        var ch1 = document.getElementById("choices1");
        var selCh1 = ch1.selectedIndex
        var ch2 = document.getElementById("choices2");
        var selCh2 = ch2.selectedIndex
        var ch3 = document.getElementById("choices3");
        var selCh3 = ch3.selectedIndex
        var ch4 = document.getElementById("choices4");
        var selCh4 = ch4.selectedIndex
        
        var dim1 = document.getElementById("dimensions1");
        var selDim1 = dim1.selectedIndex
        var dim2 = document.getElementById("dimensions2");
        var selDim2 = dim2.selectedIndex
        var dim3 = document.getElementById("dimensions3");
        var selDim3 = dim3.selectedIndex
        var dim4 = document.getElementById("dimensions4");
        var selDim4 = dim4.selectedIndex
        
        if(selCh1!=-1)
        {
            selCh1 = selCh1-1;
        }
        if(selCh2!=-1)
        {
            selCh2 = selCh2-1;
        }
        if(selCh3!=-1)
        {
            selCh3 = selCh3-1;
        }
        if(selCh4!=-1)
        {
            selCh4 = selCh4-1;
        }
        
        if (selDim1 == 2 || selDim1 == 3)
        {
            selCh1=-1;
        }
        if (selDim2 == 2 || selDim2 == 3)
        {
            selCh2=-1;
        }
        if (selDim3 == 2 || selDim3 == 3)
        {
            selCh3=-1;
        }
        if (selDim4 == 2 || selDim4 == 3)
        {
            selCh4=-1;
        }
        
        var divName = '[' + selDim4 + ', ' + selCh4 + ', ' + selDim1 + ', ' + selCh1 + ', ' + selDim2 + ', ' + selCh2 + ', ' + selDim3 + ', ' + selCh3 + ']';
        console.log(divName);
        var resultsDiv = document.getElementById(divName);
        resultsDiv.setAttribute('class', 'visible');
                
                
    }
    
    function onClickChoicesRowColumn(dimensions, choices, choicesRowColumnIndex)
    {
        if(choicesRowColumnIndex>0)
        {
            numEl=choicesRowColumn[dimensions-1][choices].length
            numEl=numEl-1
            
            if(choicesRowColumnIndex!=numEl)
            {
                choicesRowColumnIndex = choicesRowColumnIndex - 1
                var divName = '[' + dimensions + ', ' + choices + ', ' + choicesRowColumnIndex + ']'
                var resultsDiv = document.getElementById(divName);
                resultsDiv.setAttribute('class', 'visible');
                
                var childDivs = document.getElementById('results').getElementsByTagName('div');
                for( i=0; i< childDivs.length; i++ )
                {
                    var childDiv = childDivs[i];
                    if(childDiv.id != divName)
                    {
                        var resultsDiv = document.getElementById(childDiv.id);
                        resultsDiv.setAttribute('class', 'hidden');
                    }          
                }
            }
            else
            {
                showAllRowsColumn(dimensions, choices)
            }
        }
    }
    
    </script>
    """
    return js


def preporcessResults3(results, folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique, stat):
    data=[]
    allRes =''
    
    for dataDetail0 in results:
        for key0, val0 in dataDetail0.items():
            if isinstance(val0, (list)):
                for dataDetail1 in val0:
                    for key1, val1 in dataDetail1.items():
                        if isinstance(val1, (list)):
                            for dataDetail2 in val1:
                                    for key2, val2 in dataDetail2.items():
                                        if isinstance(val2, (list)):
                                            for dataDetail3 in val2:
                                                oneRes=[]
                                                oneRes.append(dataDetail0['genome'])
                                                oneRes.append(dataDetail1['folderName1'])
                                                oneRes.append(dataDetail2['folderName2'])
                                                oneRes.append(dataDetail3['refTrackName'])
                                                oneRes.append(dataDetail3['data'][stat])
                                                data.append(oneRes)
    allRes += createAllTables3(data, folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
    #createAllTables(data, folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
    
    return allRes


def resultEmpty(resultPart1, folder, resultPartAll1):
    
    if depth(folder) == 0:
        if folder == resultPart1[0]:
            try:
                resultPartAll1.append(resultPart1[1])
            except IndexError:
                resultPartAll1.append('-')
    
    if depth(folder) == 1:
        for numfV3U in range(0, len(folder)):
            i=0
            if resultPart1:
                for numEl in range(0, len(resultPart1)):
                    if resultPart1[numEl][0]==folder[numfV3U]:
                        try:
                            resultPartAll1.append(resultPart1[numEl][1])
                        except IndexError:
                            resultPartAll1.append('-')
                    else:
                        i+=1
                    if i == len(resultPart1):
                        resultPartAll1.append('-')
            else:
                resultPartAll1.append('-')
    return resultPartAll1

def sumCalc(first, second):
    
    
    third=[]
    a = len(first)
    b = int(0)
    while True:
        x = first[b]
        y = second[b]
        if x=='-':
            x=0
        if y=='-':
            y=0
        ans = x + y
        third.append(ans)
        b = b + 1
        if b == a:
            break
    return third

def calculateSumAmongElements(result3, newHeader):
    resultSum=[]         
    
    if depth(result3)==2:
        resultSum = [0 for i in range(1, len(result3[0]))]
        for numSum3 in range(0, len(result3)):
            resultSum = sumCalc(resultSum, result3[numSum3][1:])
        resultSum.insert(0, newHeader)
        
    
    if depth(result3)==3:
        for numEl in range(0, len(result3[0])):
            resSum3 = [0 for i in range(1, len(result3[0][0]))]
            for numSum3 in range(0, len(result3)):
                resSum3 = sumCalc(resSum3, result3[numSum3][numEl][1:])
            resSum3.insert(0, newHeader[numEl])
            resultSum.append(resSum3)
    
    return resultSum


def calculateForSelectedRes(result3, newHeader):
    resultSum=[]         
    
    if depth(result3)==2:
        for elNum in range(0, len(newHeader)):
            resultSumPart = [0 for i in range(1, len(result3[0]))]
            for numSum3 in range(0, len(result3)):
                if numSum3%len(newHeader)==elNum:
                    resultSumPart = sumCalc(resultSumPart, result3[numSum3][1:])
            resultSumPart.insert(0, newHeader[elNum])
            resultSum.append(resultSumPart)
    
    if depth(result3)==3:
        for elNum in range(0, len(newHeader)):
            resultSumPart=[]
            resultSumPart = [0 for i in range(1, len(result3[0][0]))]
            for numSum3 in range(0, len(result3)):
                for numSum33 in range(0, len(result3[numSum3])):
                    if numSum33%len(newHeader)==elNum:
                        resultSumPart = sumCalc(resultSumPart, result3[numSum3][numSum33][1:])
            resultSumPart.insert(0, newHeader[elNum])
            resultSum.append(resultSumPart)
    
    
    return resultSum


def calculateSum(result3, newHeader):
    
    resultSum=[]
    
    if depth(result3)==2:
        resSum3 = [0 for i in range(1, len(result3[0]))]
        for numSum3 in range(0, len(result3)):
            resSum3 = sumCalc(resSum3, result3[numSum3][1:])
        resSum3.insert(0, 'Sum')
        resultSum.append(resSum3)
    
    if depth(result3)==3:
        for numSum3 in range(0, len(result3)):
            resSum3 = [0 for i in range(1, len(result3[numSum3][0]))]
            for numSum33 in range(0, len(result3[numSum3])):
                resSum3 = sumCalc(resSum3,result3[numSum3][numSum33][1:])
            resSum3.insert(0, newHeader[numSum3])
            resultSum.append(resSum3)
            
    if depth(result3)==4:
        for numSum3 in range(0, len(result3)):
            resultSumPart=[]
            for numSum33 in range(0, len(result3[numSum3])):
                resSum3 = [0 for i in range(1, len(result3[numSum3][0][0]))]
                for numSum333 in range(0, len(result3[numSum3][numSum33])):
                    resSum3 = sumCalc(resSum3,result3[numSum3][numSum33][numSum333][1:])
                resSum3.insert(0, newHeader[numSum33])
                resultSumPart.append(resSum3)
            resultSum.append(resultSumPart)
            
    return resultSum

def calculateOwnSum(result3, newHeader):
    
    resultSum=[]
    
    if depth(result3)==2:
        for numSum3 in range(0, len(result3)):
            resultPartSum= [newHeader[numSum3]]
            sum3=0
            for numSum33 in range(0, len(result3[numSum3])):
                if isinstance(result3[numSum3][numSum33], int):
                    sum3+=result3[numSum3][numSum33]
            resultPartSum.append(sum3)
            resultSum.append(resultPartSum)
        
    if depth(result3)==3:
        for numSum3 in range(0, len(result3)):
            resultPartSum= [newHeader[numSum3]]
            for numSum33 in range(0, len(result3[numSum3])):
                sum3=0
                for numSum333 in range(0, len(result3[numSum3][numSum33])):
                    if isinstance(result3[numSum3][numSum33][numSum333], int):
                        sum3 += result3[numSum3][numSum33][numSum333]
                resultPartSum.append(sum3)
            resultSum.append(resultPartSum)
            
            
    if depth(result3)==4:
        for numSum3 in range(0, len(result3)):
            resultPart33=[]
            for numSum33 in range(0, len(result3[numSum3])):
                resultPart3=[]
                resultPart3.append(newHeader[numSum33])
                for numSum333 in range(0, len(result3[numSum3][numSum33])):
                    sum3=0
                    for numSum3333 in range(0, len(result3[numSum3][numSum33][numSum333])):
                        if isinstance(result3[numSum3][numSum33][numSum333][numSum3333], int):
                            sum3 += result3[numSum3][numSum33][numSum333][numSum3333]
                    resultPart3.append(sum3)
                resultPart33.append(resultPart3)
            resultSum.append(resultPart33)
            
    return resultSum


def calculateOwnOwnSum(result3):
    
    resultSum=[]
    
    if depth(result3)==2:
        sum3=0
        resultSum= ['Sum']
        resSum3 = [0 for i in range(1, len(result3[0]))]
        for numSum3 in range(0, len(result3)):
            for numSum33 in range(0, len(result3[numSum3])):
                if isinstance(result3[numSum3][numSum33], int):
                    sum3 += result3[numSum3][numSum33]
        resultSum.append(sum3)
    
    
    
    if depth(result3)==3:
        resultPartSum= ['Sum']
        for numSum3 in range(0, len(result3)):
            sum3=0
            for numSum33 in range(0, len(result3[numSum3])):
                for numSum333 in range(0, len(result3[numSum3][numSum33])):
                    if isinstance(result3[numSum3][numSum33][numSum333], int):
                        sum3 += result3[numSum3][numSum33][numSum333]
            resultPartSum.append(sum3)
        resultSum.append(resultPartSum)
            
            
    if depth(result3)==4:
        for numSum3 in range(0, len(result3)):
            resultPart3=['Sum']
            for numSum33 in range(0, len(result3[numSum3])):
                sum3=0
                for numSum333 in range(0, len(result3[numSum3][numSum33])):
                    for numSum3333 in range(0, len(result3[numSum3][numSum33][numSum333])):
                        if isinstance(result3[numSum3][numSum33][numSum333][numSum3333], int):
                            sum3 += result3[numSum3][numSum33][numSum333][numSum3333]
                resultPart3.append(sum3)
            resultSum.append(resultPart3)
            
    return resultSum

'''
watpie ale moze sie przyda
def calculateOwnOwnOwnSum(result3):
    
    resultSum=[]            
            
    if depth(result3)==4:
        resultPart3=['SumOwnOwnOwn']
        for numSum3 in range(0, len(result3)):
            sum3=0
            for numSum33 in range(0, len(result3[numSum3])):
                for numSum333 in range(0, len(result3[numSum3][numSum33])):
                    for numSum3333 in range(0, len(result3[numSum3][numSum33][numSum333])):
                        if isinstance(result3[numSum3][numSum33][numSum333][numSum3333], int):
                            sum3 += result3[numSum3][numSum33][numSum333][numSum3333]
            resultPart3.append(sum3)
        resultSum.append(resultPart3)
            
    return resultSum
'''


def calculateAllSum(result3, newHeader=[]):
    
    resultSum=[]
    
    if depth(result3)==2:
        resSum3 = [0 for i in range(1, len(result3[0]))]
        for numSum3 in range(0, len(result3)):
            resSum3 = sumCalc(resSum3, result3[numSum3][1:])
        
        sum3=0
        for res3 in resSum3:
            sum3+=res3
        resultSum.insert(0, 'Sum')
        resultSum.append(sum3)
    
    if depth(result3)==3:
        resSum3 = [0 for i in range(1, len(result3[0][0]))]
        for numSum3 in range(0, len(result3)):
            for numSum33 in range(0, len(result3[numSum3])):
                resSum3 = sumCalc(resSum3,result3[numSum3][numSum33][1:])
        resSum3.insert(0, 'Sum')
        resultSum.append(resSum3)
    
    if depth(result3)==4:
        for numSum3 in range(0, len(result3)):
            resSum3 = [0 for i in range(1, len(result3[0][0][0]))]
            for numSum33 in range(0, len(result3[numSum3])):
                for numSum333 in range(0, len(result3[numSum3][numSum33])):
                    resSum3 = sumCalc(resSum3,result3[numSum3][numSum33][numSum333][1:])
            resSum3.insert(0, newHeader[numSum3])
            resultSum.append(resSum3)
            
    return resultSum

def calculateAllAllSum(result3):
    
    resultSum=[] 
    if depth(result3)==3:
        resSum3 = [0 for i in range(1, len(result3[0][0]))]
        for numSum3 in range(0, len(result3)):
            for numSum33 in range(0, len(result3[numSum3])):
                resSum3 = sumCalc(resSum3,result3[numSum3][numSum33][1:])
        sum3=0
        for res3 in resSum3:
            sum3+=res3
        resultSum.insert(0, 'Sum')
        resultSum.append(sum3)
            
    if depth(result3)==4:
        resultSum.insert(0, 'Sum')
        for numSum3 in range(0, len(result3)):
            resSum3 = [0 for i in range(1, len(result3[0][0][0]))]
            for numSum33 in range(0, len(result3[numSum3])):
                for numSum333 in range(0, len(result3[numSum3][numSum33])):
                    resSum3 = sumCalc(resSum3,result3[numSum3][numSum33][numSum333][1:])
            sum3=0
            for res3 in resSum3:
                sum3+=res3
            resultSum.append(sum3)
            
    return resultSum
def calculateAllAllAllSum(result3):
    
    resultSum=[] 
            
    if depth(result3)==4:
        resultSum.insert(0, 'Sum')
        sum3=0
        for numSum3 in range(0, len(result3)):
            resSum3 = [0 for i in range(1, len(result3[0][0][0]))]
            for numSum33 in range(0, len(result3[numSum3])):
                for numSum333 in range(0, len(result3[numSum3][numSum33])):
                    resSum3 = sumCalc(resSum3,result3[numSum3][numSum33][numSum333][1:])
            for res3 in resSum3:
                sum3+=res3
        resultSum.append(sum3)
            
    return resultSum

def createAllTables3(data, folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique):
    
    allRes  =''
    #11111111
    i=0
    for d in data:
        allRes+= createResTable3([[1, folderValue0Unique.index(d[0]), 1, folderValue1Unique.index(d[1]), 1, folderValue2Unique.index(d[2]), 1, targetTrackFeatureTitles.index(d[3])], [d[0], d[1]], ['Track - ' + str(d[2]), 'Values'], [d[3], d[4]]], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        i+=1
    
    #2222222222
    for numfV0U in range(0, len(folderValue0Unique)):
        result3=[]
        for numfV1U in range(0, len(folderValue1Unique)):
            result2=[]
            resultPart3=[]
            for numfV2U in range(0, len(folderValue2Unique)):
                result1=[]
                header1=[folderValue0Unique[numfV0U], folderValue1Unique[numfV1U]]
                header3=[folderValue0Unique[numfV0U], folderValue1Unique]
                headerSum3 = [folderValue0Unique[numfV0U]]
                resultPart2=[]
                resultPartAll2=[folderValue2Unique[numfV2U]]
                resultPart35=[]
                resultPartAll35=[folderValue2Unique[numfV2U]]
                for numfV3U in range(0, len(targetTrackFeatureTitles)):
                    for d in data:
                        if d[0] == folderValue0Unique[numfV0U] and d[1] == folderValue1Unique[numfV1U] and d[2] == folderValue2Unique[numfV2U] and d[3] == targetTrackFeatureTitles[numfV3U]:
                            result1.append([d[3], d[4]])
                            resultPart2.append([d[3], d[4]])
                            resultPart35.append([d[3], d[4]])                    
                result2.append(resultEmpty(resultPart2, targetTrackFeatureTitles, resultPartAll2))  
                resultPart3.append(resultEmpty(resultPart35, targetTrackFeatureTitles, resultPartAll35))
                allRes+= createResTable3([[1, numfV0U, 1, numfV1U, 1, numfV2U, 2, -1], header1, ['Track', folderValue2Unique[numfV2U]], result1], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
                allRes+= createResTable3([[1, numfV0U, 1, numfV1U, 1, numfV2U, 3, -1], header1, ['Track', folderValue2Unique[numfV2U]], calculateSum(result1, 'HEADER')], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
            result3.append(resultPart3)
            allRes+= createResTable3([[1, numfV0U, 1, numfV1U, 2, -1, 2, -1], header1, ['Track'] + targetTrackFeatureTitles, result2], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
            allRes+= createResTable3([[1, numfV0U, 1, numfV1U, 3, -1, 2, -1], header1, ['Track'] + targetTrackFeatureTitles, calculateSum(result2, ['HEADER'])], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
            allRes+= createResTable3([[1, numfV0U, 1, numfV1U, 2, -1, 3, -1], header1, ['Track', 'Values'], calculateOwnSum(result2, folderValue2Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
            allRes+= createResTable3([[1, numfV0U, 1, numfV1U, 3, -1, 3, -1], header1, ['Track', 'Values'], calculateOwnOwnSum(result2)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[1, numfV0U, 3, -1, 2, -1, 2, -1], headerSum3, ['Track'] + targetTrackFeatureTitles, calculateSumAmongElements(result3, folderValue2Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[1, numfV0U, 3, -1, 3, -1, 3, -1], headerSum3, ['Track', 'Sum'], calculateAllAllSum(result3)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[1, numfV0U, 3, -1, 3, -1, 2, -1], headerSum3, ['Track'] + targetTrackFeatureTitles, calculateAllSum(result3)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[1, numfV0U, 2, -1, 3, -1, 2, -1], headerSum3, ['Track'] + targetTrackFeatureTitles, calculateSum(result3, folderValue1Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[1, numfV0U, 2, -1, 2, -1, 2, -1], header3, ['Track'] + targetTrackFeatureTitles, result3], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[1, numfV0U, 2, -1, 2, -1, 3, -1], headerSum3, ['Track'] + folderValue2Unique, calculateOwnSum(result3, folderValue1Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[1, numfV0U, 3, -1, 2, -1, 3, -1], headerSum3, ['Track'] + folderValue2Unique, calculateSum(calculateOwnSum(result3, folderValue1Unique), folderValue1Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[1, numfV0U, 2, -1, 3, -1, 3, -1], headerSum3, ['Track'] + folderValue1Unique, calculateOwnOwnSum(result3)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        
    #333333
    result4=[]
    header4=[]
    headerSum4=[[''],targetTrackFeatureTitles]
    for numfV3U in range(0, len(targetTrackFeatureTitles)):
        result3=[]
        result5=[]
        resultPart47=[]
        headerSum5 = [targetTrackFeatureTitles[numfV3U]]
        for numfV1U in range(0, len(folderValue1Unique)):
            result2=[]
            header2=[folderValue1Unique[numfV1U], targetTrackFeatureTitles[numfV3U]]
            resultPart3=[]
            resultPart45=[]
            resultPart3.append(folderValue1Unique[numfV1U])
            for numfV2U in range(0, len(folderValue2Unique)):
                result1=[]
                header1=[folderValue1Unique[numfV1U], folderValue2Unique[numfV2U]]
                resultPart2=[]
                resultPartAll2=[folderValue2Unique[numfV2U]]
                resultPart35=[]
                resultPart43=[]
                resultPartAll4=[folderValue2Unique[numfV2U]]
                resultPart35.append(folderValue2Unique[numfV2U])
                for numfV0U in range(0, len(folderValue0Unique)):
                    resultPart1=[]
                    resultPart1.append(folderValue0Unique[numfV0U])
                    resultPartAll1=[folderValue0Unique[numfV0U]]
                    for d in data:
                        if d[0] == folderValue0Unique[numfV0U] and d[1] == folderValue1Unique[numfV1U] and d[2] == folderValue2Unique[numfV2U] and d[3] == targetTrackFeatureTitles[numfV3U]:
                            resultPart1.append(d[4])
                            resultPart2.append([d[0], d[4]])
                            resultPart35.append(d[4])
                            resultPart43.append([d[0], d[4]])
                            if [d[1], d[3]] not in header4:
                                header4.append([d[1], d[3]])
                    result1.append(resultEmpty(resultPart1, folderValue0Unique[numfV0U], resultPartAll1))
                result2.append(resultEmpty(resultPart2, folderValue0Unique, resultPartAll2))
                allRes+= createResTable3([[2, -1, 1, numfV1U, 1, numfV2U, 1, numfV3U], header1, ['Track', targetTrackFeatureTitles[numfV3U]], result1], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
                allRes+= createResTable3([[3, -1, 1, numfV1U, 1, numfV2U, 1, numfV3U], header1, ['Track', targetTrackFeatureTitles[numfV3U]], calculateSum(result1, 'HEADER')], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
                resultPart3.append(resultPart35)
                resultPart45.append(resultEmpty(resultPart43, folderValue0Unique, resultPartAll4))
            resultPart47.append(resultPart45)
            result3.append(resultPart3)
            allRes+= createResTable3([[3, -1, 1, numfV1U, 3, -1, 1, numfV3U], header2, ['Track', 'Values'], calculateAllSum(result2)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
            allRes+= createResTable3([[2, -1, 1, numfV1U, 3, -  1, 1, numfV3U], header2, ['Track'] + folderValue0Unique, calculateSum(result2, 'HEADER')], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
            allRes+= createResTable3([[2, -1, 1, numfV1U, 2, -1, 1, numfV3U], header2, ['Track'] + folderValue0Unique, result2], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
            allRes+= createResTable3([[3, -1, 1, numfV1U, 2, -1, 1, numfV3U], header2, ['Track', 'Values'], calculateOwnSum(result2, folderValue2Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
            result5.append(result2)
        result4.append(resultPart47)
        allRes+= createResTable3([[3, -1, 2, -1, 2, -1, 1, numfV3U], headerSum5, ['Track'] + folderValue2Unique, calculateOwnSum(result5, folderValue1Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
    allRes+= createResTable3([[2, -1, 2, -1, 2, -1, 2, -1], header4, ['Track'] + folderValue0Unique, result4], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
    allRes+= createResTable3([[3, -1, 3, -1, 3, -1, 3, -1], ['All tracks'], ['Track', 'Sum'], calculateAllAllAllSum(result4)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
    allRes+= createResTable3([[3, -1, 3, -1, 3, -1, 2, -1], ['every item from ' + str(FIELD_NAME4)], ['Track'] + targetTrackFeatureTitles, calculateAllAllSum(result4)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
    
    allRes+= createResTable3([[2, -1, 2, -1, 3, -1, 2, -1], headerSum4, ['Track'] + folderValue0Unique, calculateSum(result4, folderValue1Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
    allRes+= createResTable3([[3, -1, 2, -1, 2, -1, 2, -1], headerSum4, ['Track'] + folderValue2Unique, calculateOwnSum(result4, folderValue1Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
    allRes+= createResTable3([[3, -1, 2, -1, 2, -1, 3, -1], ['every item from ' + str(FIELD_NAME2), 'every itme from  ' + str(FIELD_NAME3)], ['Track'] + folderValue2Unique, calculateSumAmongElements(calculateOwnSum(result4, folderValue1Unique), folderValue1Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
    allRes+= createResTable3([[3, -1, 3, -1, 2, -1, 3, -1], ['every item from ' + str(FIELD_NAME3)], ['Track'] + folderValue2Unique, calculateSum((calculateSumAmongElements(calculateOwnSum(result4, folderValue1Unique), folderValue1Unique)), folderValue1Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
    allRes+= createResTable3([[3, -1, 2, -1, 3, -1, 2, -1], ['every item from ' + str(FIELD_NAME2), 'every itme from ' + str(FIELD_NAME4)], ['Track'] + folderValue1Unique, calculateOwnOwnSum(result4)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
    
    
    allRes+= createResTable3([[2, -1, 3, -1, 3, -1, 2, -1], ['every item from ' + str(FIELD_NAME1), 'every item from ' + str(FIELD_NAME4)], ['Track'] + folderValue0Unique, calculateAllSum(result4, targetTrackFeatureTitles)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
    allRes+= createResTable3([[2, -1, 3, -1, 3, -1, 3, -1], ['every item from ' + str(FIELD_NAME1)], ['Track'] + folderValue0Unique, calculateSumAmongElements(calculateAllSum(result4, targetTrackFeatureTitles), 'Sum')], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
    allRes+= createResTable3([[3, -1, 3, -1, 2, -1, 2, -1], ['every item from ' + str(FIELD_NAME3), 'every item from ' + str(FIELD_NAME4)], ['Track'] + folderValue2Unique, calculateSum(calculateOwnSum(result4, folderValue1Unique), targetTrackFeatureTitles)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
    allRes+= createResTable3([[3, -1, 2, -1, 3, -1, 3, -1], ['every item from ' + str(FIELD_NAME2)], ['Track'] + folderValue1Unique, calculateSum(calculateOwnOwnSum(result4), 'HEADER')], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
    allRes+= createResTable3([[2, -1, 2, -1, 3, -1, 3, -1], ['every item from ' + str(FIELD_NAME1), 'every item from ' + str(FIELD_NAME2)], ['Track'] + folderValue0Unique, calculateForSelectedRes(calculateSum(result4, folderValue2Unique), folderValue1Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
    
    
    
    
    #444444444
    for numfV0U in range(0, len(folderValue0Unique)):
        result3=[]
        for numfV3U in range(0, len(targetTrackFeatureTitles)):
            result2=[]
            resultPart3=[]
            for numfV2U in range(0, len(folderValue2Unique)):
                result1=[]
                header1=[folderValue0Unique[numfV0U], targetTrackFeatureTitles[numfV3U]]
                header3=[folderValue0Unique[numfV0U], targetTrackFeatureTitles]
                resultPart2=[]
                resultPartAll2=[folderValue2Unique[numfV2U]]
                resultPart35=[]
                resultPartAll35=[folderValue2Unique[numfV2U]]
                for numfV1U in range(0, len(folderValue1Unique)):
                    for d in data:
                        if d[0] == folderValue0Unique[numfV0U] and d[1] == folderValue1Unique[numfV1U] and d[2] == folderValue2Unique[numfV2U] and d[3] == targetTrackFeatureTitles[numfV3U]:
                            result1.append([d[1], d[4]])
                            resultPart2.append([d[1], d[4]])
                            resultPart35.append([d[1], d[4]])                        
                result2.append(resultEmpty(resultPart2, folderValue1Unique, resultPartAll2))  
                resultPart3.append(resultEmpty(resultPart35, folderValue1Unique, resultPartAll35))
                allRes+= createResTable3([[1, numfV0U, 2, -1, 1, numfV2U, 1, numfV3U], header1, ['Track', folderValue2Unique[numfV2U]], result1], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
                allRes+= createResTable3([[1, numfV0U, 3, -1, 1, numfV2U, 1, numfV3U], header1, ['Track', folderValue2Unique[numfV2U]], calculateSum(result1, folderValue2Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
            result3.append(resultPart3)
            allRes+= createResTable3([[1, numfV0U, 3, -1, 3, -1, 1, numfV3U], header1, ['Track'] + folderValue1Unique, result2], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
            allRes+= createResTable3([[1, numfV0U, 2, -1, 3, -1, 1, numfV3U], header1, ['Track'] + folderValue1Unique, calculateSum(result2, folderValue0Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
            allRes+= createResTable3([[1, numfV0U, 2, -1, 2, -1, 1, numfV3U], header1, ['Track'] + folderValue1Unique, result3], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
            allRes+= createResTable3([[1, numfV0U, 3, -1, 2, -1, 1, numfV3U], header1, ['Track', 'Sum'], calculateOwnSum(result2, folderValue2Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
    
    #5555555  
    for numfV0U in range(0, len(folderValue0Unique)):
        result3=[]
        for numfV1U in range(0, len(folderValue1Unique)):
            result2=[]
            resultPart3=[]
            for numfV3U in range(0, len(targetTrackFeatureTitles)):
                result1=[]
                header1=[folderValue0Unique[numfV0U], folderValue1Unique[numfV1U]]
                header3=[folderValue0Unique[numfV0U], folderValue1Unique]
                resultPart2=[]
                resultPartAll2=[targetTrackFeatureTitles[numfV3U]]
                resultPart35=[]
                resultPartAll35=[targetTrackFeatureTitles[numfV3U]]
                for numfV2U in range(0, len(folderValue2Unique)):
                    for d in data:
                        if d[0] == folderValue0Unique[numfV0U] and d[1] == folderValue1Unique[numfV1U] and d[2] == folderValue2Unique[numfV2U] and d[3] == targetTrackFeatureTitles[numfV3U]:
                            result1.append([d[2], d[4]])
                            resultPart2.append([d[2], d[4]])
                            resultPart35.append([d[2], d[4]])                       
                result2.append(resultEmpty(resultPart2, folderValue2Unique, resultPartAll2))  
                resultPart3.append(resultEmpty(resultPart35, folderValue2Unique, resultPartAll35) )
                allRes+= createResTable3([[1, numfV0U, 1, numfV1U, 3, -1, 1, numfV3U], header1, ['Track', targetTrackFeatureTitles[numfV3U]], calculateSum(result1, 'HEADER')], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
                allRes+= createResTable3([[1, numfV0U, 1, numfV1U, 2, -1, 1, numfV3U], header1, ['Track', targetTrackFeatureTitles[numfV3U]], result1], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
            result3.append(resultPart3)
           
    
    #666666666    
    result3=[]
    headerSum3=[[''],targetTrackFeatureTitles]
    for numfV3U in range(0, len(targetTrackFeatureTitles)):
        result2=[]
        for numfV1U in range(0, len(folderValue1Unique)):
            header2=[targetTrackFeatureTitles[numfV3U], folderValue1Unique]
            headerSum2=[targetTrackFeatureTitles[numfV3U]]
            resultPart22=[]
            for numfV0U in range(0, len(folderValue0Unique)):
                resultPart2=[]
                resultPartAll2=[folderValue0Unique[numfV0U]]
                for numfV2U in range(0, len(folderValue2Unique)):
                    for d in data:
                        if d[0] == folderValue0Unique[numfV0U] and d[1] == folderValue1Unique[numfV1U] and d[2] == folderValue2Unique[numfV2U] and d[3] == targetTrackFeatureTitles[numfV3U]:
                            resultPart2.append([d[2], d[4]])
                resultPart22.append(resultEmpty(resultPart2, folderValue2Unique, resultPartAll2))
            result2.append(resultPart22)
        allRes+= createResTable3([[3, -1, 3, -1, 3, -1, 1, numfV3U], headerSum2, ['Track','Sum'], calculateAllAllSum(result2)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[3, -1, 3, -1, 2, -1, 1, numfV3U], headerSum2, ['Track'] + folderValue2Unique, calculateAllSum(result2)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[3, -1, 2, -1, 2, -1, 1, numfV3U], headerSum2, ['Track'] + folderValue2Unique, calculateSum(result2, folderValue2Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[2, -1, 2, -1, 2, -1, 1, numfV3U], header2, ['Track'] + folderValue2Unique, result2], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
       
        allRes+= createResTable3([[2, -1, 3, -1, 2, -1, 1, numfV3U], headerSum2, ['Track'] + folderValue2Unique, calculateSumAmongElements(result2, folderValue0Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[2, -1, 2, -1, 3, -1, 1, numfV3U], headerSum2, ['Track'] + folderValue0Unique, calculateOwnSum(result2, folderValue1Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[2, -1, 3, -1, 3, -1, 1, numfV3U], headerSum2, ['Track'] + folderValue0Unique, calculateSum(calculateOwnSum(result2, folderValue1Unique), folderValue1Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[3, -1, 2, -1, 3, -1, 1, numfV3U], headerSum2, ['Track'] + folderValue1Unique, calculateOwnOwnSum(result2)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        result3.append(calculateSumAmongElements(result2, folderValue0Unique))
    allRes+= createResTable3([[2, -1, 3, -1, 2, -1, 2, -1], headerSum3, ['Track'] + folderValue2Unique, result3], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)        
    allRes+= createResTable3([[2, -1, 3, -1, 2, -1, 3, -1], ['every item from ' + str(FIELD_NAME1), 'every item from ' + str(FIELD_NAME3)], ['Track'] + folderValue2Unique, calculateSumAmongElements(result3, folderValue0Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
    
    #777777
    headerSum3=[[''], folderValue1Unique]
    for numfV2U in range(0, len(folderValue2Unique)):
        result2=[]
        for numfV1U in range(0, len(folderValue1Unique)):
            header3=[folderValue1Unique[numfV1U], folderValue2Unique[numfV2U]]
            header2=[folderValue2Unique[numfV2U], folderValue1Unique]
            headerSum2=[folderValue2Unique[numfV2U]]
            resultPart22=[]
            result3=[]
            for numfV0U in range(0, len(folderValue0Unique)):
                resultPart2=[]
                resultPart3=[]
                resultPartAll2=[folderValue0Unique[numfV0U]]
                resultPartAll3=[folderValue0Unique[numfV0U]]
                for numfV3U in range(0, len(targetTrackFeatureTitles)):
                    for d in data:
                        if d[0] == folderValue0Unique[numfV0U] and d[1] == folderValue1Unique[numfV1U] and d[2] == folderValue2Unique[numfV2U] and d[3] == targetTrackFeatureTitles[numfV3U]:
                            resultPart2.append([d[3], d[4]])
                            resultPart3.append([d[3], d[4]])
                resultPart22.append(resultEmpty(resultPart2, targetTrackFeatureTitles, resultPartAll2))
                result3.append(resultEmpty(resultPart3, targetTrackFeatureTitles, resultPartAll3))
            result2.append(resultPart22)
            allRes+= createResTable3([[3, -1, 1, numfV1U, 1, numfV2U, 3, -1], header3, ['Track', 'Value'], calculateAllSum(result3)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
            allRes+= createResTable3([[3, -1, 1, numfV1U, 1, numfV2U, 2, -1], header3, ['Track'] + targetTrackFeatureTitles, calculateSum(result3, targetTrackFeatureTitles)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
            allRes+= createResTable3([[2, -1, 1, numfV1U, 1, numfV2U, 2, -1], header3, ['Track'] + targetTrackFeatureTitles, result3], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
            allRes+= createResTable3([[2, -1, 1, numfV1U, 1, numfV2U, 3, -1], header3, ['Track', 'Value'], calculateOwnSum(result3, folderValue0Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[3, -1, 3, -1, 1, numfV2U, 3, -1], headerSum2, ['Track', 'Value'], calculateAllAllSum(result2)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[3, -1, 3, -1, 1, numfV2U, 2, -1], headerSum2, ['Track'] + targetTrackFeatureTitles, calculateAllSum(result2)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[3, -1, 2, -1, 1, numfV2U, 2, -1], headerSum2, ['Track'] + targetTrackFeatureTitles, calculateSum(result2, folderValue1Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[2, -1, 2, -1, 1, numfV2U, 2, -1], header2, ['Track'] + targetTrackFeatureTitles, result2], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[2, -1, 3, -1, 1, numfV2U, 2, -1], headerSum2, ['Track'] + targetTrackFeatureTitles, calculateSumAmongElements(result2, folderValue0Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[2, -1, 2, -1, 1, numfV2U, 3, -1], headerSum3, ['Track'] + folderValue0Unique , calculateOwnSum(result2, folderValue1Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[3, -1, 2, -1, 1, numfV2U, 3, -1], headerSum2, ['Track'] + folderValue0Unique , calculateOwnOwnSum(result2)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[2, -1, 3, -1, 1, numfV2U, 3, -1], headerSum2, ['Track'] + folderValue0Unique , calculateSum(calculateOwnSum(result2, folderValue1Unique), folderValue0Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
    
    
    #88888
    for numfV2U in range(0, len(folderValue2Unique)):
        for numfV3U in range(0, len(targetTrackFeatureTitles)):
            header2=[folderValue2Unique[numfV2U], targetTrackFeatureTitles[numfV3U]]
            result2=[]
            for numfV0U in range(0, len(folderValue0Unique)):
                resultPart2=[]
                resultPartAll2=[folderValue0Unique[numfV0U]]
                for numfV1U in range(0, len(folderValue1Unique)):
                    for d in data:
                        if d[0] == folderValue0Unique[numfV0U] and d[1] == folderValue1Unique[numfV1U] and d[2] == folderValue2Unique[numfV2U] and d[3] == targetTrackFeatureTitles[numfV3U]:
                            resultPart2.append([d[1], d[4]])
                resultEmpty(resultPart2, folderValue1Unique, resultPartAll2)
                result2.append(resultPartAll2)
            allRes+= createResTable3([[3, -1, 3, -1, 1, numfV2U, 1, numfV3U], header2, ['Track', 'Value'], calculateAllSum(result2)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
            allRes+= createResTable3([[3, -1, 2, -1, 1, numfV2U, 1, numfV3U], header2, ['Track'] + folderValue1Unique, calculateSum(result2, targetTrackFeatureTitles)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
            allRes+= createResTable3([[2, -1, 2, -1, 1, numfV2U, 1, numfV3U], header2, ['Track'] + folderValue1Unique, result2], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
            allRes+= createResTable3([[2, -1, 3, -1, 1, numfV2U, 1, numfV3U], header2, ['Track', 'Sum'], calculateOwnSum(result2, folderValue0Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        
    #99999
    for numfV2U in range(0, len(folderValue2Unique)):
        for numfV0U in range(0, len(folderValue0Unique)):
            header2=[folderValue0Unique[numfV0U], folderValue2Unique[numfV2U]]
            result2=[]
            for numfV3U in range(0, len(targetTrackFeatureTitles)):
                resultPart2=[]
                resultPartAll2=[targetTrackFeatureTitles[numfV3U]]
                for numfV1U in range(0, len(folderValue1Unique)):
                    for d in data:
                        if d[0] == folderValue0Unique[numfV0U] and d[1] == folderValue1Unique[numfV1U] and d[2] == folderValue2Unique[numfV2U] and d[3] == targetTrackFeatureTitles[numfV3U]:
                            resultPart2.append([d[1], d[4]])
                resultEmpty(resultPart2, folderValue1Unique, resultPartAll2)
                result2.append(resultPartAll2)
            allRes+= createResTable3([[1, numfV0U, 3, -1, 1, numfV2U, 3, -1], header2, ['Track', 'Value'], calculateAllSum(result2)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)    
            allRes+= createResTable3([[1, numfV0U, 2, -1, 1, numfV2U, 3, -1], header2, ['Track'] + folderValue1Unique, calculateSum(result2, folderValue2Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
            allRes+= createResTable3([[1, numfV0U, 2, -1, 1, numfV2U, 2, -1], header2, ['Track'] + folderValue1Unique, result2], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
            allRes+= createResTable3([[1, numfV0U, 3, -1, 1, numfV2U, 2, -1], header2, ['Track', 'Sum'], calculateOwnSum(result2, targetTrackFeatureTitles)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
    
    #101010
    headerSum4=[[''],folderValue1Unique]
    result4=[]
    for numfV1U in range(0, len(folderValue1Unique)):
        result2=[]
        for numfV2U in range(0, len(folderValue2Unique)):
            header2=[folderValue1Unique[numfV1U], folderValue2Unique]
            headerSum2=[folderValue1Unique[numfV1U]]
            resultPart22=[]
            for numfV0U in range(0, len(folderValue0Unique)):
                resultPart2=[]
                resultPartAll2=[folderValue0Unique[numfV0U]]
                for numfV3U in range(0, len(targetTrackFeatureTitles)):
                    for d in data:
                        if d[0] == folderValue0Unique[numfV0U] and d[1] == folderValue1Unique[numfV1U] and d[2] == folderValue2Unique[numfV2U] and d[3] == targetTrackFeatureTitles[numfV3U]:
                            resultPart2.append([d[3], d[4]])
                resultPart22.append(resultEmpty(resultPart2, targetTrackFeatureTitles, resultPartAll2))
                result3.append(resultEmpty(resultPart3, targetTrackFeatureTitles, resultPartAll3))
            result2.append(resultPart22)
        allRes+= createResTable3([[2, -1, 1, numfV1U, 2, -1, 2, -1], header2, ['Track'] + targetTrackFeatureTitles, result2], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[3, -1, 1, numfV1U, 3, -1, 2, -1], headerSum2, ['Track'] + targetTrackFeatureTitles, calculateAllSum(result2)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[3, -1, 1, numfV1U, 3, -1, 3, -1], headerSum2, ['Track', 'Value'], calculateAllAllSum(result2)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[3, -1, 1, numfV1U, 2, -1, 2, -1], headerSum2, ['Track'] + targetTrackFeatureTitles, calculateSum(result2, folderValue2Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[3, -1, 1, numfV1U, 2, -1, 3, -1], headerSum2, ['Track', 'Value'], calculateOwnSum(calculateSum(result2, folderValue2Unique), folderValue2Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[2, -1, 1, numfV1U, 2, -1, 3, -1], headerSum2, ['Track'] + folderValue0Unique , calculateOwnSum(result2, folderValue2Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        #allRes+= createResTable3([[2, -1, 1, numfV1U, 3, -1, 3, -1], headerSum2, ['Track'] + folderValue2Unique , calculateOwnOwnSum(result2)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[2, -1, 1, numfV1U, 3, -1, 3, -1], headerSum2, ['Track', 'Sum'], calculateOwnSum(calculateSumAmongElements(result2, folderValue0Unique), folderValue0Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        allRes+= createResTable3([[2, -1, 1, numfV1U, 3, -1, 2, -1], headerSum2, ['Track'] + targetTrackFeatureTitles, calculateSumAmongElements(result2, folderValue0Unique)], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
        result4.append(calculateOwnSum(result2, folderValue2Unique))
    allRes += createResTable3([[2, -1, 2, -1, 2, -1, 3, -1], headerSum4, ['Track'] + folderValue0Unique , result4], folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique)
    
    return allRes

def createResTable3(res, folderValue1Unique, folderValue2Unique, targetTrackFeatureTitles, folderValue0Unique):

    htmlCore = HtmlCore()
    
    header='For: '
    if depth(res[1]) == 1:
        for el in res[1]:
            header += ' ' + str(el)
    
    if depth(res[3]) == 1:
        htmlCore.divBegin(res[0], 'hidden')
        htmlCore.header(header) 
        htmlCore.tableHeader(res[2], sortable=True, tableId=res[0])
        htmlCore.tableLine(res[3])
        htmlCore.tableFooter()
        htmlCore.divEnd()    
    
    if depth(res[3]) == 2:
        htmlCore.divBegin(res[0], 'hidden')
        htmlCore.header(header) 
        htmlCore.tableHeader(res[2], sortable=True, tableId=res[0])
        for tab in res[3]:
            htmlCore.tableLine(tab)
        htmlCore.tableFooter()
        htmlCore.divEnd()
        
    if depth(res[3]) == 3:
        htmlCore.divBegin(res[0], 'hidden')
        for elVal in range(0, len(res[3])):
            htmlCore.header('For ' + str(res[1][1][elVal])) 
            htmlCore.tableHeader(res[2], sortable=True, tableId=res[0])
            for row in res[3][elVal]:
                htmlCore.tableLine(row)
            htmlCore.tableFooter()
        htmlCore.divEnd()
        
    
    if depth(res[3]) == 4:
        countEl=0
        htmlCore.divBegin(res[0], 'hidden')
        for elVal in range(0, len(res[3])):
            for elVal1 in range(0, len(res[3][elVal])):
                htmlCore.header('For ' + str(res[1][countEl][0]) + ' ' + str(res[1][countEl][1])) 
                htmlCore.tableHeader(res[2], sortable=True, tableId=res[0])
                countEl+=1
                for row in res[3][elVal][elVal1]:
                    htmlCore.tableLine(row)
                htmlCore.tableFooter()
        htmlCore.divEnd()
        
    return str(htmlCore)
