from itertools import *
import json

class vis(object):
    count =0
    def __init__(self, height=400):
        #self.__class__.count +=1
        self.__class__.count =1
        self._height=height
        self._interactionNumberStart = 0
        self._interactionNumberEnd = 0
    
    
    def _addLib(self):
        return """ 
                <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
                <script src="https://code.highcharts.com/highcharts.js"></script>
                <script src="http://code.highcharts.com/modules/data.js"></script>
                <script src="http://code.highcharts.com/modules/heatmap.js"></script>
                <script src="//code.highcharts.com/modules/exporting.js"></script>
                <script src="https://raw.github.com/briancray/tooltipsy/master/tooltipsy.min.js"></script>
                <script src="http://code.highcharts.com/modules/exporting.js"></script>
                <script type="text/javascript" src="http://canvg.googlecode.com/svn/trunk/canvg.js"></script>
                
                """
    def _addStyle(self):
        return """
        <style>
        .tooltipsy {
            margin-left:50%;
            padding: 8px;
            float:right;
            max-width: 500px;
            color: #FFFFFF;
            background: rgba(119,136,153,0.95);
            border: 1px solid silver;
            border-radius: 3px;
            box-shadow: 1px 1px 2px #888;
            }
        .highcharts-tooltip>span {
            background: rgba(255,255,255,0.85);
            border: 1px solid silver;
            border-radius: 3px;
            box-shadow: 1px 1px 2px #888;
            padding: 8px;
            z-index: 2;
           }
        </style>
        """
    def _themePlot(self):
        return """
        /**
 * Sand-Signika theme for Highcharts JS
 * @author Torstein Honsi
 */

// Load the fonts
Highcharts.createElement('link', {
   href: '//fonts.googleapis.com/css?family=Signika:400,700',
   rel: 'stylesheet',
   type: 'text/css'
}, null, document.getElementsByTagName('head')[0]);

// Add the background image to the container
Highcharts.wrap(Highcharts.Chart.prototype, 'getContainer', function (proceed) {
   proceed.call(this);
   this.container.style.background = 'url(http://www.highcharts.com/samples/graphics/sand.png)';
});


Highcharts.theme = {
   colors: ["#f45b5b", "#8085e9", "#8d4654", "#7798BF", "#aaeeee", "#ff0066", "#eeaaee",
      "#55BF3B", "#DF5353", "#7798BF", "#aaeeee"],
   chart: {
      backgroundColor: null,
      style: {
         fontFamily: "Signika, serif"
      }
   },
   title: {
      style: {
         color: 'black',
         fontSize: '16px',
         fontWeight: 'bold'
      }
   },
   subtitle: {
      style: {
         color: 'black'
      }
   },
   tooltip: {
      borderWidth: 0
   },
   legend: {
      itemStyle: {
         fontWeight: 'bold',
         fontSize: '13px'
      }
   },
   xAxis: {
      labels: {
         style: {
            color: '#6e6e70',
            fontSize:'9px'
         }
      }
   },
   yAxis: {
      labels: {
         style: {
            color: '#6e6e70'
         }
      }
   },
   plotOptions: {
      series: {
         shadow: true
      },
      candlestick: {
         lineColor: '#404048'
      },
      map: {
         shadow: false
      }
   },

   // Highstock specific
   navigator: {
      xAxis: {
         gridLineColor: '#D0D0D8'
      }
   },
   rangeSelector: {
      buttonTheme: {
         fill: 'white',
         stroke: '#C0C0C8',
         'stroke-width': 1,
         states: {
            select: {
               fill: '#D0D0D8'
            }
         }
      }
   },
   scrollbar: {
      trackBorderColor: '#C0C0C8'
   },

   // General
   background2: '#E0E0E8'
   
};

// Apply the theme
Highcharts.setOptions(Highcharts.theme);
    
    """
    def addLoadPage(self):
        return """
        <script>
        
        
            
            function loadPage() 
            { 
            
            
            document.getElementById("showReads").checked=false;
            document.getElementById("legendTable").style.display = "none";
            
            var e = document.getElementById("selectMismatcheslist");
            document.getElementById("selectMismatcheslist").checked = false;
            document.getElementById("selectStatisticList").checked = false;
            
            var selVal=0;
            
            
            //var selVal = e.options[e.selectedIndex].value;
            
           
                newBox='';
                document.getElementById(newBox.concat('container_', selVal)).style.display = "block";
                
                
                var chboxs = document.getElementsByName("fileListPieChart");
                
                var j=0;
                for(var i=0;i<chboxs.length;i++) { 
                chboxs[i].checked = false;
                }    
                
            } 
            
            </script>
            """
    def addLoadPagePie(self):
        return """
        <script>
        
        
            
            function loadPagePie() 
            { 
            
             document.getElementById("legendTable").style.display = "none";
                 
                
                var chboxs = document.getElementsByName("fileListPieChart");
                
                var j=0;
                for(var i=0;i<chboxs.length;i++) { 
                chboxs[i].checked = false;
                }    
                
            } 
            
            </script>
            """
    def addLoadPageHistogram(self):
        return """
        <script>
        
        
            
            function loadPageHistogram() 
            { 
            
                 
                
                var chboxs = document.getElementsByName("fileListHistogram");
                
                var j=0;
                for(var i=0;i<chboxs.length;i++) { 
                chboxs[i].checked = false;
                }    
                
            } 
            
            </script>
            """
            
            
    def addShowHide(self):
        return """
        <script>
        
        function showMePieChart(box)
        {
          var e = document.getElementById("selectMismatcheslist");
            
            
            if(document.getElementById("selectMismatcheslist").checked == true)
            {
              var selVal=1;
            }
            else
            {
            var selVal=0;
            }
            
            //var selVal = e.options[e.selectedIndex].value;
            
             var chboxs = document.getElementsByName("fileListPieChart");
             
            var tr=false;
            for(var i=0;i<chboxs.length;i++) { 
                if(chboxs[i].checked){
                
                 newBox='';
                 newBox = newBox.concat('containerPieChart_', chboxs[i].value);
                 if (document.getElementById(newBox) != null)
                 {
                     document.getElementById(newBox).style.display = "block";
                 }
                   tr=true; 
                }
                else
                {
                newBox='';
                 newBox = newBox.concat('containerPieChart_', chboxs[i].value);
                 if (document.getElementById(newBox) != null)
                 {
                     document.getElementById(newBox).style.display = "none";
                 }
                }
                }
                
                if (tr == true)
                {
                document.getElementById("legendTable").style.display = "block";
                }
                else
                {
                document.getElementById("legendTable").style.display = "none";
                }
          
                newBox='';
                
                if(selVal == 0)
                {
                    document.getElementById('container_0').style.display = "block";
                    document.getElementById('container_1').style.display = "none";
                }
                else
                {
                    document.getElementById('container_1').style.display = "block";
                    document.getElementById('container_0').style.display = "none";
                }
                
                

                

            }
        
        
        function showMe (box) {

            var e = document.getElementById("selectMismatcheslist");
            
            
            if(document.getElementById("selectMismatcheslist").checked == true)
            {
              var selVal=1;
            }
            else
            {
            var selVal=0;
            }
            
            //var selVal = e.options[e.selectedIndex].value;
            
             var chboxs = document.getElementsByName("fileList");
                
               
          
                newBox='';
                
                if(selVal == 0)
                {
                    document.getElementById('container_0').style.display = "block";
                    document.getElementById('container_1').style.display = "none";
                }
                else
                {
                    document.getElementById('container_1').style.display = "block";
                    document.getElementById('container_0').style.display = "none";
                }
                
                

                list = document.getElementsByClassName('stat');
                for (var i = 0; i < list.length; i++) {
                 list[i].style.display ='block';
                }

                }
      
        
        function showReads()
        {
            if(document.getElementById("showReads").checked == false)
            {
                
                document.getElementById('tabReads_0').style.display = "none";
                document.getElementById('tabReads_1').style.display = "none";
            }
            else
            {
                var e = document.getElementById("selectMismatcheslist");
                
                if(document.getElementById("selectMismatcheslist").checked == true)
                {
                  var selVal=1;
                }
                else
                {
                var selVal=0;
                }
                
                
                //var selVal = e.options[e.selectedIndex].value;
                
                
                if(selVal == 0)
                {
                    document.getElementById('tabReads_0').style.display = "block";
                    document.getElementById('tabReads_1').style.display = "none";
                }
                else
                {
                    document.getElementById('tabReads_0').style.display = "none";
                    document.getElementById('tabReads_1').style.display = "block";
                }
                
                
            }
        
        
        }
        
        function showMeOptionList (box) {

            var e = document.getElementById("selectMismatcheslist");
            var selVal = e.options[e.selectedIndex].value;
            
             var chboxs = document.getElementsByName("fileList");
                
                
                for(var i=0;i<chboxs.length;i++) { 
                chboxs[i].checked = true;
                }
            
            
          
                newBox='';
                
                if(selVal == 0)
                {
                    document.getElementById('container_0').style.display = "block";
                    document.getElementById('container_1').style.display = "none";
                }
                else
                {
                    document.getElementById('container_1').style.display = "block";
                    document.getElementById('container_0').style.display = "none";
                }
                
                
                if(document.getElementById("showReads").checked == false)
            {
                
                document.getElementById('tabReads_0').style.display = "none";
                document.getElementById('tabReads_1').style.display = "none";
            }
            else
            {
                var e = document.getElementById("selectMismatcheslist");
                var selVal = e.options[e.selectedIndex].value;
                
                
                if(selVal == 0)
                {
                    document.getElementById('tabReads_0').style.display = "block";
                    document.getElementById('tabReads_1').style.display = "none";
                }
                else
                {
                    document.getElementById('tabReads_0').style.display = "none";
                    document.getElementById('tabReads_1').style.display = "block";
                }
                
                
            }
        
                

                list = document.getElementsByClassName('stat');
                for (var i = 0; i < list.length; i++) {
                 list[i].style.display ='block';
                }

                }
                
        function showMeOptionListChb (box) {

            var e = document.getElementById("selectMismatcheslist");
            
            if(document.getElementById("selectMismatcheslist").checked == true)
            {
              var selVal=1;
            }
            else
            {
            var selVal=0;
            }
            
            
            //var selVal = e.options[e.selectedIndex].value;
            
             var chboxs = document.getElementsByName("fileList");
                
                
                for(var i=0;i<chboxs.length;i++) { 
                chboxs[i].checked = true;
                }
            
            
          
                newBox='';
                
                if(document.getElementById("selectMismatcheslist").checked == false)
                {
                
                    document.getElementById('container_0').style.display = "block";
                    document.getElementById('container_1').style.display = "none";
                }
                else
                {
                    document.getElementById('container_1').style.display = "block";
                    document.getElementById('container_0').style.display = "none";
                }
                
                
                if(document.getElementById("showReads").checked == false)
            {
                
                document.getElementById('tabReads_0').style.display = "none";
                document.getElementById('tabReads_1').style.display = "none";
            }
            else
            {
                //var e = document.getElementById("selectMismatcheslist");
                //var selVal = e.options[e.selectedIndex].value;
                
                
                if(selVal == 0)
                {
                    document.getElementById('tabReads_0').style.display = "block";
                    document.getElementById('tabReads_1').style.display = "none";
                }
                else
                {
                    document.getElementById('tabReads_0').style.display = "none";
                    document.getElementById('tabReads_1').style.display = "block";
                }
                
                
            }
        
                

                list = document.getElementsByClassName('stat');
                for (var i = 0; i < list.length; i++) {
                 list[i].style.display ='block';
                }

                }        
        
        function showMeOptionListStat (box) {

            
            if(document.getElementById("selectStatisticList").checked == true)
            {
              var selStat=1;
              document.getElementById("legendTable").style.display = "block";
              document.getElementById("containerPieChart").style.display = "block";
            }
            else
            {
            var selStat=0;
            document.getElementById("legendTable").style.display = "none";
            document.getElementById("containerPieChart").style.display = "none";
            }
            console.log(selStat);


            


                }        
                
                
            </script>
        """
    
    def addShowHidePie(self):
        return """
        <script>
        
        function showMePieChart(box)
        {
            
             var chboxs = document.getElementsByName("fileListPieChart");
             
            var tr = false;
            for(var i=0;i<chboxs.length;i++) { 
                if(chboxs[i].checked)
                {
                    
                 newBox='';
                 newBox = newBox.concat('containerPieChart_', chboxs[i].value);
                 document.getElementById(newBox).style.display = "block";
                 tr=true;
                }
                else
                {
                newBox='';
                 newBox = newBox.concat('containerPieChart_', chboxs[i].value);
                 document.getElementById(newBox).style.display = "none";
                
                }
                }
            if (tr==true)
            {
            document.getElementById("legendTable").style.display = "block";
            }
            else
            {
            document.getElementById("legendTable").style.display = "none";
            }
                

            }
        
        
        function showMe (box) {

            
             var chboxs = document.getElementsByName("fileList");
                
               
          
                newBox='';
                
                
                
                

                list = document.getElementsByClassName('stat');
                for (var i = 0; i < list.length; i++) {
                 list[i].style.display ='block';
                }

                }
      
        
        function showMeOptionList (box) {

             var chboxs = document.getElementsByName("fileList");
                
                for(var i=0;i<chboxs.length;i++) { 
                chboxs[i].checked = true;
                }
                newBox='';
                
                list = document.getElementsByClassName('stat');
                for (var i = 0; i < list.length; i++) {
                 list[i].style.display ='block';
                }

                }
            </script>
        """
    def addShowHideHistogram(self):
        return """
        <script>
        
        function showMeHistogram(box)
        {
            
             var chboxs = document.getElementsByName("fileListHistogram");
             
       
            for(var i=0;i<chboxs.length;i++) { 
                if(chboxs[i].checked){
                    
                 newBox='';
                 newBox = newBox.concat('containerHistogram_', chboxs[i].value);
                 console.log(document.getElementById(newBox));
                 document.getElementById(newBox).style.display = "block";
             
                }
                else
                {
                newBox='';
                 newBox = newBox.concat('containerHistogram_', chboxs[i].value);
                 document.getElementById(newBox).style.display = "none";
                
                }
                }
            

            }
        
        
            </script>
        """
    
    def _depth(self,l):
        if isinstance(l, list):
            return 1 + max(self._depth(item) for item in l)
        else:
            return 0
    
    def _buildContainer(self, containerName, addOptions, extraArg):
        className=''
        if extraArg != False:
            className = 'plot'
        else:
            className = 'stat'
            
        if addOptions == None:
            addOptions='width: 96%; margin: 0 auto;display:none'
        #return '''<div id="container''' + str(self.__class__.count) + '''" style="height: ''' + str(height) +'''px; width: 100%; margin: 0 auto"></div>'''
        containerN = "container_" + str(containerName)
        
        return '''<div class="''' + str(className)  + '''" id="container_''' + str(containerName) + '''" style= "''' + str(addOptions) + '''"></div>''', containerN
    def _parseData(self, dataY, type, seriesType, seriesName, multiYAxis, linkedSeries, stackingListNames, addLegendFake, colorPackage, sumEl, addLegendFakeColor):
        
         
        dataYdepth = self._depth(dataY)      
        
        #default: there are the same type of charts on one char
        if seriesType == None:
            if dataYdepth == 1:
                seriesType = [type]
            else:
                seriesType = [type for dY in dataY]
        
        legendSizeExtra=0
        legendSize=''
        if seriesName == None:
            seriesName=''
        else:
            legendSize =  len(max(seriesName, key = len))
            legendSizeExtra = len(seriesName)
            legendSizeExtra = legendSizeExtra / ( int(1000 / (legendSize*6)) )*12
            
        colors = ['#7cb5ec',   
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
                      ]
        
        
        
    
        data=''        
        if isinstance(dataY[0], list) == True:
            
            if multiYAxis == True:
                i=0
                for d in dataY:
                    if i==0:
                        data = '{0}{1}{2}{3}{4}{5}{6}'.format(""" type: '""" + seriesType[0] + """', """, """yAxis: """ + str(i) + """ ,""" ,  """  name: """, "'" if seriesName=='' else "'" + seriesName[i] + "'" ,""", data: """, json.dumps(d), """ } """ )
                    else:
                        data = data + '{0}{1}{2}{3}{4}{5}{6}'.format(""" , { type: '"""  + seriesType[i] + """', """ , """yAxis: """ + str(i) + """ ,""", """name: """ , "'" if seriesName=='' else "'" + seriesName[i] + "'" , """, data: """, json.dumps(d), """ } """ )
                    i+=1
            else:
                j=0
                i=0
                for d in dataY:
                    if i==0:
                        if seriesName=='':
                            sN = "name: '', "
                        else:  
                            sN ='name: "' + seriesName[i] + '", '  
                        
                          
                        if colorPackage!=None:
                            cP ='color: "' + colorPackage[i] + '", '  
                        else:
                            cP=''
                        
                        
                        if stackingListNames=='' or stackingListNames==None:
                            sLN=''
                        else:
                            sLN ='stack: "' + stackingListNames[i] + '", ' 
                            
                        if sumEl == True:
                            if sum(d) > 0:
                                data = '{0}{1}{2}{3}{4}'.format(""" type: '""" + seriesType[0] + """', """ , sN+sLN + cP ,""" data: """, json.dumps(d), """ } """ )
                        else:
                            data = '{0}{1}{2}{3}{4}'.format(""" type: '""" + seriesType[0] + """', """ , sN+sLN + cP ,""" data: """, json.dumps(d), """ } """ )
                    else:
                        if seriesName=='':
                            sN = "name: '', "
                        else:  
                            sN ='name: "' + seriesName[i] + '", ' 
                            
                        if stackingListNames=='' or stackingListNames==None:
                            sLN=''
                        else:
                            sLN ='stack: "' + stackingListNames[i] + '", ' 
                            
                        if colorPackage!=None:
                            cP ='color: "' + colorPackage[i] + '", '  
                        else:
                            cP=''
                            
                        if linkedSeries != None and (i+1)%linkedSeries == 0:
                            Lt = "linkedTo:" + "':previous', " #color: '" + str(colors[j]) + "', "
                            j+=1
                        else:
                            Lt=''
                        if sumEl == True:
                            if sum(d) > 0:
                                if data!='':
                                    data += ' , {'
                                data = data + '{0}{1}{2}{3}{4}'.format("""  type: '"""  + seriesType[i] + """', """ , sN+ Lt+sLN +cP  , """ data: """, json.dumps(d), """ } """ )
                        else:
                            if data!='':
                                data += ' , {'
                            data = data + '{0}{1}{2}{3}{4}'.format("""  type: '"""  + seriesType[i] + """', """ , sN+ Lt+sLN +cP  , """ data: """, json.dumps(d), """ } """ )
                    i+=1
        else:
            if seriesName=='':
                sN = "name: '', "
            else:  
                sN ="name: '" + seriesName[0] + "'," 
            
            if sumEl == True:
                if sum(dataY) >0:
                    data = '{0}{1}{2}{3}{4}'.format(""" type: '""" + seriesType[0] + """',  """  , sN , """ data: """, json.dumps(dataY), """ } """ )
