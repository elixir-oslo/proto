# Author: Diana Domanska

import json

#import quick.webtools.restricted.visualization.visualizationPlots as vp
#vp.addJSlibs() #JS libraries
#vp.useThemePlot() #Theme
#vp.addJSlibsExport() #Export picture as png, svg,...
#vp.addJSlibsHeatmap() #JS libraries to heatmap plot
#
#drawChart(dataY) #draw single plot for single/multi data
#drawHeatMap(dataY, colorMap) #draw single heatmap
#drawChartMulti # draw multi plots for single/multi data
#
#heatmapPlotNumber, heatmapPlot = drawHeatMap(dataY, colorMap, interaction, otherPlotNumber, otherPlotData) #draw single heatmap with interaction among plots
#drawChartInteractionWithHeatmap([startEnd, startEndInterval], 10, type='line', seriesType=['column', 'line'],  minWidth=300, height=400, lineWidth=3, titleText='titleText', yAxisTitle='yAxisTitle', subtitleText='subtitleText', legend=True, heatmapPlot=heatmapPlot, heatmapPlotNumber=heatmapPlotNumber)

def addJSlibs():
    return """
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
    <script src="https://code.highcharts.com/highcharts.js"></script>
    """
    
def addJSlibsPolar():
    print """
    <script src="https://code.highcharts.com/highcharts-more.js"></script>
    """
def addJSlibsHeatmap():
    return """
    <script src="https://code.highcharts.com/modules/data.js"></script>
    <script src="https://code.highcharts.com/modules/heatmap.js"></script>
    
    <script>
    
    function linkDownload(a, filename, content) {
        contentType =  'data:application/octet-stream,';
        uriContent = contentType + encodeURIComponent(content);
        a.setAttribute('href', uriContent);
        a.setAttribute('download', filename);
      }
      
      
      function downloadFileReads(filename) {
      
        var a = document.createElement('a');
        var content = ''
        var dataRes = document.getElementsByClassName("hiddenClass");
        
        for (var i = 0; i < dataRes.length; ++i) 
        {
            var item = dataRes[i]; 
            var idN = item.id;
            
            console.log(item);
            //console.log('item', filename, item.id, item.value, idN.indexOf(filename), filename.indexOf(idN)); 
            
            if(idN.indexOf(filename) > -1)
            {
                if (item.value!='')
                {
                    content += item.value  + '\\n';
                }
                dataRes[i].value = '';
            }
            console.log(dataRes[i]);
        }
        
        
        
        linkDownload(a, filename, content);
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      }
    </script>
    
    """
    

def axaddJSlibsOverMouseAxisisPopup():
    from config.Config import DATA_FILES_PATH, STATIC_PATH, STATIC_REL_PATH

    import os
    relPath = os.path.join('data', 'visualization', 'tooltipsy.min.js')
    url = '/'.join([STATIC_REL_PATH, relPath])

    return '<script src="' + str(url) + '"></script>'

def addJSlibsExport():
    #http://www.highcharts.com/component/content/article/2-news/52-serverside-generated-charts
    return """<script src="https://code.highcharts.com/modules/exporting.js"></script>"""


def _addGuidelineV1(tableName='tn'):
        
        strText = """ 
        
        <br \><p class="infomessage"><a href='#' class='""" + str(tableName) + """clickme'>Show instructions for plots</a></p>
        
        
        """
        
        strText += """ <div id ='""" + str(tableName) + """plot'  style='display:none;min-width:400px;margin-top:10px;border:1px solid #000033;padding:10px;color:#181818' >
            <div id ='guideLine'  style='font-weght:bold;text-transform:uppercase;margin-bottom:5px;'>
            Guidelines for viewing the plots:
            </div>

            <div id ='option1d'  style='font-weght:bold;margin-bottom:5px;margin-top:5px;'>
            Sorting:
            </div>
            - To sort a plot by a column, click on the column header in the table.

            <div id ='option1d'  style='font-weght:bold;margin-bottom:5px;margin-top:5px;'>
            Zooming:
            </div>
            
            - To zoom a plot representing one dataset, e.g. one line, click on the plot and drag your mouse to the left/right side.<br \>s
            - To zoom when viewing multiple plots that represent related datasets, in the same output page, zooming one plot will automatically zoom all plots.<br \>
            - To reset the zooming press the button: Reset zoom

            <div id ='option1d'  style='font-weght:bold;margin-bottom:5px;margin-top:5px;'>
            Show/Hide:
            </div>

            - To show/hide a specific dataset in the plot, click the colored checkbox next to the name of that dataset located in the legend below the plot.

            <div id ='option1d'  style='font-weght:bold;margin-bottom:5px;margin-top:5px;'>
            Print and download:
            </div>

            - To print or download, open the context menu, located in the top right corner of the plot, and choose from there.

           <div id ='option1d'  style='font-weght:bold;margin-bottom:5px;margin-top:5px;'>
            Heatmap:
            </div>
            - To select a specific region and download it locally as a group of .bed files, click the region of interest (or multiple regions by using ctrl/cmd) and press the Get selected regions button. The .bed file/files will appear above the heatmap where they can be downloaded.



        </div>

        """

        strText += """
        <script>
        
        $('.""" + str(tableName) + """clickme').on('click', function(e) {
                console.log('#""" + str(tableName) + """plot');
                $('#""" + str(tableName) + """plot').slideToggle('fast');
                
            });
        
        </script>
        
        
        """
        
        return strText


def addGuideline(htmlCore):
    htmlCore.divBegin('plotDiv', style="min-width:400px;border:1px solid #000033;padding:10px;color:#181818")
    htmlCore.divBegin('guideLine', style="font-weght:bold;text-transform:uppercase;margin-bottom:5px;")
    htmlCore.line('Guidelines for viewing the plots:')
    htmlCore.divEnd()
    htmlCore.divBegin('option1d', style="font-weght:bold;margin-bottom:5px;margin-top:5px;")
    htmlCore.line('Sorting:')
    htmlCore.divEnd()
    htmlCore.line('- To sort a plot by a column, click on the column header in the table.')
     
    htmlCore.divBegin('option1', style="font-weght:bold;margin-bottom:5px;margin-top:5px;")
    htmlCore.line('Zooming:')
    htmlCore.divEnd()
    htmlCore.line('- To zoom a plot representing one dataset, e.g. one line, click on the plot and drag your mouse to the left/right side.')
    htmlCore.line('- To zoom when viewing multiple plots that represent related datasets, in the same output page, zooming one plot will automatically zoom all plots.')
    htmlCore.line('- To reset the zooming press the button: \"Reset zoom\"')
    
    htmlCore.divBegin('option1', style="font-weght:bold;margin-bottom:5px;margin-top:5px;")
    htmlCore.line('Show/Hide:')
    htmlCore.divEnd()
    
    htmlCore.line('- To show/hide a specific dataset in the plot, click the colored checkbox next to the name of that dataset located in the legend below the plot.')
    
    htmlCore.divBegin('option1', style="font-weght:bold;margin-bottom:5px;margin-top:5px;")
    htmlCore.line('Print and download:')
    htmlCore.divEnd()
    
    htmlCore.line('- To print or download, open the context menu, located in the top right corner of the plot, and choose from there.')
    
    htmlCore.divBegin('option1', style="font-weght:bold;margin-bottom:5px;margin-top:5px;")
    htmlCore.line('Heatmap:')
    htmlCore.divEnd()
    
    htmlCore.line('- To select a specific region and download it locally as a group of .bed files, click the region of interest (or multiple regions by using ctrl/cmd) and press the \"Get selected regions\" button. The .bed file/files will appear above the heatmap where they can be downloaded.')
    htmlCore.divEnd()
    
    return htmlCore