#             else:
#                 data = '{0}{1}{2}{3}{4}'.format(""" type: '""" + seriesType[0] + """',  """  , sN , """ data: """, json.dumps(dataY), """ } """ )
        
        if addLegendFakeColor != None:
            addLegendFakeColor=addLegendFakeColor
        else:
            addLegendFakeColor='#ffffff'
        
        if addLegendFake!=None:
            if data!='':
                data+= ', { '
            data += """  name:'Area of expression', data: [0], color: '""" + str(addLegendFakeColor) + """"'}"""
       
        
        
            
        return data, legendSize, legendSizeExtra
    
    def _parseData2(self, dataY, type, seriesType, seriesName):   
        
        dataYdepth = self._depth(dataY)        
        #default: there are the same type of charts on one char
        if seriesType == None:
            if dataYdepth == 1:
                seriesType = [type]
            else:
                seriesType = [type for dY in dataY]
        
        legendSizeExtra=0
        legendSize=''
        if seriesName == None:
            seriesName=''
        else:
            legendSize =  len(max(seriesName, key = len))
            legendSizeExtra = len(seriesName)
            legendSizeExtra = legendSizeExtra / ( int(1000 / (legendSize*6)) )*12
            
        
        data='data: ['        
        if isinstance(dataY[0], list) == False:
            for eldY in range(0, len(dataY)):
                
                sN=''
                if seriesName=='':
                    sN="''"
                else:
                    sN = '"' + seriesName[eldY] + '"'
                
                data += "{ name: " + str(sN) + ", y:" + str(json.dumps(dataY[eldY])) +  "}"
                
                if len(dataY)-1 != eldY:
                    data += ", "
                else:
                    data +="] }"
        
        return data, legendSize, legendSizeExtra
    
    def _parseData3(self, dataY, type, seriesType, seriesName, idSL, name):   
        
        dataYdepth = self._depth(dataY)        
        #default: there are the same type of charts on one char
        if seriesType == None:
            if dataYdepth == 1:
                seriesType = [type]
            else:
                seriesType = [type for dY in dataY]
        
        legendSizeExtra=0
        legendSize=''
        if seriesName == None:
            seriesName=''