def useThemePlot():
    scriptText = """<script>
    Highcharts.createElement('link', {
    href: 'https://fonts.googleapis.com/css?family=Dosis:400,600',
    rel: 'stylesheet',
    type: 'text/css'
 }, null, document.getElementsByTagName('head')[0]);

 Highcharts.theme = {
    colors: ["#7cb5ec", "#f7a35c", "#90ee7e", "#7798BF", "#aaeeee", "#ff0066", "#eeaaee",
       "#55BF3B", "#DF5353", "#7798BF", "#aaeeee"],
    chart: {
       backgroundColor: null,
       style: {
          fontFamily: "Dosis, sans-serif"
       }
    },
    title: {
       style: {
          fontSize: '16px',
          fontWeight: 'bold',
          textTransform: 'uppercase'
       }
    },
    tooltip: {
       borderWidth: 0,
       backgroundColor: 'rgba(219,219,216,0.8)',
       shadow: false,
       position:absolute
    },
    legend: {
       itemStyle: {
          fontWeight: 'bold',
          fontSize: '13px'
       }
    },
    xAxis: {
       gridLineWidth: 1,
       labels: {
          style: {
            fontSize: '12px'
          }
       }
    },
    yAxis: {
       minorTickInterval: 'auto',
       title: {
          style: {
             textTransform: 'uppercase'
          }
       },
       labels: {
          style: {
             fontSize: '12px'
          }
       }
    },
    plotOptions: {
       candlestick: {
          lineColor: '#404048'
       }
    },


    // General
    background2: '#F0F0EA'
    
 };

    Highcharts.setOptions(Highcharts.theme);
    </script>
    <style>
    .tooltipsy
    {
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
    </style>
    """
    return scriptText



def depth(l):
    if isinstance(l, list):
        return 1 + max(depth(item) for item in l)
    else:
        return 0


#dataY = [1, 2] OR dataY = [[1, 2, 3], [1, 5, 5]]
#tickInterval=1 OR categories = ['one', 'two', 'three'],
#type='line' OR 'column' OR 'area'
#minWidth=300
#height=400
#lineWidth=1
#titleText='Plot text'
#seriesType=['area', 'line', 'column', 'spline']
#seriesName=['one', 'two']
#yAxisTitle='Title'
#subtitleText='Subtitle'
#legend=True OR False
#plotNumber=1 IMPORTANT (each plot has to be have own number starting from 1)
#dataLabels=True
#polar=False (polar plot)
#label <b>{series.name}: </b>{point.y}{point.x}<br/>
def drawChart(dataY, tickInterval=1, tickMinValue=None, type='line', label='<b>{series.name}: </b>{point.y}', minWidth=300, height=800, lineWidth=1, titleText='', categories=None, seriesType='', seriesName='', yAxisTitle='', subtitleText='', legend=True, plotNumber=1, xAxisRotation=0, dataLabels=True, polar=False, stacked=False, shared=True, overMouseAxisX=False, overMouseLabelX=' + this.value + ', showChartClickOnLink=False, typeAxisXScale=None, pointStartLog=None):

    container=''
    jsCodeShowChartClickOnLink=''
    addOptionJsCodeShowChartClickOnLink=''
    if showChartClickOnLink==True:
        jsCodeShowChartClickOnLink = """
        <script type="text/javascript">
        jQuery(document).ready(function() {
                $("#linkContainer""" + str(plotNumber) + """").click(function() {
                        $("#container""" + str(plotNumber) + """").slideDown("slow");
                });
        });
        </script>"""
        addOptionJsCodeShowChartClickOnLink = """display:none; """
        container = """<div id='container""" + str(plotNumber) + """' style='""" + str(addOptionJsCodeShowChartClickOnLink) + """ width: 100%; height: """ + str(height) + """px;'></div>"""
    else:
        container = """<div id='container""" + str(plotNumber) + """' style='""" + str(addOptionJsCodeShowChartClickOnLink) + """min-width: """ + str(minWidth) + """; height: """ + str(height) + """px; margin: 0 auto'></div>"""
    
    if tickInterval==None:
        tickInterval= ""
    elif tickInterval==False:
        tickInterval= """ tickInterval: """ + str('null') + """, """
    else:
        tickInterval= """ tickInterval: """ + str(tickInterval) + """, """
        
    if tickMinValue ==None:
        tickMinValue = ""
    else:
        tickMinValue = """min: """ + str(tickMinValue) + ""","""
    
    if categories == None:
        categories = ""
    else:
        categories = """categories: """ + str(categories) + """, """
    
    if pointStartLog == None:
        pointStartLog = ""
    else:   
        pointStartLog = """ pointStart: 1,"""
        
    if typeAxisXScale == None:
        typeAxisXScale = ""
    else:
        typeAxisXScale = """type: 'logarithmic', """
   
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

    
    if legend == True:
        legend = """ legend: {
                layout: 'vertical',
                align: 'right',
                verticalAlign: 'middle',
                borderWidth: 0
            },"""
    else:
        legend=''
        
        
    if dataLabels == True: 
        dataLabels = """fillColor: { 
                        linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1},
                        stops: [
                            [0, Highcharts.getOptions().colors[0]],
                            [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                        ]
                    },"""
    else:
        dataLabels=""" dataLabels: { enabled: true },
         enableMouseTracking: false, """
    
    if polar==True:
        polar= ', polar: true'  
    else:
        polar=''
        
    if stacked == True:
        stacked = " stacking: 'normal', "
    else:
        stacked=''
    if shared==True:
        shared='true' 
    else:
        shared='false' 
    
    functionJS1 = """ <script> $(function () { 
        $('#container""" + str(plotNumber) + """').highcharts({
        chart: { zoomType: 'x' """ + polar +   """ , marginTop: 60, },
        title: { text: '""" + titleText + """'  },
        subtitle: { text: '""" + subtitleText + """'},
        xAxis: {  """ + tickInterval +  tickMinValue + categories +  typeAxisXScale + """
                  labels: {rotation:""" + str(xAxisRotation) + labelX + """}
                },
            yAxis: { 
                title: { text: '""" + yAxisTitle + """' }
            },
            plotOptions: {
                """ + type + """: { """ + stacked + dataLabels + """
                    lineWidth: """ + str(lineWidth) + """,
                    pointPadding: 0.2,
                    borderWidth: 0
                }
               
            },
            tooltip: {
                headerFormat: '',
                pointFormat: '""" + label + """', 
                footerFormat: '',
                shared: """ + shared + """,
                crosshairs: true,
                useHTML: true,
                crosshairs: true
            }, """ + legend + """
            series: [{ """ + pointStartLog 
    
    if isinstance(dataY[0], list) == True:
        i=0
        for d in dataY:
            if i==0:
                data = '{0}{1}{2}{3}{4}{5}'.format(""" type: '""" + seriesType[0] + """', """ ,  """  name: """, "'" if seriesName=='' else "'" + seriesName[i] ,"""', data: """, d, """ } """ )
            else:
                data = data + '{0}{1}{2}{3}{4}{5}'.format(""" , { type: '"""  + seriesType[i] + """', """ ,"""name: """ , "'" if seriesName=='' else "'" + seriesName[i] , """', data: """, d, """ } """ )
            i+=1
    else:
        data = '{0}{1}{2}{3}{4}{5}'.format(""" type: '""" + seriesType[0] + """', """  ,"""  name: """, "'" if seriesName=='' else "'" + seriesName[0] , """', data: """, dataY, """ } """ )
                    
    functionJS2 = """ ] }); }); </script> """
    
    
    return '{0}{1}{2}{3}{4}'.format(jsCodeShowChartClickOnLink, container, functionJS1, data, functionJS2)

        

def drawHeatMap(dataY, colorMap, tickInterval=1, minWidth=1000,  height=600, label='this.point.value',  titleText='', categories="''", yAxisTitle='', subtitleText='',plotNumber=1, marginBottom=100, xAxisRotation=90, interaction=False, otherPlotNumber='', otherPlotData='', overMouseAxisX=False, overMouseAxisY=False, yAxisNameOverMouse='', overMouseLabelX=' + this.value + ', overMouseLabelY=' + this.value + ', extrOp=''):
    
#     dataYTemp = dataY
#     dataYTemp.reverse()
    
    if overMouseAxisY==True:
        labelY = """ labels: {
                useHTML: true,
                formatter: function () {
                    return '<div class="hastip" title="' """ + overMouseLabelY + """ '" >' + this.value + '</div>';
                }
            }, """
        yAxisMO = """ $('.hastip').tooltipsy(); """
    else:
        labelY=''
        yAxisMO=''

    if overMouseAxisY==True:
        labelX = """
                useHTML: true,
                formatter: function () {
                    
                    return '<div class="hastip" title="' + this.value + ' ">' """ + overMouseLabelX + """ '</div>';
                },
        """
    else:
        labelX=''
    
    if interaction == True:
        plotNumberInteraction = len(otherPlotData)
    
    style = """
        <style>
    .highcharts-tooltip>span {
        background: rgba(255,255,255,0.85);
        border: 1px solid silver;
        border-radius: 3px;
        box-shadow: 1px 1px 2px #888;
        padding: 8px;
        z-index: 2;
    }
    </style>
    
    <script>
    
    var dataToBed =[];
    var dataYToBed = """ + str(categories) + """;
    var staticFile = """ + str(extrOp) + """;
    
    </script>
    
    <style>
    
    .downLink {
    cursor: pointer;
    }
    
    </style>
    
    """
    container = """<button id="button" class="autocompare">Get selected regions</button><br \><br \>"""
    
    
    for el in yAxisNameOverMouse:
        container += """ <div style='display:none;' id ='""" + str(el) + """'> """
        
        container += """ <div style='float:left;width:80%;padding:10px;font-weight:bold;border:1px dotted #010101;'> """
        container += str(el)
        container += """ </div> """
        container += ''' <div  class='downLink' style='float:left;width:20%;padding:10px;border:1px dotted #010101;' onclick='downloadFileReads("''' + str(el.replace(' ',' ')) + '''")'>download</div> '''
        
        container += """ </div> <div style='clear:both;' > </div>"""
        
    
        
    container += """<div id='container""" + str(plotNumber) + """' style='min-width: """ + str(minWidth) + """px; height: """ + str(height) + """px; margin: 0 auto'></div><pre id="csv" style="display: none">data\n
    
    
    """ 
  
    i=0
    j=1
    data=''
    for d in dataY:
        j=0
        for dd in d:
            data = data +  "{},{},{} {} ".format(j, i, dd, '\n')
            j+=1
        i+=1

    container= "{} {} {}".format(container,data,'</pre>')
 
 
    functionJS1="""<script>
    
    
    $(function () {

    /**
     * This plugin extends Highcharts in two ways:
     * - Use HTML5 canvas instead of SVG for rendering of the heatmap squares. Canvas
     *   outperforms SVG when it comes to thousands of single shapes.
     * - Add a K-D-tree to find the nearest point on mouse move. Since we no longer have SVG shapes
     *   to capture mouseovers, we need another way of detecting hover points for the tooltip.
     */
    (function (H) {
        var wrap = H.wrap,
            seriesTypes = H.seriesTypes;
        /**
         * Recursively builds a K-D-tree
         */
        function KDTree(points, depth) {
            var axis, median, length = points && points.length;

            if (length) {

                // alternate between the axis
                axis = ['plotX', 'plotY'][depth % 2];

                // sort point array
                points.sort(function (a, b) {
                    return a[axis] - b[axis];
                });

                median = Math.floor(length / 2);

                // build and return node
                return {
                    point: points[median],
                    left: KDTree(points.slice(0, median), depth + 1),
                    right: KDTree(points.slice(median + 1), depth + 1)
                };

            }
        }

        /**
         * Recursively searches for the nearest neighbour using the given K-D-tree
         */
        function nearest(search, tree, depth) {
            var point = tree.point,
                axis = ['plotX', 'plotY'][depth % 2],
                tdist,
                sideA,
                sideB,
                ret = point,
                nPoint1,
                nPoint2;

            // Get distance
            point.dist = Math.pow(search.plotX - point.plotX, 2) +
                Math.pow(search.plotY - point.plotY, 2);

            // Pick side based on distance to splitting point
            tdist = search[axis] - point[axis];
            sideA = tdist < 0 ? 'left' : 'right';

            // End of tree
            if (tree[sideA]) {
                nPoint1 = nearest(search, tree[sideA], depth + 1);

                ret = (nPoint1.dist < ret.dist ? nPoint1 : point);

                sideB = tdist < 0 ? 'right' : 'left';
                if (tree[sideB]) {
                    // compare distance to current best to splitting point to decide wether to check side B or not
                    if (Math.abs(tdist) < ret.dist) {
                        nPoint2 = nearest(search, tree[sideB], depth + 1);
                        ret = (nPoint2.dist < ret.dist ? nPoint2 : ret);
                    }
                }
            }
            return ret;
        }

        // Extend the heatmap to use the K-D-tree to search for nearest points
        H.seriesTypes.heatmap.prototype.setTooltipPoints = function () {
            var series = this;

            this.tree = null;
            setTimeout(function () {
                series.tree = KDTree(series.points, 0);
            });
        };
        H.seriesTypes.heatmap.prototype.getNearest = function (search) {
            if (this.tree) {
                return nearest(search, this.tree, 0);
            }
        };

        H.wrap(H.Pointer.prototype, 'runPointActions', function (proceed, e) {
            var chart = this.chart;
            proceed.call(this, e);

            // Draw independent tooltips
            H.each(chart.series, function (series) {
                var point;
                if (series.getNearest) {
                    point = series.getNearest({
                        plotX: e.chartX - chart.plotLeft,
                        plotY: e.chartY - chart.plotTop
                    });
                    if (point) {
                        point.onMouseOver(e);
                    }
                }
            })
        });

        /**
         * Get the canvas context for a series
         */
        H.Series.prototype.getContext = function () {
            var canvas;
            if (!this.ctx) {
                canvas = document.createElement('canvas');
                canvas.setAttribute('width', this.chart.plotWidth);
                canvas.setAttribute('height', this.chart.plotHeight);
                canvas.style.position = 'absolute';
                canvas.style.z-index = 5;
                canvas.style.left = this.group.translateX + 'px';
                canvas.style.top = this.group.translateY + 'px';
                canvas.style.zIndex = 0;
                canvas.style.cursor = 'crosshair';
                this.chart.container.appendChild(canvas);
                if (canvas.getContext) {
                    this.ctx = canvas.getContext('2d');
                }
            }
            return this.ctx;
        }

        /**
         * Wrap the drawPoints method to draw the points in canvas instead of the slower SVG,
         * that requires one shape each point.
         */
        H.wrap(H.seriesTypes.heatmap.prototype, 'drawPoints', function (proceed) {

            var ctx;
            if (this.chart.renderer.forExport) {
                // Run SVG shapes
                proceed.call(this);

            } else {

                if (ctx = this.getContext()) {

                    // draw the columns
                    H.each(this.points, function (point) {
                        var plotY = point.plotY,
                            shapeArgs;

                        if (plotY !== undefined && !isNaN(plotY) && point.y !== null) {
                            shapeArgs = point.shapeArgs;

                            ctx.fillStyle = point.pointAttr[''].fill;
                            ctx.fillRect(shapeArgs.x, shapeArgs.y, shapeArgs.width, shapeArgs.height);
                        }
                    });

                } else {
                    this.chart.showLoading("Your browser doesn't support HTML5 canvas, <br>please use a modern browser");

                    // Uncomment this to provide low-level (slow) support in oldIE. It will cause script errors on
                    // charts with more than a few thousand points.
                    //proceed.call(this);
                }
            }
        });
    }(Highcharts));
    
    """
    heatmapPlot=''
    if overMouseAxisY==True:
        heatmapPlot = 'var ' + heatmapPlot + 'yAxisNameOverMouse =' + str(yAxisNameOverMouse) + ';'
    
    if interaction == True:
        heatmapPlot = heatmapPlot + """ chart""" + str(plotNumber) + """= new Highcharts.Chart({
            chart: { margin: [60, 10, 220, 50], type: 'heatmap', zoomType: 'x' , renderTo: 'container""" + str(plotNumber) + """', isZoomed:false }, 
            """
    else:
        heatmapPlot = """    var start; 
        $('#container""" + str(plotNumber) + """').highcharts({
             chart: {
                        type: 'heatmap',
                        margin: [60, 10, """ + str(marginBottom) + """, 50]
                    },
        """
    heatmapPlot = heatmapPlot + """    

        data: {
            csv: document.getElementById('csv').innerHTML,
            parsed: function () {
                start = +new Date();
            }
        },

       

        title: {
            text: '""" + titleText + """',
            align: 'left',
            x: 40
        },

        subtitle: {
            text: '""" + subtitleText + """',
            align: 'left',
            x: 40
        },

        tooltip: {
            backgroundColor: null,
            borderWidth: 0,
            distance: 10,
            shadow: false,
            useHTML: true,
            style: {
                padding: 0,
                color: 'black'
            }
        },

        xAxis: {
            min: """ + str(0.01) +  """,
            max: """ + str(len(dataY[0])-1) +  """,
            labels: {
                align: 'left',
                x: 0,
                format: '{value}', """ + labelX + """
                rotation:""" + str(xAxisRotation) + """ 
            },
            showLastLabel: true,
            tickInterval: """ + str(tickInterval) + """,  
            tickmarkPlacement: 'between',
            categories: """ + str(categories) 
    if interaction == True:          
        heatmapPlot = heatmapPlot +          """
          , events:{
                    afterSetExtremes:function(){
                         if (!this.chart.options.chart.isZoomed)
                         {                                         
                            var xMin = this.chart.xAxis[0].min;
                            var xMax = this.chart.xAxis[0].max;
                             
                            var zmRange = computeTickInterval(xMin, xMax);
                                """
        heatmapPlot = heatmapPlot + """chart""" + str(plotNumber) + """.xAxis[0].options.tickInterval =zmRange;
                      chart""" + str(plotNumber) + """.xAxis[0].isDirty = true; """
        for kk in range(otherPlotNumber, otherPlotNumber+plotNumberInteraction):
                heatmapPlot = heatmapPlot + """chart""" + str(plotNumber) + """.xAxis[0].options.tickInterval =zmRange;
                          chart""" + str(plotNumber) + """.xAxis[0].isDirty = true; chart""" + str(kk) + """.options.chart.isZoomed = true; 
                                                chart""" + str(kk) + """.xAxis[0].setExtremes(xMin, xMax, true);
                                                chart""" + str(kk) + """.options.chart.isZoomed = false;
                                    """                        
        heatmapPlot = heatmapPlot +    """ } } } """
        
    heatmapPlot = heatmapPlot +  """    
    },

        yAxis: {
            title: {
                text: '""" + yAxisTitle + """'
            },
            labels: {
                format: '{value}'
            },
            """ + labelY + """
            minPadding: 0,
            maxPadding: 0,
            startOnTick: false,
            endOnTick: false,
            tickWidth: 1,
            min: 0,
            max: """ + str(len(dataY)-1) +  """,
            tickInterval: """ + str(tickInterval) +  """
        },
        
        plotOptions: {
            series: {
                allowPointSelect: true,
                /*
                events: {
                    click: function (event) {
                        console.log(this);    
                        dataToBed.push([this.series.xAxis.categories[this.point.x], yAxisNameOverMouse[this.point.y]]);
                        console.log(dataToBed);
                    }
                }
                */
            }
        },

        colorAxis: {
            stops: """ + str(colorMap) + """,
            min: 0,
            max: 1,
            startOnTick: false,
            endOnTick: false,
            labels: {
                format: '{value}'
            }
        },
        tooltip: {
            formatter: function () {
                return """ + label + """;
            }
        },
        series: [{
            borderWidth: 0,
            nullColor: '#EFEFEF',
            colsize: 1.01,
            turboThreshold: Number.MAX_VALUE // #3404, remove after 4.0.5 release
        }]

    }
    """
    if interaction == True:
        heatmapPlot = heatmapPlot+ """ , function(chart) { """ + yAxisMO + """ syncronizeCrossHairs(chart); }
                    );  """
    else:
        heatmapPlot = heatmapPlot + """ , function(chart) { """ + yAxisMO + """ ); """
    
    
    heatmapPlot += """
    
   function addInput(name, val) {
    var input = document.createElement('input');
    input.setAttribute("id", name);
    input.setAttribute('type', 'hidden');
    input.setAttribute('value', val);
    input.setAttribute('class', 'hiddenClass');
    document.body.appendChild(input);
}
    
    $('#button').click(function () {
    
            //console.log('#container""" + str(plotNumber) + """');
    
            var chart = $('#container""" + str(plotNumber) + """').highcharts();
            
            
            var selectedPoints = chart.getSelectedPoints();
            //console.log('staticFile', staticFile);
            
            var x=0;
            var y=0;
            
            var dictRes={};
            var data = [];
            
            for (var i=0; i<selectedPoints.length;i++)
            {
                x = selectedPoints[i].options.x;
                y = selectedPoints[i].options.y;
                
                if (!(yAxisNameOverMouse[y] in dictRes))
                {
                    dictRes[yAxisNameOverMouse[y]] = [];
                    data.push([yAxisNameOverMouse[y], '<button id="button" class="autocompare">Download file</button>']);
                }
                
                var res = dataYToBed[x].split(':');
                var res1 = res[1].split('-');
                var res2 = res1[0].split(' ');
                var res3 = res1[1].split(' ');
                
                dictRes[yAxisNameOverMouse[y]].push([res[0] + '\t' + parseInt(res2[0]) + '\t' + parseInt(res3[0])]);
                console.log(x, y, dataYToBed[x], yAxisNameOverMouse[y], dictRes, res[0], res2[0], res3[0]);
            }
            //dictRes
            
            for (var i=0; i< yAxisNameOverMouse.length;i++)
            {
                name = yAxisNameOverMouse[i];
                document.getElementById(name).style.display = "none";
            }
            
            for (var key in dictRes) 
            {
                var value = dictRes[key];
                
                document.getElementById(key).style.display = "block";
                
                for (var i=0; i< value.length;i++)
                {
                    name = "'" + key + "-" + i + "'";
                    console.log(key, name, value[i]);   
                    addInput(name, value[i]);   
                }
            
            }
            
            
        });
        
    
    """
    
    functionJS3 = """ });
    
    
    
    </script> """
    
    if interaction == False:
        return '{0}{1}{2}{3}{4}'.format(style, container, functionJS1, heatmapPlot, functionJS3)
    else:
        hm =  '{0}{1}{2}{3}'.format(style, container, functionJS1, functionJS3)
        return hm, plotNumber, heatmapPlot