#         else:
#             legendSize =  len(max(seriesName, key = len))
#             legendSizeExtra = len(seriesName)
#             legendSizeExtra = legendSizeExtra / ( int(1000 / (legendSize*6)) )*12
            
            
#         if idSL == 0:
#             sL = 'showInLegend:true,'
#         else:
#             sL = 'showInLegend:false,'
        sL = 'showInLegend:false,'
        centerStart = 40 * idSL + 30
        
        data="{ type:'pie', "  + """
         title: {
            align: 'center',
            format: '<p style="text-transform: uppercase;text-weight:bold;">{name}</p>',
            verticalAlign: 'top',
            y: -40
        },
        
        """ + " name:'" + str(name) + "' , center: ['" + str(centerStart) + "%'" + ", '50%'], " + str(sL)  + "  data: ["      
        if isinstance(dataY[0], list) == False:
            for eldY in range(0, len(dataY)):
                
                sN=''
                if seriesName=='':
                    sN="''"
                else:
                    sN = '"' + seriesName[eldY] + '"'
                
                data += "[" + str(sN) + ", " + str(json.dumps(dataY[eldY])) +  "]"
                
                if len(dataY)-1 != eldY:
                    data += ", "
                else:
                    data +="] },\n "
        
        return data, legendSize, legendSizeExtra
    
    def _parseData4(self, dataY, type, seriesType, seriesName):   
        
        dataYdepth = self._depth(dataY)        
        #default: there are the same type of charts on one char
        if seriesType == None:
            if dataYdepth == 1:
                seriesType = [type]
            else:
                seriesType = [type for dY in dataY]
        
        legendSizeExtra=0
        legendSize=''
        if seriesName == None:
            seriesName=''
            
        
        data ="borderWidth: 1, borderColor:'#060606', data: ["      
        
        j=0
        for el in range(0, len(dataY)):
            i=0
            for eldY in range(len(dataY[el])-1, -1, -1):
                
                data += "[" + str(j)  + ', ' + str(i) + ', ' + str(dataY[el][eldY]) +  "]"
                
                if 0 != eldY:
                    data += ", "
                i+=1
            
            if len(dataY) - 1 == el:
                data +="] }\n "
            else:
                data += ", "
            j+=1
        
        return data, legendSize, legendSizeExtra
    
    def _useAttribute1(self, att, attName):
        if att == None:
            att= attName + ": '',"
        else:
            if type(att)==int or type(att)==float:
                att = attName + ": " + str(att) + ", "
            else:
                att = attName + ": '" + str(att) + "', "
            
        return att
    
    
    def _useAttribute2(self, att, attName):
        if att==None:
            att= ""
        elif att==False:
            att= attName + ": " + str('null') + ", "
        else:
            if type(att)==int or type(att)==float:
                att= attName + ": " + str(att) + ", "    
            else:
                att= attName + ": '" + str(att) + "', "
        return att
    
    #attOptions=[True, False]
    def _useAttribute3(self, att, attName, attOption):
        if att == True:
            att = attName + ": '" + attOption + "', "
        else:
            att= ''
        return att
    
    def _useAttribute4(self, att, attName):
        if att == None:
            att= ''
        else:
            if type(att)==int or type(att)==float:
                att = attName + ": " + str(att) + ", "
            else:
                att = attName + ": '" + str(att) + "', "
            
        return att
    
    def _useAttribute5(self, att, attName):
        
        if att == None:
            att =''
        else:
            if type(att)==int or type(att)==float:
                att = attName + ": " + str(att) + ", "
            else:
                att = attName + ": '" + str(att) + "', "
        return att
    
        
    def _useAttribute6(self, att, attName):
        if att == None:
            att= attName + ": '',"
        else:
            att = attName + ": " + str(att) + ", "
            
            
        return att
    
    def _useColors(self, useColors):
        if useColors == True:
            return """
             colors: ['#7cb5ec', '#ff3232',
                      '#434348', '#ff3232',
                      '#99D6D6', '#ff3232',
                      '#90ed7d', '#ff3232',
                      '#f7a35c', '#ff3232',
                      '#005C5C', '#ff3232',
                      '#292933', '#ff3232',
                      '#336699', '#ff3232',
                      '#8085e9', '#ff3232',
                      '#B2CCFF', '#ff3232',
                      '#f15c80', '#ff3232',
                      '#e4d354', '#ff3232',
                      '#8085e8', '#ff3232',
                      '#8d4653', '#ff3232',
                      '#6699FF', '#ff3232',
                      '#91e8e1', '#ff3232',
                      '#7A991F', '#ff3232',
                      '#525266', '#ff3232',
                      '#1A334C', '#ff3232',
                      '#334C80', '#ff3232',
                      '#292900', '#ff3232',
                      '#142900', '#ff3232',
                      '#99993D', '#ff3232',
                      '#009999', '#ff3232',
                      '#1A1A0A', '#ff3232',
                      '#5C85AD', '#ff3232',
                      '#804C4C', '#ff3232',
                      '#1A0F0F', '#ff3232',
                      '#A3A3CC', '#ff3232',
                      '#660033', '#ff3232',
                      '#3D4C0F', '#ff3232',
                      '#fde720', '#ff3232',
                      '#554e44', '#ff3232',
                      '#1ce1ce', '#ff3232',
                      '#dedbbb', '#ff3232',
                      '#facade', '#ff3232',
                      '#baff1e', '#ff3232',
                      '#aba5ed', '#ff3232',
                      '#f2b3b3', '#ff3232',
                      '#f9e0e0', '#ff3232',
                      '#abcdef', '#ff3232',
                      '#f9dcd3', '#ff3232',
                      '#eb9180', '#ff3232',
                      '#c2dde5', '#ff3232'
                      ],
             """
        elif useColors == 'onlyRed':
            return """
             colors: ['#ff3232',
                      '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232',
                       '#ff3232'
                      ],
             """
        else:
            return """
             colors: ['#7cb5ec',   
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
                      ],
             """
        
    def _useXAxis(self, xAxisTitle, tickInterval, tickMinValue, categories, typeAxisXScale, xAxisRotation, labelX, interaction, plotLines, dataOld, containerName, extraOptions, addLegendFakeColor):
        
        #print self.__class__.count
        #print interaction
        #print self._interactionNumberStart
        #print self._interactionNumberEnd
        
        
        xAxis = """
        xAxis: {  
                  title: { 
                  """ + self._useAttribute1(xAxisTitle, "text") + """
                  }, 
                  """ + self._useAttribute2(tickInterval, "tickInterval") + self._useAttribute4(tickMinValue, "min") + self._useAttribute6(categories, "categories") +  self._useAttribute1(typeAxisXScale, "type") + """
                  labels: {
                      """ + self._useAttribute1(xAxisRotation, "rotation") 
        
        if extraOptions!=None:
            xAxis += """
                          formatter: function () {
                            if (inArray(blue, this.value)) {
                                return '<span style="fill: blue;">' + categories[this.value] + '</span>';
                            }
                            else if (inArray(red, this.value)) {
                                return '<span style="fill: red;">' + categories[this.value] + '</span>';
                            }
                             else {
                                return '<span style="fill: black;">' +categories[this.value] + '</span>';
                            }
                        },
                      
                      """ 
        xAxis += labelX
        
        xAxis += "}, "
        
        if plotLines!=None:
            xAxis += "plotLines: ["
             
            if self._depth(dataOld) == 1:
                for numdY in range(0, len(dataOld)):
                    if dataOld[numdY] > 0:
                        xAxis += """
                      {
                          color: '""" + str(addLegendFakeColor) + """',
                          width: 2,
                          value: """ + str(numdY) + """,
                          id: 'plotline-""" + str(containerName) + """',
                          
                      },
                    """
            else:
                finalDataOld = [sum(sublist) for sublist in izip(*dataOld)]
                
                i=0
                start=-1
                for numdY in range(0, len(finalDataOld)):
                    if finalDataOld[numdY] > 0:
                        if i==0:
                            start = numdY - 0.25                  
                        i+=1
                    else:
                        if start!=-1:
                            end = numdY-0.75
                            i=0
                            xAxis += """
                              {
                                  color: '""" +  str(addLegendFakeColor) +  """',
                                  from: """ + str(start) + """,
                                  to: """ + str(end) + """,
                                  id: 'all',
                              },
                            """
                            start=-1
                        
            xAxis += "],"
             
     
              
                
        
        if interaction == True:
            xAxis += """
                      , events: {
                                afterSetExtremes: function() {
                                    if (!this.chart.options.chart.isZoomed) 
                                    {
                                        var xMin = this.chart.xAxis[0].min;
                                        var xMax = this.chart.xAxis[0].max;
                                        var zmRange = computeTickInterval(xMin, xMax);
                    """
            
            for el in range(self._interactionNumberStart, self._interactionNumberEnd+1):
                xAxis += """
                        chart"""+str(el)+""".xAxis[0].options.tickInterval =zmRange;
                        chart"""+str(el)+""".xAxis[0].isDirty = true;                                 
                """        
            for el in range(self._interactionNumberStart, self._interactionNumberEnd+1):
                if el != self.__class__.count:
                    xAxis += """
                    chart"""+str(el)+""".options.chart.isZoomed = true;
                       chart"""+str(el)+""".options.chart.isZoomed = true;
                       """
            for el in range(self._interactionNumberStart, self._interactionNumberEnd+1):
                if el != self.__class__.count:
                    xAxis += """
                    chart"""+str(el)+""".xAxis[0].setExtremes(xMin, xMax, true);
                    chart"""+str(el)+""".xAxis[0].setExtremes(xMin, xMax, true);
                       """
            for el in range(self._interactionNumberStart, self._interactionNumberEnd+1):
                if el != self.__class__.count:
                    xAxis += """
                    chart"""+str(el)+""".options.chart.isZoomed = false;
                       chart"""+str(el)+""".options.chart.isZoomed = false;
                       """
                      
            xAxis += """
                            }
                        }
                }
        """
        xAxis += "},"
        
       
        
        return xAxis
    
    
    def _useYAxis(self, yAxisTitle, axisYType, categoriesY, visibleY):
        
        if axisYType == None:
            axisYType = ''
        else:
            axisYType = ' type: "' + str(axisYType) + '", '
            
            
        if visibleY==None:
            visibleY=''
        elif visibleY == False:
            visibleY= ' visible: false, '
            
        
        return """
        yAxis: { """ + self._useAttribute6(categoriesY, "categories")   + """
                    
                   title: { 
                  """ + self._useAttribute1(yAxisTitle, "text") + """
                  },
                  """ + axisYType + visibleY + """
            },
        """
        
    def _useMultiYAxis(self, yAxisTitle):
        
        yAxis = "yAxis: ["
        
        
        for elNum in range(0, len(yAxisTitle)):
            if elNum < len(yAxisTitle)/2:
                yAxis += """
                     {
                           title: { 
                          """ + self._useAttribute1(yAxisTitle[elNum], "text") + """
                          },
                    },
                """    
            else:
                yAxis += """
                     {
                           title: { 
                          """ + self._useAttribute1(yAxisTitle[elNum], "text") + """
                          },
                          opposite: true
                    },
                """
        
        yAxis += "],"
        
        return yAxis
        
        
    def _useTitle(self, titleText):
        return """
        title: { 
                  """ + self._useAttribute1(titleText, "text") + """  
                  },
        """
    def _useSubTitle(self, subtitleText):
        return """    
            subtitle: {
                  """ + self._useAttribute1(subtitleText, "text") + """
            },
        """
    def _useChart(self, height, polar, marginTop, zoomType, countNum, containerName, type):
        return """
        chart: {
        
                type: '""" + str(type) + """',
                height: """ + str(height) + """,
                renderTo: 'container_""" + str(containerName) + """',
                isZoomed:false,
                """ + self._useAttribute5(zoomType, 'zoomType') + self._useAttribute3(polar, 'polar', 'true') +  self._useAttribute5(marginTop, 'marginTop') + """
            },
        """
    
    def _usePlotOptions(self, type, stacking, lineWidth, dataLabels, extraArg, size, changePlot, colorAxis, getColor, addPlotOptExtra):
        
        if type!='heatmap':
            if size == None:
                size=''
            else:
                size  = "size: " + str(size) + " ,"
                
                
            if changePlot==None:
                changePlot=''
            else:
                changePlot = """
                events: {
                            legendItemClick: function (e) { """ + changePlot + """
                                
                                
                                    
                                }
                            },
                """
            
            if addPlotOptExtra!=None:
                addPlotOptExtra=addPlotOptExtra
            else:
                addPlotOptExtra=''
            
            if extraArg == False:
                return """
                plotOptions: {
                    """ + type + """: {
                        allowPointSelect: true,
                        cursor: 'pointer',
                        """ + str(size) + """
                        dataLabels: {
                            enabled: false
                        },
                        
                    }
                },
                """
            else:
                return """
            plotOptions: {
                    """ + type + """: { """ + str(size) + """
                        """ + self._useAttribute3(stacking, "stacking", 'normal') + self._useAttribute5(lineWidth, 'lineWidth') + dataLabels + changePlot + """ 
                    },
                   """ + addPlotOptExtra + """
                },
            """
        else:
            if colorAxis!=None:
                colorAxis= 'max:' + str(colorAxis) + ','
            else:
                colorAxis=''
                
            return """
        colorAxis: {
            min: 0,
            """ + str(colorAxis)  + """
            minColor: '#FFFFFF',
            maxColor: Highcharts.getOptions().colors[""" + str(getColor)  + """]
        },
        """
         
        
    def _useToolTip(self, label, shared, extraArg, extraScript, type):
        
        if extraScript == None:
            extraScript=''
        
        
        if extraArg == True:
            return """
        tooltip: {
                formatter: function() {
                
                    
                var s = ''
                $.each(this.points, function () {
                    mm='';
                    if (parseInt(folderFileList.indexOf(this.series.name)) >= 0)
                    {
                        if (mismatch[parseInt(folderFileList.indexOf(this.series.name))] !== undefined)
                        {
                            if (mismatch[parseInt(folderFileList.indexOf(this.series.name))][this.x] != '')
                            {
                                mm = ' , mismatch: ' + mismatch[parseInt(folderFileList.indexOf(this.series.name))][this.x];
                            
                            }
                        }
                    }
                    
                    s += '<b>' + this.series.name + ': </b>' + this.y  + mm + '<br \>'  ;
                });

                return s;
            
                 },
                 shared:true ,
            },
        """
        elif extraArg == False:
            return """
            tooltip: {
            formatter: function () {
            
            """ + str(extraScript) + """
            
                val = ''
                
                if(resMisLetter!= "" && resMisLetter[this.point.name] !== undefined && resMisLetter[this.point.name].length != 0)
                {
                    
                    val += '<span style="color:#198b19">' + 'inside: ' + '</span>' ;
                    val += resMisLetter[this.point.name] + ', ' + '<br \>';
                }
                if(resMisLetterNot!= "" && resMisLetterNot[this.point.name] !== undefined && resMisLetterNot[this.point.name].length != 0)
                {
                    
                    val += '<span style="color:#198b19">' + 'outside: ' + '</span>'; 
                    val += resMisLetterNot[this.point.name];
                }
               
            
                return  '<b>' + this.point.name + '</b>: ' + Highcharts.numberFormat(this.y, 0,',',',') + '<br \>' + val ;
            }
            },
            """
        elif extraArg == 'onlyRed':
            return ''
        else:
            
            if type == "heatmap":
                return """
            
                    tooltip: {
                    formatter: function () {
                        return '<b>' + this.series.yAxis.categories[this.point.y]  + '</b>: '  + this.point.value;
                    }
                },
                
            """
            else:
            
            
                return """
                tooltip: {
                        headerFormat: '',
                        pointFormat: '""" + label + """', 
                        footerFormat: '',
                        shared: """ + shared + """,
                        crosshairs: true,
                        useHTML: true,
                        crosshairs: true
                    },
                """
            
                
        
    
    def _draw(self, dataY, legendSize, legendSizeExtra, type, height, addOptions, tickInterval, tickMinValue, label, lineWidth, titleText, subtitleText, xAxisTitle, yAxisTitle, categories, 
               legend, xAxisRotation, dataLabels, polar, stacking, shared, overMouseAxisX, overMouseLabelX, showChartClickOnLink, typeAxisXScale, pointStartLog, zoomType, marginTop, 
               interaction, multiYAxis, plotLines, dataOld, containerName, extraArg, useColors, extraOptions, itemMarginBottom, script, extraScript, extraSc, extraSc2, 
               size, axisYType, changePlot, colorAxis, categoriesY, getColor, credits, visibleY, addPlotOptExtra, addLegendFakeColor):
        
        container=''
        
        
            
        container, containerN = self._buildContainer(containerName, addOptions, extraArg)
        
        
        #if self.__class__.count==1:
            #container += self._addLib() + self._addStyle()

        
        jsCodeShowChartClickOnLink=''
        
                
        if overMouseAxisX==True:
            labelX = """
                ,
                useHTML: true,
                formatter: function () {
                    return '<div class="hastip" title="' + this.value + ' ">' """ + overMouseLabelX + """ '</div>';
                }
        """
            yAxisMO = """ $('.hastip').tooltipsy(); """
        else:
            labelX=''
            yAxisMO=''
    
        #default legend center
        if legend == None:
            legend = 'center'
        
        if legendSize != '':
            legendSize = legendSize*6+36 
            legendSizeExtra = legendSizeExtra+100
            legendSize = """, maxHeight: """ + str(legendSizeExtra) + """, itemWidth: """ + str(legendSize)
        
        if legend == 'img':
            legend = """ legend: { enabled:false, } , """
        else:
            legend = """ legend: { align: '""" + str(legend) + """', itemMarginBottom:""" +  str(itemMarginBottom) + str(legendSize) + """},"""
        
         
        if type=='heatmap':
            legend = """
            legend: {
            align: 'right',
            layout: 'vertical',
            margin: 0,
            verticalAlign: 'top',
            y: 25,
            symbolHeight: 280
        },
        """
        
        if height == None:
            height = int(self._height)
        
            
        height += legendSizeExtra    
            
        if dataLabels == True: 
            dataLabels =  """fillColor: { 
                            linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1},
                            stops: [
                                [0, Highcharts.getOptions().colors[0]],
                                [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                            ]
                        },"""
        else:
            dataLabels=""" 
             dataLabels: { enabled: true },
             enableMouseTracking: false, 
             """
        
        if shared==True:
            shared='true' 
        else:
            shared='false'         
            
        inter=''
        if interaction == True:
            inter = """, function(chart) { 
                    syncronizeCrossHairs(chart);
                    }"""
        
        thousandSep= """
        Highcharts.setOptions({
            lang: {
                thousandsSep: ','
            }
        });
        """
        
        functionJS1 = " <script> $(function () { "   + thousandSep + self._themePlot() + "chart"+ str(self.__class__.count)+" = new Highcharts.Chart({"
        functionJS1 += str(self._useChart(height, polar, marginTop, zoomType, self.__class__.count, containerName, type)) 
        functionJS1 += str(self._useTitle(titleText)) 
        functionJS1 += str(self._useSubTitle(subtitleText)) 
        if useColors != None:
            functionJS1 += str(self._useColors(useColors))
        
        if extraArg!=False:
            functionJS1 += str(self._useXAxis(xAxisTitle, tickInterval, tickMinValue, categories, typeAxisXScale, xAxisRotation, labelX, interaction, plotLines, dataOld, containerName, extraOptions, addLegendFakeColor))
        
        if extraArg!=False:
            if multiYAxis==True: 
                functionJS1 += str(self._useMultiYAxis(yAxisTitle))
            else:
                functionJS1 += str(self._useYAxis(yAxisTitle, axisYType, categoriesY, visibleY))
                
        if extraSc==None:
            extraSc=''
         
        if credits !=None:
            functionJS1+="""
                    credits: {
                    enabled: false
                },"""
             
        functionJS1 += str(self._usePlotOptions(type, stacking, lineWidth, dataLabels, extraArg, size, changePlot, colorAxis, getColor, addPlotOptExtra)) 
        functionJS1 += str(self._useToolTip(label, shared, extraArg, extraScript, type)) 
        functionJS1 += legend 
        functionJS1 += """
        exporting: {
            enabled: false
        },
        """
        functionJS1 += " series: [{ " + self._useAttribute4(pointStartLog, "pointStart") 
            
        if extraSc==None:
            extraSc=''
        if extraSc2==None:
            extraSc2=''
            
        functionJS2 = """ ] } """ + inter  + extraSc + """    );""" + extraSc2
        
        functionJS2 += script
        
        if type == 'column':
            functionJS2 += """ }); 
           
          
            $( function() {
             $('#save_btn').click(function() {
               console.log($('#""" +  containerN + """').highcharts());
             save_chart($('#""" +  containerN + """').highcharts());
                });
                
            setTimeout(function() {
                $('#save_btn').trigger('click');
            }, 0);
        });
            </script> """
        else:
            functionJS2 += """ }); </script> """
        
        self.__class__.count +=1  
        
        return '{0}{1}{2}{3}{4}'.format(jsCodeShowChartClickOnLink, container, functionJS1, dataY, functionJS2)

    
    def _interactionAmongCharts(self, numCountList):
        graph='<script> '
        for el in numCountList:
            graph += "var chart"+str(el)+";"
        
        graph += """
        var controllingChart;
        var defaultTickInterval = 5;
        var currentTickInterval = defaultTickInterval;
        
       
        function unzoom() {
        """
        
        for el in numCountList:
            graph += "chart"+str(el)+".options.chart.isZoomed = false;"
            graph += "chart"+str(el)+".xAxis[0].setExtremes(null, null);"
        graph += '}'
        
        graph += """
        //catch mousemove event and have all 3 charts' crosshairs move along indicated values on x axis

        function syncronizeCrossHairs(chart) {
            var container = $(chart.container),
                offset = container.offset(),
                x, y, isInside, report;

            container.mousemove(function(evt) {

                x = evt.clientX - chart.plotLeft - offset.left;
                y = evt.clientY - chart.plotTop - offset.top;
                if(!chart.isInsidePlot(x, y)) {
                     return false;   
                }
                var xAxis = chart.xAxis[0];
                //remove old plot line and draw new plot line (crosshair) for this chart
        """
        for el in numCountList:
            graph += """
                var xAxis"""+str(el)+""" = chart"""+str(el)+""".xAxis[0];
                xAxis"""+str(el)+""".removePlotLine("myPlotLineId");
                xAxis"""+str(el)+""".addPlotLine({
                    value: chart.xAxis[0].translate(x, true),
                    width: 1,
                    color: 'red',
                    //dashStyle: 'dash',                   
                    id: "myPlotLineId"
                });
            """
        graph += " }); }"
        
        graph+="""
        //compute a reasonable tick interval given the zoom range -
        //have to compute this since we set the tickIntervals in order
        //to get predictable synchronization between 3 charts with
        //different data.
        function computeTickInterval(xMin, xMax) {
            var zoomRange = xMax - xMin;
            
            if (zoomRange <= 2)
                currentTickInterval = 0.5;
            if (zoomRange < 20)
                currentTickInterval = 1;
            else if (zoomRange < 100)
                currentTickInterval = 5;
        }
            //explicitly set the tickInterval for the 3 charts - based on
            //selected range
            function setTickInterval(event) {
                var xMin = event.xAxis[0].min;
                var xMax = event.xAxis[0].max;
                computeTickInterval(xMin, xMax);
       """
       
        for el in numCountList:
            graph += """
            chart"""+str(el)+""".xAxis[0].options.tickInterval = currentTickInterval;
            chart"""+str(el)+""".xAxis[0].isDirty = true;
           """
        
            
        graph += """}
        //reset the extremes and the tickInterval to default values
        function unzoom1() {
        """
        for el in numCountList:
            graph += """
            chart"""+str(el)+""".xAxis[0].options.tickInterval = defaultTickInterval;
            chart"""+str(el)+""".xAxis[0].isDirty = true;
            chart"""+str(el)+""".xAxis[0].setExtremes(null, null);
            """
        graph += """  } 
        
        $('#btn""" + str(self._interactionNumberStart) +"""').click(function(){
                unzoom();
            });
            
            var myPlotLineId = "myPlotLine";
        """
        
        
        
        graph += ' </script> '
        
        return graph
    
    def drawPieChartWithSingleLegend(self, dataY, titleText=None, height=None, addOptions=None, label=None, 
                     seriesType=None, seriesName=None, showInLegend=True, containerName=None,
                     itemMarginBottom=0, extraScript=None, extraSc=None, extraSc2=None, size=None, useColors=None,
                     visibleY=None):
        
        d = ''
        for iDataY in range(0, len(dataY)):
            data, legendSize, legendSizeExtra = self._parseData3(dataY=dataY[iDataY], type = 'pie', seriesType=seriesType, seriesName=seriesName, idSL=iDataY, name=titleText[iDataY])
            d+=data
        d+= ' '
        
       
        
        type='pie'
        graph = self._draw(
                           d[1:], legendSize, legendSizeExtra, 
                           type=type, 
                           height=height, 
                           addOptions=addOptions,
                           tickInterval=None, 
                           tickMinValue=None,  
                           label=label, 
                           lineWidth=None, 
                           titleText=None, 
                           subtitleText=None, 
                           xAxisTitle=None, 
                           yAxisTitle=None,
                           categories=None, 
                           legend=None, 
                           xAxisRotation=None, 
                           dataLabels=None, 
                           polar=None, 
                           stacking=None, 
                           shared=True, 
                           overMouseAxisX=None, 
                           overMouseLabelX=None, 
                           showChartClickOnLink=None, 
                           typeAxisXScale=None, 
                           pointStartLog=None, 
                           zoomType=None, 
                           marginTop=None, 
                           interaction=None,
                           multiYAxis=False,
                           plotLines=None,
                           dataOld=dataY,
                           containerName=containerName,
                           extraArg=False,
                           useColors=useColors,
                           extraOptions=None,
                           itemMarginBottom=itemMarginBottom,
                           script='',
                           extraScript=extraScript,
                           extraSc=extraSc,
                           extraSc2=extraSc2,
                           size=size,
                           axisYType=None,
                           changePlot=None,
                           colorAxis=None,
                           categoriesY=None,
                           getColor=None,
                           credits=None,
                           visibleY=None,
                           addPlotOptExtra=None,
                           addLegendFakeColor=None
                           )
        return graph
    
    
    def drawPieChart(self, dataY, titleText=None, height=None, addOptions=None, label=None, 
                     seriesType=None, seriesName=None, showInLegend=True, containerName=None,
                     itemMarginBottom=0, extraScript=None, extraSc=None,extraSc2=None, size=None,
                     visibleY=None):
        
        data, legendSize, legendSizeExtra = self._parseData2(dataY=dataY, type = 'pie', seriesType=seriesType, seriesName=seriesName)
        
        type='pie'
        graph = self._draw(
                           data, legendSize, legendSizeExtra, 
                           type=type, 
                           height=height, 
                           addOptions=addOptions,
                           tickInterval=None, 
                           tickMinValue=None,  
                           label=label, 
                           lineWidth=None, 
                           titleText=titleText, 
                           subtitleText=None, 
                           xAxisTitle=None, 
                           yAxisTitle=None,
                           categories=None, 
                           legend=None, 
                           xAxisRotation=None, 
                           dataLabels=None, 
                           polar=None, 
                           stacking=None, 
                           shared=True, 
                           overMouseAxisX=None, 
                           overMouseLabelX=None, 
                           showChartClickOnLink=None, 
                           typeAxisXScale=None, 
                           pointStartLog=None, 
                           zoomType=None, 
                           marginTop=None, 
                           interaction=None,
                           multiYAxis=False,
                           plotLines=None,
                           dataOld=dataY,
                           containerName=containerName,
                           extraArg=False,
                           useColors=None,
                           extraOptions=None,
                           itemMarginBottom=itemMarginBottom,
                           script='',
                           extraScript=extraScript,
                           extraSc=extraSc, 
                           extraSc2=extraSc2,
                           size=size,
                           axisYType=None,
                           changePlot=None,
                           colorAxis=None,
                           categoriesY=None,
                           getColor=None,
                           credits=None,
                           visibleY=None,
                           addPlotOptExtra=None,
                           addLegendFakeColor=None
                           )
        return graph
    
    
    def drawHeatmap(self,
                    dataY, 
                      height=None, 
                      addOptions=None,
                      tickInterval=None,
                      label=None, 
                      lineWidth=1, 
                      titleText=None, 
                      subtitleText=None, 
                      xAxisTitle=None, 
                      yAxisTitle=None,
                      categories=None, 
                      seriesType=None, 
                      seriesName=None, 
                      legend=None, 
                      xAxisRotation=0, 
                      dataLabels=True, 
                      shared=True, 
                      stacking=False,
                      overMouseAxisX=False, 
                      overMouseLabelX=' + this.value + ', 
                      showChartClickOnLink=False, 
                      typeAxisXScale=None, 
                      pointStartLog=None,
                      zoomType='x',
                      marginTop=60,
                      interaction=False,
                      containerName=None,
                      plotLines=None,
                      extraArg=None,
                      useColors=None,
                      linkedSeries=None,
                      tickMinValue=None,
                      itemMarginBottom=0,
                      script='',
                      extraSc=None,
                      size=None,
                      extraOptions=None,
                      axisYType=None,
                      stackingListNames=None,
                      changePlot=None,
                      extraSc2=None,
                      addLegendFake=None,
                      colorPackage=None,
                      colorAxis=None,
                      categoriesY=None,
                      getColor=None,
                      visibleY=None
                    ):
        
        type='heatmap'
        
        data, legendSize, legendSizeExtra = self._parseData4(dataY=dataY, type = type, seriesType=seriesType, seriesName=seriesName)
        
        
        graph = self._draw(
                           dataY=data, legendSize=legendSize, legendSizeExtra=legendSizeExtra, 
                           type=type, 
                           height=height, 
                           addOptions=addOptions,
                           tickInterval=tickInterval, 
                           tickMinValue=tickMinValue,  
                           label=label, 
                           lineWidth=lineWidth, 
                           titleText=titleText, 
                           subtitleText=subtitleText, 
                           xAxisTitle=xAxisTitle, 
                           yAxisTitle=yAxisTitle,
                           categories=categories, 
                           legend=legend, 
                           xAxisRotation=xAxisRotation, 
                           dataLabels=dataLabels, 
                           polar=None, 
                           stacking=stacking, 
                           shared=shared, 
                           overMouseAxisX=overMouseAxisX, 
                           overMouseLabelX=overMouseLabelX, 
                           showChartClickOnLink=showChartClickOnLink, 
                           typeAxisXScale=typeAxisXScale, 
                           pointStartLog=pointStartLog, 
                           zoomType=zoomType, 
                           marginTop=marginTop, 
                           interaction=interaction,
                           multiYAxis=False,
                           plotLines=plotLines,
                           dataOld=dataY,
                           containerName=containerName,
                           extraArg=extraArg,
                           useColors=useColors,
                           extraOptions=extraOptions,
                           itemMarginBottom=itemMarginBottom,
                           script=script,
                           extraScript=None,
                           extraSc=extraSc,
                           size=size,
                           extraSc2=extraSc2,
                           axisYType=axisYType,
                           changePlot=changePlot,
                           colorAxis=colorAxis,
                           categoriesY=categoriesY,
                           getColor=getColor,
                           credits=None,
                           visibleY=None,
                           addPlotOptExtra=None,
                           addLegendFakeColor=None
                           )
        return graph
    
    
    
    def drawColumnChart(self, 
                      dataY, 
                      height=None, 
                      addOptions=None,
                      tickInterval=None,
                      label='<b>{series.name}: </b>{point.y} <br \>', 
                      lineWidth=1, 
                      titleText=None, 
                      subtitleText=None, 
                      xAxisTitle=None, 
                      yAxisTitle=None,
                      categories=None, 
                      seriesType=None, 
                      seriesName=None, 
                      legend=None, 
                      xAxisRotation=0, 
                      dataLabels=True, 
                      shared=True, 
                      stacking=False,
                      overMouseAxisX=False, 
                      overMouseLabelX=' + this.value + ', 
                      showChartClickOnLink=False, 
                      typeAxisXScale=None, 
                      pointStartLog=None,
                      zoomType='x',
                      marginTop=60,
                      interaction=False,
                      containerName=None,
                      plotLines=None,
                      extraArg=None,
                      useColors=False,
                      linkedSeries=None,
                      tickMinValue=None,
                      itemMarginBottom=0,
                      script='',
                      extraSc=None,
                      size=None,
                      extraOptions=None,
                      axisYType=None,
                      stackingListNames=None,
                      changePlot=None,
                      extraSc2=None,
                      addLegendFake=None,
                      colorPackage=None,
                      categoriesY=None,
                      sumEl=True,
                      credits=None,
                      visibleY=None,
                      addPlotOptExtra=None,
                      addLegendFakeColor=None
                     ):
        
        type='column'
        
        
        
        data, legendSize, legendSizeExtra = self._parseData(dataY=dataY, type = type, seriesType=seriesType, seriesName=seriesName, multiYAxis=False, linkedSeries=linkedSeries, stackingListNames=stackingListNames, addLegendFake=addLegendFake, colorPackage=colorPackage, sumEl=sumEl, addLegendFakeColor=addLegendFakeColor)
        
        if legend == 'img':
            legendSize=0
            legendSizeExtra=0
             
        graph = self._draw(
                           dataY=data, legendSize=legendSize, legendSizeExtra=legendSizeExtra, 
                           type=type, 
                           height=height, 
                           addOptions=addOptions,
                           tickInterval=tickInterval, 
                           tickMinValue=tickMinValue,  
                           label=label, 
                           lineWidth=lineWidth, 
                           titleText=titleText, 
                           subtitleText=subtitleText, 
                           xAxisTitle=xAxisTitle, 
                           yAxisTitle=yAxisTitle,
                           categories=categories, 
                           legend=legend, 
                           xAxisRotation=xAxisRotation, 
                           dataLabels=dataLabels, 
                           polar=None, 
                           stacking=stacking, 
                           shared=shared, 
                           overMouseAxisX=overMouseAxisX, 
                           overMouseLabelX=overMouseLabelX, 
                           showChartClickOnLink=showChartClickOnLink, 
                           typeAxisXScale=typeAxisXScale, 
                           pointStartLog=pointStartLog, 
                           zoomType=zoomType, 
                           marginTop=marginTop, 
                           interaction=interaction,
                           multiYAxis=False,
                           plotLines=plotLines,
                           dataOld=dataY,
                           containerName=containerName,
                           extraArg=extraArg,
                           useColors=useColors,
                           extraOptions=extraOptions,
                           itemMarginBottom=itemMarginBottom,
                           script=script,
                           extraScript=None,
                           extraSc=extraSc,
                           size=size,
                           extraSc2=extraSc2,
                           axisYType=axisYType,
                           changePlot=changePlot,
                           colorAxis=None,
                           categoriesY=categoriesY,
                           getColor=None,
                           credits=credits,
                           visibleY=visibleY,
                           addPlotOptExtra=addPlotOptExtra,
                           addLegendFakeColor=addLegendFakeColor
                           )
        return graph