def addDynamicsStart(plotNumber, plotNumberInteraction, heatmapPlotNumber):
    functionJS = """<script>
    $(function() { """
    
    for kk in range(plotNumber, plotNumber+plotNumberInteraction):
        functionJS = functionJS + " var char" + str(kk) + ";"
    if heatmapPlotNumber!= '':
        functionJS = functionJS + "var char" + str(heatmapPlotNumber)+ ";"
    functionJS = functionJS + """var controllingChart;
    
    var defaultTickInterval = 1;
    var currentTickInterval = defaultTickInterval;
    
    $(document).ready(function() {
        function unzoom() { """
    
    for kk in range(plotNumber, plotNumber+plotNumberInteraction):
        functionJS = functionJS + """
            chart""" + str(kk) + """.options.chart.isZoomed = false;
            chart""" + str(kk) + """.xAxis[0].setExtremes(null, null);"""
    if heatmapPlotNumber!='':
        functionJS = functionJS + """chart""" + str(heatmapPlotNumber) + """.options.chart.isZoomed = false;
                chart""" + str(heatmapPlotNumber) + """.xAxis[0].setExtremes(null, null);
        """
    
    functionJS = functionJS +   """ }
        function syncronizeCrossHairs(chart) {
            var container = $(chart.container),
                offset = container.offset(),
                x, y, isInside, report;

            container.mousemove(function(evt) {

                x = evt.clientX - chart.plotLeft - offset.left;
                y = evt.clientY - chart.plotTop - offset.top;
                var xAxis = chart.xAxis[0];
                //remove old plot line and draw new plot line (crosshair) for this chart
       """
    for kk in range(plotNumber, plotNumber+plotNumberInteraction):
        functionJS = functionJS + """         
                var xAxis""" + str(kk) + """ = chart""" + str(kk) + """.xAxis[0];
                xAxis""" + str(kk) + """.removePlotLine("myPlotLineId");
                xAxis""" + str(kk) + """.addPlotLine({
                    value: chart.xAxis[0].translate(x, true),
                    width: 1,
                    color: 'red',
                    //dashStyle: 'dash',                   
                    id: "myPlotLineId"
                });
        """  
    if heatmapPlotNumber!='':      
        functionJS = functionJS + """         
                    var xAxis""" + str(heatmapPlotNumber) + """ = chart""" + str(heatmapPlotNumber) + """.xAxis[0];
                    xAxis""" + str(heatmapPlotNumber) + """.removePlotLine("myPlotLineId");
                    xAxis""" + str(heatmapPlotNumber) + """.addPlotLine({
                        value: chart.xAxis[0].translate(x, true),
                        width: 1,
                        color: 'red',
                        //dashStyle: 'dash',                   
                        id: "myPlotLineId"
                    });
            """        
    functionJS = functionJS + """                        
            });
        }

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
    for kk in range(plotNumber, plotNumber+plotNumberInteraction):
        functionJS = functionJS + """  
        chart""" + str(kk) + """.xAxis[0].options.tickInterval = currentTickInterval;
        chart""" + str(kk) + """.xAxis[0].isDirty = true;
    """
    if heatmapPlotNumber!='':
        functionJS = functionJS + """  
        chart""" + str(heatmapPlotNumber) + """.xAxis[0].options.tickInterval = currentTickInterval;
        chart""" + str(heatmapPlotNumber) + """.xAxis[0].isDirty = true;
    """
    
    functionJS = functionJS + """    
    }
    //reset the extremes and the tickInterval to default values
    function unzoom() {
    """
    
    for kk in range(plotNumber, plotNumber+plotNumberInteraction):
        functionJS = functionJS + """  
        chart""" + str(kk) + """.xAxis[0].options.tickInterval = defaultTickInterval;
        chart""" + str(kk) + """.xAxis[0].isDirty = true;
        chart""" + str(kk) + """.xAxis[0].setExtremes(null, null);
        """
    if heatmapPlotNumber!='':
        functionJS = functionJS + """  
        chart""" + str(heatmapPlotNumber) + """.xAxis[0].options.tickInterval = defaultTickInterval;
        chart""" + str(heatmapPlotNumber) + """.xAxis[0].isDirty = true;
        chart""" + str(heatmapPlotNumber) + """.xAxis[0].setExtremes(null, null);
        """
    functionJS = functionJS + """ }

            $(document).ready(function() {

                
                $('#btn').click(function(){
                    unzoom();
                });
                
                var myPlotLineId = "myPlotLine";
        
    """
    return functionJS

def addDynamicsEnd():
    return """ }); }); });</script>"""

#dataY = [[1, 2], [3, 4]] OR dataY = [[[1, 2, 3], [1, 5, 5]], [[1, 2, 3], [1, 5, 5]]]
#seriesType=['area', 'line', 'column', 'spline'] OR #seriesType=[['area', 'line'], ['column', 'spline']]
def drawChartMulti(dataY, tickInterval=1, type='line', minWidth=300, label='<b>{series.name}: </b>{point.y}<br/>', height=400, lineWidth=1, titleText='', categories="''", seriesType='', seriesName='', yAxisTitle='', subtitleText='', legend=True, plotNumber=1, dataLabels=True, polar=False, interaction=True, enabled=True, plotBandsY=''):
    
    plotNumberInteraction = len(dataY)
    dataYDepth = depth(dataY)
    
    container=''
    if interaction == True:
        container='<button id="btn">Reset zoom</button>'
        

    for i in range(plotNumber, plotNumber+plotNumberInteraction):
        container = container + """<div id='container""" + str(i) + """' style='min-width: """ + str(minWidth) + """px; height: """ + str(height) + """px; margin: 0 auto'></div>"""
  
     
    if legend == True:
        legend = """ legend: {
                layout: 'vertical',
                align: 'right',
                verticalAlign: 'middle',
                borderWidth: 0
            },"""
    else:
        legend=''
        
    if enabled==True:
        enabled=''
    else:
        enabled= """,  labels: { enabled: false } """
  
    if list(plotBandsY):
        plotBandsY = """
        ,plotBands: [{
                color: '""" + str(plotBandsY[2]) + """',
                from: """ + str(plotBandsY[0]) + """,
                to: """ + str(plotBandsY[1]) + """    ,
                label: {
                text: '""" + str(plotBandsY[3]) + """'
                } 
                  }]
                  """
    
        
    if dataLabels == True: 
        dataLabels = """fillColor: { 
                        linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1},
                        stops: [
                            [0, Highcharts.getOptions().colors[0]],
                            [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                        ]
                    },"""
    else:
        dataLabels=""" dataLabels: { enabled: true },
         enableMouseTracking: false, """
    
    if polar==True:
        polar= ', polar: true'  
    else:
        polar=''
    
    ddd=''
    
    k=plotNumber
    kInd=0
    for dd in dataY:
        functionJS1=''
        if interaction == True:
            functionJS1 = functionJS1 + """ chart""" + str(k) + """= new Highcharts.Chart({
            chart: { zoomType: 'x' """ + polar +   """, renderTo: 'container""" + str(k) + """', isZoomed:false }, 
            """
        else:
            functionJS1 = functionJS1 + """ <script> $(function () { $('#container""" + str(k) + """').highcharts({ 
            chart: { zoomType: 'x' """ + polar +   """ },
            """
        
        functionJS1 = functionJS1 + """
        title: { text: '""" + titleText + """'  },
        subtitle: { text: '""" + subtitleText + """'},
        xAxis: {  tickInterval: """ + str(tickInterval) + """,
                  labels: {rotation: 90}, 
                  categories: """ + str(categories) + """, """
        if interaction == True:          
            functionJS1 = functionJS1 +          """
                  events:{
                            afterSetExtremes:function(){
                                 if (!this.chart.options.chart.isZoomed)
                                 {                                         
                                    var xMin = this.chart.xAxis[0].min;
                                    var xMax = this.chart.xAxis[0].max;
                                     
                                    var zmRange = computeTickInterval(xMin, xMax);
                                        """
            for kk in range(plotNumber, plotNumber+plotNumberInteraction):
                functionJS1 = functionJS1 + """chart""" + str(kk) + """.xAxis[0].options.tickInterval =zmRange;
                              chart""" + str(kk) + """.xAxis[0].isDirty = true; """
                if kk != k:
                    functionJS1 = functionJS1 + """ chart""" + str(kk) + """.options.chart.isZoomed = true; 
                                                    chart""" + str(kk) + """.xAxis[0].setExtremes(xMin, xMax, true);
                                                    chart""" + str(kk) + """.options.chart.isZoomed = false;
                                        """
                                        
                                        
                                        
                                        
            functionJS1 = functionJS1 +    """ } } } """
            
        functionJS1 = functionJS1 +"""
                },
            yAxis: { 
                title: { text: '""" + yAxisTitle[kInd] + """' } """ + enabled + plotBandsY + """
            },
            plotOptions: {
                """ + type + """: { """ + dataLabels + """
                    lineWidth: """ + str(lineWidth) + """,
                    pointPadding: 0.2,
                    borderWidth: 0
                }
               
            },
            tooltip: {
                headerFormat: '',
                pointFormat: '""" + label + """', 
                footerFormat: '',
                shared: true,
                crosshairs: true,
                useHTML: true,
                crosshairs: true
            }, """ + legend + """ series: [{ """
        
        if dataYDepth == 3:    
            i=0
            for d in dd:
                if i==0:
                    data = '{0}{1}{2}{3}{4}{5}'.format(""" type: '""" + seriesType[kInd][0] + """', """ ,  """  name: """, "'" if seriesName=='' else "'" + seriesName[kInd] ,"""', data: """, json.dumps(d), """ } """ )
                else:
                    data = data + '{0}{1}{2}{3}{4}{5}'.format(""" , { type: '"""  + seriesType[kInd][i] + """', """ ,"""name: """ , "'" if seriesName=='' else "'" + seriesName[i] , """', data: """, json.dumps(d), """ } """ )
                i+=1
            data = data + " ] }"    
        elif dataYDepth == 2:
            data='' 
            if k==kInd:
                data = '{0}{1}{2}{3}{4}{5}'.format(""" type: '""" + seriesType[kInd] + """', """ ,  """  name: """, "'" if seriesName=='' else "'" + seriesName[kInd] ,"""', data: """, json.dumps(dd), """ } """ )
            else:
                data = data + '{0}{1}{2}{3}{4}{5}'.format("""   type: '"""  + seriesType[kInd] + """', """ ,"""name: """ , "'" if seriesName=='' else "'" + seriesName[kInd] , """', data: """, json.dumps(dd), """ } """ )
            data = data + " ] }" 

        if interaction == True:
            functionJS2 = """ , function(chart) { //add this function to the chart definition to get synchronized crosshairs
                        syncronizeCrossHairs(chart);
                     });  """
        else:
            functionJS2 = """ ); }); </script> """
            
        ddd = ddd + '{0}{1}{2}'.format(functionJS1, data, functionJS2)
        k+=1
        kInd+=1
   
    
    if interaction == True:
        container = container + addDynamicsStart(plotNumber, plotNumberInteraction, '')
    container = container + ddd
    if interaction == True:
        container = container + addDynamicsEnd()
        
    return container

    


def drawChartInteractionWithHeatmap(dataY, tickInterval=1, label='', type='line', minWidth=300, height=400, extraXAxis='', lineWidth=1, titleText='', categories="''", seriesType='', seriesName='', yAxisTitle='', subtitleText='', legend=True, plotNumber=1, dataLabels=True, polar=False, xAxisRotation=0, heatmapContainer='', heatmapPlot='', heatmapPlotNumber='', overMouseAxisX=False, overMouseLabelX=' + this.value + '):
    
    plotNumberInteraction = len(dataY)
    dataYDepth = depth(dataY)
    
    container='<button id="btn">Reset zoom</button>'
        

    for i in range(plotNumber, plotNumber+plotNumberInteraction):
        container = container + """<div id='container""" + str(i) + """' style='min-width: """ + str(minWidth) + """px; height: """ + str(height) + """px; margin: 0 auto'></div>"""
  
     
    if legend == True:
        legend = """ legend: {
                layout: 'vertical',
                align: 'right',
                verticalAlign: 'middle',
                borderWidth: 0
            },"""
    else:
        legend=''
        
        
    if dataLabels == True: 
        dataLabels = """fillColor: { 
                        linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1},
                        stops: [
                            [0, Highcharts.getOptions().colors[0]],
                            [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                        ]
                    },"""
    else:
        dataLabels=""" dataLabels: { enabled: true },
         enableMouseTracking: false, """
    
    if polar==True:
        polar= ', polar: true'  
    else:
        polar=''
    
    ddd=''
    
    k=plotNumber
    kInd=0
    for dd in dataY:
        if overMouseAxisX==True:
            labelX = """
                ,
                useHTML: true,
                formatter: function () {
                    
                    return '<div class="hastip""" + str(kInd) + """ " title="' + this.value + ' ">' """ + overMouseLabelX + """ '</div>';
                }
        """
            yAxisMO = """ $('.hastip""" + str(kInd) + """').tooltipsy(); """
        else:
            labelX=''
            yAxisMO=''
            
        functionJS1=''
        functionJS1 = functionJS1 + """ chart""" + str(k) + """= new Highcharts.Chart({
        chart: { zoomType: 'x' """ + polar +   """, renderTo: 'container""" + str(k) + """', isZoomed:false }, 
        """
        
        functionJS1 = functionJS1 + """
        title: { text: '""" + titleText[kInd] + """'  },
        subtitle: { text: '""" + subtitleText[kInd] + """'},
        xAxis: {  tickInterval: """ + str(tickInterval) + """,
                  categories: """ + str(categories[kInd]) + """,
                  """ + extraXAxis + """ 
                  labels: {
                  rotation:""" + str(xAxisRotation) + """
                  """ + labelX + """
                  }, """
                
        functionJS1 = functionJS1 +          """
              events:{
                        afterSetExtremes:function(){
                             if (!this.chart.options.chart.isZoomed)
                             {                                         
                                var xMin = this.chart.xAxis[0].min;
                                var xMax = this.chart.xAxis[0].max;
                                 
                                var zmRange = computeTickInterval(xMin, xMax);
                                    """
        for kk in range(plotNumber, plotNumber+plotNumberInteraction):
            functionJS1 = functionJS1 + """chart""" + str(kk) + """.xAxis[0].options.tickInterval =zmRange;
                          chart""" + str(kk) + """.xAxis[0].isDirty = true; """
            if kk != k:
                functionJS1 = functionJS1 + """ chart""" + str(kk) + """.options.chart.isZoomed = true; 
                                                chart""" + str(kk) + """.xAxis[0].setExtremes(xMin, xMax, true);
                                                chart""" + str(kk) + """.options.chart.isZoomed = false;
                                    """
        functionJS1 = functionJS1 + """chart""" + str(heatmapPlotNumber) + """.xAxis[0].options.tickInterval =zmRange;
                          chart""" + str(heatmapPlotNumber) + """.xAxis[0].isDirty = true; chart""" + str(heatmapPlotNumber) + """.options.chart.isZoomed = true; 
                                                chart""" + str(heatmapPlotNumber) + """.xAxis[0].setExtremes(xMin, xMax, true);
                                                chart""" + str(heatmapPlotNumber) + """.options.chart.isZoomed = false;
                                    """
        
        
                                    
                                    
                                    
                                    
        functionJS1 = functionJS1 +    """ } } } """
            
        functionJS1 = functionJS1 +"""
                },
            yAxis: { 
                title: { text: '""" + yAxisTitle[kInd] + """' }
            },
            plotOptions: {
                """ + type + """: { """ + dataLabels + """
                    lineWidth: """ + str(lineWidth) + """,
                    pointPadding: 0.2,
                    borderWidth: 0
                }
               
            },
            tooltip: {
                headerFormat: '',
                pointFormat: '""" + label[kInd] + """', 
                footerFormat: '',
                shared: true,
                crosshairs: true,
                useHTML: true,
                crosshairs: true
            }, """ + legend + """ series: [{ """
        
        if dataYDepth == 3:    
            i=0
            for d in dd:
                if i==0:
                    data = '{0}{1}{2}{3}{4}{5}'.format(""" type: '""" + seriesType[kInd][0] + """', """ ,  """  name: """, "'" if seriesName=='' else "'" + seriesName[kInd][i] ,"""', data: """, d, """ } """ )
                else:
                    data = data + '{0}{1}{2}{3}{4}{5}'.format(""" , { type: '"""  + seriesType[kInd][i] + """', """ ,"""name: """ , "'" if seriesName=='' else "'" + seriesName[kInd][i] , """', data: """, d, """ } """ )
                i+=1
            data = data + " ] }"    
        elif dataYDepth == 2:
            data='' 
            if k==kInd:
                data = '{0}{1}{2}{3}{4}{5}'.format(""" type: '""" + seriesType[kInd] + """', """ ,  """  name: """, "'" if seriesName=='' else "'" + seriesName[kInd] ,"""', data: """, dd, """ } """ )
            else:
                data = data + '{0}{1}{2}{3}{4}{5}'.format("""   type: '"""  + seriesType[kInd] + """', """ ,"""name: """ , "'" if seriesName=='' else "'" + seriesName[kInd] , """', data: """, dd, """ } """ )
            data = data + " ] }" 

        functionJS2 = """ , function(chart) { """ + yAxisMO + """
                    syncronizeCrossHairs(chart);
                 });  """
            
        ddd = ddd + '{0}{1}{2}'.format(functionJS1, data, functionJS2)
        k+=1
        kInd+=1
   
    container = container + addDynamicsStart(plotNumber, plotNumberInteraction, heatmapPlotNumber)
    container = container + ddd + heatmapPlot
    container = container + addDynamicsEnd()
    
    return container



def addDrilldownlibs():
    return  """<script src="https://code.highcharts.com/modules/drilldown.src.js"></script>"""


#data1 = [[], []] - first plot
#data2 = [[[], []], [[],[],[], []], [[], []], []] - second plots     
#dataName0 = ['name1', 'name2', 'name3', 'name4']
#dataName1 = ['xSeries1', 'xSeries1']
#dataName2 = ['SeriesName1','SeriesName2'...]
#categories = ['c1','c2'...]
#typeData2 = 'line' OR 'column' OR each data has own type of series, seriesTypeData2=['line', 'column', ...]
#typeData1 = 'column' OR 'line'


def drawChartDrilldown(data1, data2, dataName0, dataName1, dataName2, categories, typeData1='column', stacking=True, seriesTypeData2='', typeData2='line', titleText='', yAxisTitle='', plotNumber=1, minWidth=300, height=400):
  
    container = """<div id='container""" + str(plotNumber) + """' style='min-width: """ + str(minWidth) + """px; height: """ + str(height) + """px; margin: 0 auto'></div>"""
    
    
    if seriesTypeData2 == '':
        seriesTypeData2 = [typeData2 for dN2 in dataName2]
    
    if stacking == True:
        stacking = "stacking: 'normal'"
    else:
        stacking=''
    
    script =  """
<script> 
$(function () {


    Highcharts.setOptions({
        lang: {
            drillUpText: 'Back to {series.name}'
        }
    });

    (function (H) {
        var noop = function () {},
        defaultOptions = H.getOptions(),
            each = H.each,
            extend = H.extend,
            format = H.format,
            wrap = H.wrap,
            Chart = H.Chart,
            seriesTypes = H.seriesTypes,
            PieSeries = seriesTypes.pie,
            ColumnSeries = seriesTypes.column,
            fireEvent = HighchartsAdapter.fireEvent,
            inArray = HighchartsAdapter.inArray;
        H.wrap(H.Chart.prototype, 'drillUp', function (proceed) {
            var chart = this,
                drilldownLevels = chart.drilldownLevels,
                levelNumber = drilldownLevels[drilldownLevels.length - 1].levelNumber,
                i = drilldownLevels.length,
                chartSeries = chart.series,
                seriesI = chartSeries.length,
                level,
                oldSeries,
                newSeries,
                oldExtremes,
                addSeries = function (seriesOptions) {
                    var addedSeries;
                    each(chartSeries, function (series) {
                        if (series.userOptions === seriesOptions) {
                            addedSeries = series;
                        }
                    });

                    addedSeries = addedSeries || chart.addSeries(seriesOptions, false);
                    if (addedSeries.type === oldSeries.type && addedSeries.animateDrillupTo) {
                        addedSeries.animate = addedSeries.animateDrillupTo;
                    }
                    if (seriesOptions === level.seriesOptions) {
                        newSeries = addedSeries;
                    }
                };
                while (i--) {

                level = drilldownLevels[i];
                 
                if (level.levelNumber === levelNumber) {
                    drilldownLevels.pop();

                    // Get the lower series by reference or id
                    oldSeries = level.lowerSeries;

                    if ($.isArray(oldSeries)) {
                       
       if (chart.series) {
           while (chart.series.length > 0) {
               chart.series[0].remove(false);
           }
       }
        if (level.levelSubtitle) {
            chart.setTitle(null, {text: level.levelSubtitle});
        } else {
            chart.setTitle(null, {
                text: ''
            });
        }
                    if (chart.xAxis && level.levelXAxis) {
                        while (chart.xAxis.length > 0) {
                            chart.xAxis[0].remove(false);
                        }
                    }
                    if (chart.yAxis && level.levelYAxis) {
                        while (chart.yAxis.length > 0) {
                            chart.yAxis[0].remove(false);
                        }
                    }

                    if (level.levelYAxis) {
                        $.each(level.levelYAxis, function () {
                            chart.addAxis(this, false, false);
                        });
                    }
                    if (level.levelXAxis) {
                        $.each(level.levelXAxis, function () {
                            chart.addAxis(this, true, false);
                        });
                    }
                    $.each(level.levelSeriesOptions, function () {
                        chart.addSeries(this, false);
                    });
               

                } else {
                    if (!oldSeries.chart) { // #2786
                        while (seriesI--) {
                            if (chartSeries[seriesI].options.id === level.lowerSeriesOptions.id) {
                                oldSeries = chartSeries[seriesI];
                                break;
                            }
                        }
                    }
                    oldSeries.xData = []; // Overcome problems with minRange (#2898)

                    each(level.levelSeriesOptions, addSeries);

                    fireEvent(chart, 'drillup', {
                        seriesOptions: level.seriesOptions
                    });

                    if (newSeries.type === oldSeries.type) {
                        newSeries.drilldownLevel = level;
                        newSeries.options.animation = chart.options.drilldown.animation;

                        if (oldSeries.animateDrillupFrom) {
                            oldSeries.animateDrillupFrom(level);
                        }
                    }

                    newSeries.levelNumber = levelNumber;

                    oldSeries.remove(false);

                    // Reset the zoom level of the upper series
                    if (newSeries.xAxis) {
                        oldExtremes = level.oldExtremes;
                        newSeries.xAxis.setExtremes(oldExtremes.xMin, oldExtremes.xMax, false);
                        newSeries.yAxis.setExtremes(oldExtremes.yMin, oldExtremes.yMax, false);
                    }

                }
            }
        }

        this.redraw();

        if (this.drilldownLevels.length === 0) {
            console.log('destroy');
            this.drillUpButton = this.drillUpButton.destroy();
        } else {
            console.log('no destroy '+this.drilldownLevels.length);
            this.drillUpButton.attr({
                text: this.getDrilldownBackText()
            })
                .align();
        }

    });

    H.wrap(H.Chart.prototype, 'addSingleSeriesAsDrilldown', function (proceed, point, ddOptions) {

        if (!ddOptions.series) {
            proceed.call(this, point, ddOptions);
        } else {

            var thisChart = this;

            var oldSeries = point.series,
                xAxis = oldSeries.xAxis,
                yAxis = oldSeries.yAxis,
                color = point.color || oldSeries.color,
                pointIndex,
                levelSeries = [],
                levelSeriesOptions = [],
                levelXAxis = [],
                levelYAxis = [],
                levelSubtitle,
                level,
                levelNumber;

            levelNumber = oldSeries.levelNumber || 0;

        //    ddOptions.series[0] = extend({
         //       color: color
        //    }, ddOptions.series[0]);
        //    pointIndex = inArray(point, oldSeries.points);

            // Record options for all current series
            each(oldSeries.chart.series, function (series) {
                if (series.xAxis === xAxis) {
                    levelSeries.push(series);
                    levelSeriesOptions.push(series.userOptions);
                    series.levelNumber = series.levelNumber || 0;
                }
            });

            each(oldSeries.chart.xAxis, function (xAxis) {
                levelXAxis.push(xAxis.userOptions);
            });

            each(oldSeries.chart.yAxis, function (yAxis) {
                levelYAxis.push(yAxis.userOptions);
            });

               
            if(oldSeries.chart.subtitle && oldSeries.chart.subtitle.textStr){
                levelSubtitle = oldSeries.chart.subtitle.textStr;
                
            }

            // Add a record of properties for each drilldown level
            level = {
                levelNumber: levelNumber,
                seriesOptions: oldSeries.userOptions,
                levelSeriesOptions: levelSeriesOptions,
                levelSeries: levelSeries,
                levelXAxis: levelXAxis,
                levelYAxis: levelYAxis,
                levelSubtitle: levelSubtitle,
                shapeArgs: point.shapeArgs,
                bBox: point.graphic.getBBox(),
                color: color,
                lowerSeriesOptions: ddOptions,
                pointOptions: oldSeries.options.data[pointIndex],
                pointIndex: pointIndex,
                oldExtremes: {
                    xMin: xAxis && xAxis.userMin,
                    xMax: xAxis && xAxis.userMax,
                    yMin: yAxis && yAxis.userMin,
                    yMax: yAxis && yAxis.userMax
                }
            };

            // Generate and push it to a lookup array
            if (!this.drilldownLevels) {
                this.drilldownLevels = [];
            }
            this.drilldownLevels.push(level);

            level.lowerSeries = [];

            if (ddOptions.subtitle) {
                this.setTitle(null, {text: ddOptions.subtitle});
            }else{
                this.setTitle(null, {text: ''});
            }

            if (this.xAxis && ddOptions.xAxis) {
                while (this.xAxis.length > 0) {
                    this.xAxis[0].remove(false);
                }
            }
            if (this.yAxis && ddOptions.yAxis) {
                while (this.yAxis.length > 0) {
                    this.yAxis[0].remove(false);
                }
            }
            

            if (ddOptions.yAxis) {
                if ($.isArray(ddOptions.yAxis)) {
                    $.each(ddOptions.yAxis, function () {
                        thisChart.addAxis(this, false, false);
                    });
                } else {
                    thisChart.addAxis(ddOptions.yAxis, false, false);
                }
            }
            if (ddOptions.xAxis) {
                if ($.isArray(ddOptions.xAxis)) {
                    $.each(ddOptions.xAxis, function () {
                        thisChart.addAxis(this, true, false);
                    });
                } else {
                    thisChart.addAxis(ddOptions.xAxis, true, false);
                }

            }



                $.each(ddOptions.series, function () {

                    var newSeries = thisChart.addSeries(this, true);
                    level.lowerSeries.push(newSeries);
                    newSeries.levelNumber = levelNumber + 1;
        //            if (xAxis) {
       //                 xAxis.oldPos = xAxis.pos;
          //              xAxis.userMin = xAxis.userMax = null;
           //             yAxis.userMin = yAxis.userMax = null;
             //       }

               //     // Run fancy cross-animation on supported and equal types
                //    if (oldSeries.type === newSeries.type) {
                 //       newSeries.animate = newSeries.animateDrilldown || noop;
                 //       newSeries.options.animation = true;
                  //  }
                });



            }
        });

        H.wrap(H.Point.prototype, 'doDrilldown', function (proceed, _holdRedraw) {

            if (!$.isPlainObject(this.drilldown)) {
                proceed.call(this, _holdRedraw);
            } else {
                var ddChartConfig = this.drilldown;
               
                var ddSeries = ddChartConfig.series;

                var series = this.series;
                var chart = series.chart;
                var drilldown = chart.options.drilldown;

                var seriesObjs = [];
                for (var i = 0; i < ddSeries.length; i++) {
                    if (!$.isPlainObject(ddSeries[i])) {
                       
                        var j = (drilldown.series || []).length;
                        var seriesObj = null;
                        while (j-- && !seriesObj) {
                            if (drilldown.series[j].id === ddSeries[i]) {
                                seriesObj = drilldown.series[j];
                            }
                        }
                        if (seriesObj) {
                            seriesObjs.push(seriesObj);
                        }
                    } else {
                        seriesObjs.push(ddSeries[i]);
                    }
                }

                ddChartConfig.series = seriesObjs;
                ddSeries = ddChartConfig.series;

                // Fire the event. If seriesOptions is undefined, the implementer can check for 
                // seriesOptions, and call addSeriesAsDrilldown async if necessary.
                HighchartsAdapter.fireEvent(chart, 'drilldown', {
                    point: this,
                    seriesOptions: ddChartConfig
                });

                if (ddChartConfig) {
                    if (_holdRedraw) {
                        chart.addSingleSeriesAsDrilldown(this, ddChartConfig);
                    } else {
                        chart.addSeriesAsDrilldown(this, ddChartConfig);
                    }
                }
            }

        });
    }(Highcharts)); """


    #series 
    dataId = []
    dataTempId=[]
    datadata= ''
    nr=0
    i=0
    dd=0
    c=0
    ll=0
    
    for d2 in data2:
        deep = depth(d2)
        j=0
        dataTempId = []
        if deep == 1:            
            datadata = datadata + """ {   name: '""" + str(dataName2[nr]) + """', type: '""" + str(seriesTypeData2[nr]) + """', id: '""" + str(nr) + """', data: [ """
            dataTempId.append(str(nr))
            nr+=1
        maxLenght =0
        c=0
        for dd2 in d2:
            
            if deep == 2:
                datadata = datadata + """ {   name: '""" + str(dataName2[nr]) + """', type: '""" + str(seriesTypeData2[nr]) + """', id: '""" + str(nr) + """', data: [ """
                k=0
                #dd=0, c=0, c=1, c=2
                dataTempId.append(str(nr))
                if dd!=0:
                    c=c+len(dd2) 
                c=0
                if j==0:
                    ll=ll
                if dd==0:
                    ll=0
                    
                for ddd2 in dd2:
                    datadata = datadata +  """ { name: '""" + str(categories[ll+c]) + """', y: """ + str(ddd2)  + """ } """
                    if not len(dd2) == k+1:
                        datadata = datadata + ", "
                    k+=1
                    c+=1
                datadata = datadata + """ ]} """
                nr+=1
                
                if k >= maxLenght:
                        maxLenght = k
            elif deep == 1:
                datadata = datadata +  """ { name: '""" + str(categories[ll+c]) + """', y: """ + str(dd2)  + """ } """
                if not len(d2) == j+1:
                    datadata = datadata + ", "
                c+=1
            if deep==2 and not len(d2) == i+1:
                datadata = datadata + ", "
                        
            j+=1  
        ll=ll + maxLenght 
        
        
        dataId.append(dataTempId)  
        if deep == 1:
            datadata = datadata + """ ]} """
            if not len(d2) == i:
                datadata = datadata + """ , """         
        i+=1
        dd+=1

        
    script = script + """
    $('#container""" + str(plotNumber) + """').highcharts({
        chart: {
            type: '""" + typeData1 + """'
        },
        tooltip: {
                headerFormat: '',
                pointFormat: '<b>{series.name}: </b>{point.y}<br/>'
        },
        title: {
            text: '""" + str(titleText) + """'
        },
        xAxis: {
            type: 'category'
        },
        yAxis: { 
                title: { text: '""" + yAxisTitle + """' }
            },
        plotOptions: {
            column: {
                """ + stacking  +""" 
            }
        },

        series: ["""
        
    data = ''
    i=0        
    nr=0
    for d1 in data1:
        j=0
        if not len(data1) == i:
            data = data + """{ name: '""" + str(dataName1[i]) + """', data: ["""
        
        for d11 in d1:
            data = data + """   
            {
                name: '""" + str(dataName0[nr]) + """',
                y: """ + str(d11) + """,
                drilldown: {
                    series: """ + str(dataId[nr])  + """}}            
        """
            if not len(d1) == j+1:
                data = data + ","
            j+=1
            nr+=1
        if not len(data1) == i+1:
            data = data + "]},"
        i+=1
    data = data + "]},"
    script = script + data
    script = script +  """
    ],
    drilldown: {
        series: [
        """
    script = script + datadata
    script = script + """ 

        ]
    }
})
});</script> 

 """
    return container + script


def useThemePlotNew():
    return """
    Highcharts.createElement('link', {
    href: 'http://fonts.googleapis.com/css?family=Dosis:400,600',
    rel: 'stylesheet',
    type: 'text/css'
 }, null, document.getElementsByTagName('head')[0]);

 Highcharts.theme = {
    colors: ["#7cb5ec", "#f7a35c", "#90ee7e", "#7798BF", "#aaeeee", "#ff0066", "#eeaaee",
       "#55BF3B", "#DF5353", "#7798BF", "#aaeeee"],
    chart: {
       backgroundColor: null,
       style: {
          fontFamily: "Dosis, sans-serif"
       }
    },
    title: {
       style: {
          fontSize: '16px',
          fontWeight: 'bold',
          textTransform: 'uppercase'
       }
    },
    tooltip: {
       borderWidth: 0,
       backgroundColor: 'rgba(219,219,216,0.8)',
       shadow: false
    },
    legend: {
       itemStyle: {
          fontWeight: 'bold',
          fontSize: '13px'
       }
    },
    xAxis: {
       gridLineWidth: 1,
       labels: {
          style: {
             fontSize: '12px'
          }
       }
    },
    yAxis: {
       minorTickInterval: 'auto',
       title: {
          style: {
             textTransform: 'uppercase'
          }
       },
       labels: {
          style: {
             fontSize: '12px'
          }
       }
    },
    plotOptions: {
       candlestick: {
          lineColor: '#404048'
       }
    },


    // General
    background2: '#F0F0EA'
    
 };

    Highcharts.setOptions(Highcharts.theme);
    
    """

def drawMultiYAxis(dataY1, dataY2, tickInterval=1, categories= '', titleText='', subtitleText='', plotNumber=1, seriesType1='', seriesName1='', seriesType2='', seriesName2='', minWidth=300, height=600, title1='', title2=''):
    
    dataY1Depth = depth(dataY1)
    dataY2Depth = depth(dataY2)
    
    js = """<div id='container""" + str(plotNumber) + """' style='min-width: """ + str(minWidth) + """px; height: """ + str(height) + """px; margin: 0 auto'></div>"""
    
            
    js += """        
    <script>
    $(function () {"""
    
    
    js+= str(useThemePlotNew())
    
    js+= """
    $('#container""" + str(plotNumber) + """').highcharts({
        chart: {
            zoomType: 'x'
        },
        title: {  text: '""" + titleText + """' },
        subtitle: { text: '""" + subtitleText + """' },
        xAxis: [{
            tickInterval: """ + str(tickInterval) + """,
            labels: {rotation: 90},
            categories: """ + str(categories) + """,
            crosshair: true
        }],
        yAxis: [{ 
            labels: {
                format: '{value}',
            },
            title: {
                text: '""" + str(title2) +  """'
            },
            opposite: true,
            reversed: true,
            height: '55%',

        }, { 
            gridLineWidth: 0,
            title: {
                text: '""" + str(title1) +  """'
            },
            top: '50%',
            height: '55%',
            
        }
        ],
        tooltip: {
            shared: true
        },
        series: [
        """
        
    if dataY1Depth == 2:    
        i=0
        for d in dataY1:
            js+="""
            {
            name: '""" + str(seriesName1[i]) + """',
            type: '""" + str(seriesType1[i]) + """',
            yAxis: 1,
            data: """ + str(d) + """
            }
            """
            if i < len(dataY1)-1:
                js+= ','
            i+=1
    
    if dataY2Depth == 2:    
        i=0
        if i == 0:
            js+= ','
        for d in dataY2:
            js+="""
            {
            name: '""" + str(seriesName2[i]) + """',
            type: '""" + str(seriesType2[i]) + """',
            dashStyle: 'shortdot',
            data: """ + str(d) + """
            }
            """
            if i < len(dataY2)-1:
                js+= ','
            i+=1
        
    js+= """
        ]
    });
});
        </script>
        """
    
    return js
