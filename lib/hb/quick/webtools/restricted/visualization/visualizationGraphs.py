import json

'''
create object with height (default 400px + 12px for each line in legend)
use method:

#seriesType = line, area, bar, column

#data for one series --- data1 = [1,2,3]
#data for many series on one plot --- data2 =[[1,2,3], [4, 5, 6]]
#data for many series on many plot --- dat3 =[[[1,2,3], [4, 5, 6]], [[2,3,4]]]

drawLineChart(data1 OR data2)
drawLineCharts(data3)

drawAreaChart(data1 OR data2)
drawAreaCharts(data3)

drawPieChart(data1)

drawBarChart(data1 OR data2)
drawBarCharts(data3)

drawColumnChart(data1 OR data2)
drawColumnCharts(data3)

drawMultiTypeSeriesChart(data1 OR data2, seriesType=['line', 'column', ...])
drawMultiTypeSeriesCharts(data3, seriesType=['line', 'column', ...])
'''


'''
Plan TODO:
- single chart
- multi chart
- interaction among charts
- more available options for charts
- heatmap
'''

from proto.hyperbrowser.HtmlCore import HtmlCore
from random import randint

class colorList:
    def __init__(self):
        pass

    def rgb_to_hex(self):
        return '#%02x%02x%02x' % (randint(0,255),randint(0,255),randint(0,255))

    def fullColorList(self, lenColorList=0):

        colors=['#19198c',
                '#ED561B',
                '#DDDF00',
                '#24CBE5',
                '#64E572',
                '#FF9655',
                '#FFF263',
                '#6AF9C4',
                '#7cb5ec',
                '#FCE9A1',
                '#E7DEC5',
                '#B58AA5',
                '#50B432',
                '#fdd07c',
                '#C3C3E5',
                '#C8CF78',
                '#4a6c8d',
                '#ffe063',
                '#C4B387',
                '#84596B',
                '#ffb037',
                '#443266',
                '#a6ab5b',
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
                '#c2dde5',
                '#008B8B',
                '#B8860B',
                '#A9A9A9',
                '#006400',
                '#BDB76B',
                '#8B008B',
                '#556B2F',
                '#FF8C00',
                '#9932CC',
                '#8B0000',
                '#E9967A',
                '#8FBC8F',
                '#483D8B',
                '#2F4F4F',
                '#00CED1',
                '#9400D3',
                '#FF1493',
                '#00BFFF',
                '#696969',
                '#1E90FF',
                '#B22222',
                '#FFFAF0',
                '#228B22',
                '#FF00FF',
                '#DCDCDC',
                '#F8F8FF',
                '#FFD700',
                '#DAA520',
                '#808080',
                '#008000',
                '#ADFF2F',
                '#F0FFF0',
                '#FF69B4',
                '#CD5C5C',
                '#4B0082',
                '#FFFFF0',
                '#F0E68C',
                '#E6E6FA',
                '#FFF0F5',
                '#7CFC00',
                '#FFFACD',
                '#ADD8E6',
                '#F08080',
                '#E0FFFF',
                '#FAFAD2',
                '#D3D3D3',
                '#90EE90',
                '#FFB6C1',
                '#FFA07A',
                '#20B2AA',
                '#87CEFA',
                '#778899',
                '#B0C4DE',
                '#FFFFE0',
                '#00FF00',
                '#32CD32',
                '#FAF0E6',
                '#FF00FF',
                '#800000',
                '#66CDAA',
                '#0000CD',
                '#BA55D3',
                '#9370DB',
                '#3CB371',
                '#7B68EE',
                '#00FA9A',
                '#48D1CC',
                '#C71585',
                '#191970',
                '#F5FFFA',
                '#FFE4E1',
                '#FFE4B5',
                '#FFDEAD',
                '#000080',
                '#FDF5E6',
                '#808000',
                '#6B8E23',
                '#FFA500',
                '#FF4500',
                '#DA70D6',
                '#EEE8AA',
                '#98FB98',
                '#AFEEEE',
                '#DB7093',
                '#FFEFD5',
                '#FFDAB9',
                '#CD853F',
                '#FFC0CB',
                '#DDA0DD',
                '#B0E0E6',
                '#800080',
                '#663399',
                '#FF0000',
                '#BC8F8F',
                '#4169E1',
                '#8B4513',
                '#FA8072',
                '#F4A460',
                '#2E8B57',
                '#FFF5EE',
                '#A0522D',
                '#C0C0C0',
                '#87CEEB',
                '#6A5ACD',
                '#708090',
                '#FFFAFA',
                '#00FF7F',
                '#4682B4',
                "#00CED1",
                "#00FA9A",
                "#00FF00",
                "#00FF7F",
                "#00FFFF",
                "#00FFFF",
                "#191970",
                "#1E90FF",
                "#20B2AA",
                "#228B22",
                "#2E8B57",
                "#2F4F4F",
                "#32CD32",
                "#3CB371",
                "#40E0D0",
                "#4169E1",
                "#4682B4",
                "#483D8B",
                "#48D1CC",
                "#4B0082",
                "#556B2F",
                "#5F9EA0",
                "#6495ED",
                "#663399",
                "#66CDAA",
                "#808000",
                "#808080",
                "#87CEEB",
                "#87CEFA",
                "#8A2BE2",
                "#8B0000",
                "#8B008B",
                "#8B4513",
                "#8FBC8F",
                "#90EE90",
                "#9370DB",
                "#9400D3",
                "#98FB98",
                "#9932CC",
                "#9ACD32",
                "#A0522D",
                "#A52A2A",
                "#A9A9A9",
                "#ADD8E6",
                "#ADFF2F",
                "#AFEEEE",
                "#B0C4DE",
                "#B0E0E6",
                "#B22222"
                ]

        if len(colors) < lenColorList:
            for el in range(0, lenColorList - len(colors)):
                colors.append(self.rgb_to_hex())

        return colors

class visualizationGraphs(object):
    count =0
    
    def __init__(self, height=600):
        
        self.__class__.count +=1
        self._height=height
        self._interactionNumberStart = 0
        self._interactionNumberEnd = 0
        
        self._colorList =[
                          '#1ebff0',   
                '#050708', 
                '#e62725',
                '#cbcacb', 
                '#a1cf64',  
                '#edc8c5',
                '#C8CF78',
                
                '#4a6c8d',
                '#ffe063', 
                '#C4B387', 
                '#84596B',  
                '#ffb037',  
                '#443266',  
                '#a6ab5b',
                  
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
                '#c2dde5',
                '#008B8B',
                '#B8860B',
                '#A9A9A9',
                '#006400',
                '#BDB76B',
                '#8B008B',
                '#556B2F',
                '#FF8C00',
                '#9932CC',
                '#8B0000',
                '#E9967A',
                '#8FBC8F',
                '#483D8B',
                '#2F4F4F',
                '#00CED1',
                '#9400D3',
                '#FF1493',
                '#00BFFF',
                '#696969',
                '#1E90FF',
                '#B22222',
                '#FFFAF0',
                '#228B22',
                '#FF00FF',
                '#DCDCDC',
                '#F8F8FF',
                '#FFD700',
                '#DAA520',
                '#808080',
                '#008000',
                '#ADFF2F',
                '#F0FFF0',
                '#FF69B4',
                '#CD5C5C',
                '#4B0082',
                '#FFFFF0',
                '#F0E68C',
                '#E6E6FA',
                '#FFF0F5',
                '#7CFC00',
                '#FFFACD',
                '#ADD8E6',
                '#F08080',
                '#E0FFFF',
                '#FAFAD2',
                '#D3D3D3',
                '#90EE90',
                '#FFB6C1',
                '#FFA07A',
                '#20B2AA',
                '#87CEFA',
                '#778899',
                '#B0C4DE',
                '#FFFFE0',
                '#00FF00',
                '#32CD32',
                '#FAF0E6',
                '#FF00FF',
                '#800000',
                '#66CDAA',
                '#0000CD',
                '#BA55D3',
                '#9370DB',
                '#3CB371',
                '#7B68EE',
                '#00FA9A',
                '#48D1CC',
                '#C71585',
                '#191970',
                '#F5FFFA',
                '#FFE4E1',
                '#FFE4B5',
                '#FFDEAD',
                '#000080',
                '#FDF5E6',
                '#808000',
                '#6B8E23',
                '#FFA500',
                '#FF4500',
                '#DA70D6',
                '#EEE8AA',
                '#98FB98',
                '#AFEEEE',
                '#DB7093',
                '#FFEFD5',
                '#FFDAB9',
                '#CD853F',
                '#FFC0CB',
                '#DDA0DD',
                '#B0E0E6',
                '#800080',
                '#663399',
                '#FF0000',
                '#BC8F8F',
                '#4169E1',
                '#8B4513',
                '#FA8072',
                '#F4A460',
                '#2E8B57',
                '#FFF5EE',
                '#A0522D',
                '#C0C0C0',
                '#87CEEB',
                '#6A5ACD',
                '#708090',
                '#FFFAFA',
                '#00FF7F',
                '#4682B4',
                "#00CED1",
                "#00FA9A",
                "#00FF00",
                "#00FF7F",
                "#00FFFF",
                "#00FFFF",
                "#191970",
                "#1E90FF",
                "#20B2AA",
                "#228B22",
                "#2E8B57",
                "#2F4F4F",
                "#32CD32",
                "#3CB371",
                "#40E0D0",
                "#4169E1",
                "#4682B4",
                "#483D8B",
                "#48D1CC",
                "#4B0082",
                "#556B2F",
                "#5F9EA0",
                "#6495ED",
                "#663399",
                "#66CDAA",
                "#808000",
                "#808080",
                "#87CEEB",
                "#87CEFA",
                "#8A2BE2",
                "#8B0000",
                "#8B008B",
                "#8B4513",
                "#8FBC8F",
                "#90EE90",
                "#9370DB",
                "#9400D3",
                "#98FB98",
                "#9932CC",
                "#9ACD32",
                "#A0522D",
                "#A52A2A",
                "#A9A9A9",
                "#ADD8E6",
                "#ADFF2F",
                "#AFEEEE",
                "#B0C4DE",
                "#B0E0E6",
                "#B22222"
                ]
        
        
    
    def _addLib(self):
        return """ 
                <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
                <script src="https://code.highcharts.com/highcharts.js"></script>
                <script src="https://code.highcharts.com/modules/data.js"></script>
                <script src="https://code.highcharts.com/modules/heatmap.js"></script>
                <script src="https://code.highcharts.com/modules/exporting.js"></script>
                <script src="https://raw.github.com/briancray/tooltipsy/master/tooltipsy.min.js"></script>
                <script src="https://code.highcharts.com/highcharts-more.js"></script>
                """
                
    def _addToLargeHeatmap(self):
        return """
        /**
     * This plugin extends Highcharts in two ways:
     * - Use HTML5 canvas instead of SVG for rendering of the heatmap squares. Canvas
     *   outperforms SVG when it comes to thousands of single shapes.
     * - Add a K-D-tree to find the nearest point on mouse move. Since we no longer have SVG shapes
     *   to capture mouseovers, we need another way of detecting hover points for the tooltip.
     */
    (function (H) {
        var Series = H.Series,
            each = H.each;

        /**
         * Create a hidden canvas to draw the graph on. The contents is later copied over
         * to an SVG image element.
         */
        Series.prototype.getContext = function () {
            if (!this.canvas) {
                this.canvas = document.createElement('canvas');
                this.canvas.setAttribute('width', this.chart.chartWidth);
                this.canvas.setAttribute('height', this.chart.chartHeight);
                this.image = this.chart.renderer.image('', 0, 0, this.chart.chartWidth, this.chart.chartHeight).add(this.group);
                this.ctx = this.canvas.getContext('2d');
            }
            return this.ctx;
        };

        /**
         * Draw the canvas image inside an SVG image
         */
        Series.prototype.canvasToSVG = function () {
            this.image.attr({ href: this.canvas.toDataURL('image/png') });
        };

        /**
         * Wrap the drawPoints method to draw the points in canvas instead of the slower SVG,
         * that requires one shape each point.
         */
        H.wrap(H.seriesTypes.heatmap.prototype, 'drawPoints', function () {

            var ctx = this.getContext();

            if (ctx) {

                // draw the columns
                each(this.points, function (point) {
                    var plotY = point.plotY,
                        shapeArgs;

                    if (plotY !== undefined && !isNaN(plotY) && point.y !== null) {
                        shapeArgs = point.shapeArgs;

                        ctx.fillStyle = point.pointAttr[''].fill;
                        ctx.fillRect(shapeArgs.x, shapeArgs.y, shapeArgs.width, shapeArgs.height);
                    }
                });

                this.canvasToSVG();

            } else {
                this.chart.showLoading('Your browser doesnt support HTML5 canvas, <br>please use a modern browser');

                // Uncomment this to provide low-level (slow) support in oldIE. It will cause script errors on
                // charts with more than a few thousand points.
                // arguments[0].call(this);
            }
        });
        H.seriesTypes.heatmap.prototype.directTouch = false; // Use k-d-tree
    }(Highcharts));


    var start;
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
        
        .buttonArea{
            margin-top:10px;
        }
        
        input[type=button] {
            padding:10px 10px;
            cursor:pointer;
            background-color:#FFE899;
        }   
        
        input[type=button]:hover {
            background-color:#fff;
        }
           
        </style>
        
        <script>
    
    function sortTwoLists(A, B, namesFromTable, type)
    {
    
        console.log('sort time ---- A', A);
        console.log('B', B);
        console.log('namesFromTable', namesFromTable);
        console.log(type);
        results=[]
        indexList=[]


        if (type == 'desc')
        {
            for (var i = 0; i < namesFromTable.length; i++) 
            {
                for (var j = 0; j < B.length; j++) 
                {
                    if(namesFromTable[i] == B[j])
                    {
                        indexList[i]=j;
                        results[i]=A[j];
                    }
                } 
            } 
        }  
        if (type == 'asc')
        {
            for (var i = 0; i < namesFromTable.length; i++) 
            {
                for (var j = 0; j < B.length; j++) 
                {
                    if(namesFromTable[i] == B[j])
                    {
                        indexList[i]=j;
                        results[i]=A[j];
                    }
                } 
            } 
        }

        console.log('after sort', 'results', results, 'indexList', indexList);
       
        
        var C=[]
        C[0]=results; 
        C[1]=indexList;
        return C
    }
    
    function sortListAccordingToOtherList(A, D)
    {
        var C=[];
        for (var i = 0; i < A.length; i++) 
        {
            C[i] = D[A[i]];
        }
        return C
    }
    
    </script>
        
        """
    def _themePlot(self):
        return """
        Highcharts.createElement('link', {
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
        
    def _depth(self,l):
        if isinstance(l, list):
            return 1 + max(self._depth(item) for item in l)
        else:
            return 0
     
     
    def countFromStart(self):
        self.__class__.count=1
        
    
    def _buildContainer(self, addOptions, addTable, titleText):
        if addOptions is None:
            addOptions='width: 100%; margin: 0 auto'
        
        
        table=''
        if addTable == True:
            table += str('''<div id="table_''' + ".".join(titleText.replace("'", "").replace('"', "").split()) + '''" style="display:none">''')
        
        if addTable == 'option2':
            table += str('''<div id="table_''' + ".".join(titleText.replace("'", "").replace('"', "").split()) + '''" style="display:block">''')
        
        table  += str('''<div id="container''' + str(self.__class__.count) + '''" style= "''' + str(addOptions) + '''"></div>''')
        if addTable == True:
            table += '</div>'
            
        return table
    
    
    
    
    def _addGuideline(self, htmlCore):
        htmlCore.line(""" 
        
        <a href="#" class="clickme">Show instructions for plots</a>
        
        <script>
        
        $('#plotDivd').hide();

        $('.clickme').each(function() {
            $(this).show(0).on('click', function(e) {
                e.preventDefault();
                
                $(this).next('#plotDivd').slideToggle('fast');
            });
        });
        </script>
        
        """)
        htmlCore.divBegin('plotDivd', style="min-width:400px;border:1px solid #000033;padding:10px;color:#181818")
        htmlCore.divBegin('guideLine', style="font-weght:bold;text-transform:uppercase;margin-bottom:5px;")
        htmlCore.line('Guidelines for viewing the plots:')
        htmlCore.divEnd()
        
        htmlCore.divBegin('option1d', style="font-weght:bold;margin-bottom:5px;margin-top:5px;")
        htmlCore.line('Sorting:')
        htmlCore.divEnd()
        htmlCore.line('- To sort a plot by a column, click on the column header in the table.')     
        
        htmlCore.divBegin('option1d', style="font-weght:bold;margin-bottom:5px;margin-top:5px;")
        htmlCore.line('Zooming:')
        htmlCore.divEnd()
        htmlCore.line('- To zoom a plot representing one dataset, e.g. one line, click on the plot and drag your mouse to the left/right side.')
        htmlCore.line('- To zoom when viewing multiple plots that represent related datasets, in the same output page, zooming one plot will automatically zoom all plots.')
        htmlCore.line('- To reset the zooming press the button: \"Reset zoom\"')
        
        htmlCore.divBegin('option1d', style="font-weght:bold;margin-bottom:5px;margin-top:5px;")
        htmlCore.line('Show/Hide:')
        htmlCore.divEnd()
        htmlCore.line('- To show/hide a specific dataset in the plot, click the colored checkbox next to the name of that dataset located in the legend below the plot.')
        
        htmlCore.divBegin('option1d', style="font-weght:bold;margin-bottom:5px;margin-top:5px;")
        htmlCore.line('Print and download:')
        htmlCore.divEnd()
        htmlCore.line('- To print or download, open the context menu, located in the top right corner of the plot, and choose from there.')
        
        
        htmlCore.divBegin('option1d', style="font-weght:bold;margin-bottom:5px;margin-top:5px;")
        htmlCore.line('Heatmap:')
        htmlCore.divEnd()
        htmlCore.line('- To select a specific region and download it locally as a group of .bed files, click the region of interest (or multiple regions by using ctrl/cmd) and press the \"Get selected regions\" button. The .bed file/files will appear above the heatmap where they can be downloaded.')
        
        htmlCore.divEnd()
        
        return htmlCore
    
    def _addGuidelineV1(self, tableName):
        
        strText = """ 
        
        <style>
        .infomessage{
        cursor:pointer;
        }
        
        </style>
        
        <br \><div class="infomessage"><div class='""" + str(tableName) + """clickme'>Show instruction for plots</div></div>
        
        
        """
        
        strText += """
        <div id ='""" + str(tableName) + """plot'  style='display:none;min-width:400px;margin-top:10px;border:1px solid #000033;padding:10px;color:#181818' >
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
            
            - To zoom a plot representing one dataset, e.g. one line, click on the plot and drag your mouse to the left/right side.<br \>
            - To zoom when viewing multiple plots that represent related datasets, in the same output page, zooming one plot will automatically zoom all plots.<br \>
            - To reset the zooming press the button: \"Reset zoom\"
        
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
            
            - To select a specific region and download it locally as a group of .bed files, click the region of interest (or multiple regions by using ctrl/cmd) and press the \"Get selected regions\" button. The .bed file/files will appear above the heatmap where they can be downloaded.
        
       
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
    
    def addTable(self, name, tableName, option, indexSpecial):
        
        table = """
        <style>
        .tabRes {
            display: table;
            width: 100%; 
            background: #fff;
            margin: 0;
            box-sizing: border-box;
        }
        .tabRes th {
            background-color: #4A9900;
            font-weight: bold;
            color: #FFF;
            white-space: nowrap;
            
        }
        .tabRes th, .tabRes td {
            padding: 0.50em 1.0em;
            text-align: left;
            border:  1px solid #010101;
        }
        select{
        -webkit-appearance: none;
        -moz-appearance: none;
        appearance: none;
        padding: 0.2em 1.5em;
        }
        </style>
        """
        
        
#         table += """
#         <input type="hidden" name="checkedVal" id="checkedVal" value="noChecked">
#         <table class="tabRes">
#         <tr>
#         <th>Option</th>
#         <th>Name</th>
#         </tr>
#         """
#         
#         inx=0
#         for n in name:
#             nVal = 'table_' + str(".".join(n.replace("'", "").replace('"', "").split()))
#             table += '<tr><td>' + '<input type="checkbox"  checked="checked" name="tabResList" id ="' + str(inx)  + '" value="' + nVal  + '"' + ' onclick="showMe(' +"'" + nVal + "'" + ')"'   + '\>' + '</td>' 
#             table += '<td>' +  str(n) + '</td></tr>'
#             inx+=1
#             
#             
#         table += '</table>'

        if option==1:
            noChecked='noChecked'
        else:
            noChecked='checked'

        table += """
        <input type="hidden" name="checkedVal" id="checkedVal" value=""" + str(noChecked) + """>
        
        <script>
        """
        
        
        
        if type(name) is str:
            inx=0
            n=name
            nVal = 'table_' + str(".".join(n.replace("'", "").replace('"', "").split()))
            strJs = "'" + '<input type="checkbox"  checked="checked" name="tabResList" id ="' + str(inx)  + '" value="' + nVal  + '"' + ' onclick=showMe("' + nVal + '")'   + '\>' + "';"
            table += 'document.getElementById("' + str(tableName) + '").getElementsByTagName("th")[' + str(inx+1) + '].innerHTML += ' + strJs  
            inx+=1
        else:
            inx=indexSpecial
            for n in name:
                nVal = 'table_' + str(".".join(n.replace("'", "").replace('"', "").split()))
                
                strJs = "'" + '<input type="checkbox"  checked="checked" name="tabResList" id ="' + str(inx)  + '" value="' + nVal  + '"' + ' onclick=showMe("' + nVal + '")'   + '\>' + "';"
                table += 'document.getElementById("' + str(tableName) + '").getElementsByTagName("th")[' + str(inx+1) + '].innerHTML += ' + strJs  
                inx+=1
            
            
        table += "</script>"
        
        
        
        table += """
        
        <script>
        
        
        if(document.getElementById("checkedVal").value == 'noChecked')
        {
            document.getElementById("checkedVal").value='checked'
            var chboxs = document.getElementsByName("tabResList");
            for(var i=0;i<chboxs.length;i++) 
            {
                chboxs[i].checked=false;
            }
        }
       
        
        function showMe(box) 
        {
        
            var chboxs = document.getElementsByName("tabResList");
            
            for(var i=0;i<chboxs.length;i++) 
            { 
                
                if(chboxs[i].checked)
                {
                    newBox=chboxs[i].value;
                    document.getElementById(newBox).style.display = "block";
                }
                else
                {
                    newBox=chboxs[i].value;
                    document.getElementById(newBox).style.display = "none";
                }
            }
        }
        
        
        
        </script>
        """
        
        
        return str(table)
        
            
    
    def _parseData(self, dataY, type, seriesType, seriesName, multiYAxis, visible, yAxisMulti, multiXAxis, xAxisMulti, markerRadius):
        
        
        dataYdepth = self._depth(dataY)        
        #default: there are the same type of charts on one char
        if seriesType is None:
            if dataYdepth == 1:
                seriesType = [type]
            else:
                seriesType = [type for dY in dataY]
        
        legendSizeExtra=0
        legendSize=''
        if seriesName is None:
            seriesName=''
        else:
            if isinstance(seriesName, basestring):
                legendSize =  len(max(seriesName, key = len)) + 10
                legendSizeExtra = len(seriesName)
                legendSizeExtra = legendSizeExtra / ( int(1000 / (legendSize*6)) )*15
            else:
                legendSize = len(max(seriesName, key = len)) + 10
                legendSizeExtra = len(seriesName)
                legendSizeExtra = legendSizeExtra / ( int(1000 / (legendSize*6)) )*15
            
        
        data=''        
        
        if visible == False:
            visible = ' visible: false, '
        else:
            visible=''
        
        
        marker=''
        if markerRadius!=None:
            marker += 'marker: { '
            if markerRadius!=None:
                marker += 'radius: ' + str(markerRadius) + ', '
                marker += "symbol: 'circle'" + ', '
            marker += '},'


        if isinstance(dataY[0], list) == True:
            
            if multiYAxis == True:

                halfDataColor = len(dataY) / 2
                colorsList = colorList().fullColorList(halfDataColor)



                i=0
                j=0
                for d in dataY:
                    
                    try:
                        d = json.dumps(d).replace('"', "")
                    except Exception, e:
                        d=d

                    if i == halfDataColor:
                        j=0
                    
                    if i==0:
                        if seriesType[0] != 'scatter':
                            marker1 = ''
                        else:
                            marker1 = marker
                        data = '{0}{1}{2}{3}{4}{5}'.format(""" color: '""" + colorsList[j] + """', """ + """ type: '""" + seriesType[0] + """', """ + """ """ ,  visible + marker1 +"""  name: """, "'" if seriesName=='' else "'" + seriesName[i] ,"""', data: """, d, """ } """ )
                    else:
                        yAxisMultiVal=str(i)
                        if yAxisMultiVal is not None:
                            yAxisMultiVal = yAxisMulti[i]
                        if seriesType[i] != 'scatter':
                            marker1 = ''
                        else:
                            marker1=marker
                        data = data + '{0}{1}{2}{3}{4}{5}{6}'.format( """ , { """ + """ color: '""" + colorsList[j] + """', """ +  """ type: '"""  + seriesType[i] + """', """ , """yAxis: """ + str(yAxisMultiVal) + """ ,""", visible + marker1 + """name: """ , "'" if seriesName=='' else "'" + seriesName[i] , """', data: """, d, """ } """ )

                    i+=1
                    j+=1

            elif multiXAxis == True:
                i = 0
                for d in dataY:

                    try:
                        d = json.dumps(d).replace('"', "")
                    except Exception, e:
                        d = d

                    if i == 0:
                        data = '{0}{1}{2}{3}{4}{5}{6}'.format(""" type: '""" + seriesType[0] + """', """ + """ ""","""xAxis: """ + str(0) + """ ,""",
                                                           visible + marker + """  name: """,
                                                           "'" if seriesName == '' else "'" + seriesName[i],
                                                           """', data: """, d, """ }  """)


                    else:
                        xAxisMultiVal = str(i)
                        if xAxisMultiVal is not None:
                            xAxisMultiVal = xAxisMulti[i]
                        data = data + '{0}{1}{2}{3}{4}{5}{6}'.format(""" , { type: '""" + seriesType[i] + """', """,
                                                                     """xAxis: """ + str(xAxisMultiVal) + """ ,""",
                                                                     visible + marker + """name: """,
                                                                     "'" if seriesName == '' else "'" + seriesName[i],
                                                                     """', data: """, d, """ } """)
                    i += 1
            else:
                
                i=0
                for d in dataY:
                    try:
                        d = json.dumps(d).replace('"', "")
                    except Exception, e:
                        d=d
                    
                    
                    if i==0:
                        data = '{0}{1}{2}{3}{4}{5}'.format(""" type: '""" + seriesType[0] + """', """ ,  visible +  marker +"""  name: """, "'" if seriesName=='' else "'" + seriesName[i] ,"""', data: """, d, """ } """ )
                    else:
                        data = data + '{0}{1}{2}{3}{4}{5}'.format(""" , { type: '"""  + seriesType[i] + """', """ , visible +  marker +"""name: """ , "'" if seriesName=='' else "'" + seriesName[i] , """', data: """, d, """ } """ )
                    i+=1
        else:
            
            try:
                dataY = json.dumps(dataY).replace('"', "")
            except Exception, e:
                dataY=dataY
                
            data = '{0}{1}{2}{3}{4}{5}'.format(""" type: '""" + seriesType[0] + """', """  , visible +  marker +"""  name: """, "'" if seriesName=='' else "'" + seriesName[0] , """', data: """, dataY, """ } """ )



        return data, legendSize, legendSizeExtra
    def _parseData2(self, dataY, type, seriesType, seriesName):   
        
        dataYdepth = self._depth(dataY)        
        #default: there are the same type of charts on one char
        if seriesType is None:
            if dataYdepth == 1:
                seriesType = [type]
            else:
                seriesType = [type for dY in dataY]
        
        
        legendSizeExtra=0
        legendSize=''
        if seriesName is None:
            seriesName=''
        else:
            if isinstance(seriesName, basestring):
                legendSize =  len(max(str(seriesName), key = len))+10
                legendSizeExtra = len(str(seriesName))
                legendSizeExtra = legendSizeExtra / ( int(1000 / (legendSize*6)) )*12
            else:
                legendSize = len(max(str(seriesName), key = len)) + 10
                legendSizeExtra = len(str(seriesName))
                legendSizeExtra = 15
            

        

        data='data: ['        
        if isinstance(dataY[0], list) == False:
            for eldY in range(0, len(dataY)):
                
                sN=''
                if seriesName=='':
                    sN="''"
                else:
                    sN = "'" + str(seriesName[eldY]) + "'"
                
                d=dataY[eldY]
                try:
                    d = json.dumps(dataY[eldY]).replace('"', "")
                except Exception, e:
                    d = float(dataY[eldY])
                    
                
                data += "{ name: " + str(sN) + ", y:" + str(d) +  "}"
                
                if len(dataY)-1 != eldY:
                    data += ", "
                else:
                    data +="] }"
        
        return data, legendSize, legendSizeExtra
    
    #[[10,20,30],[30,40,50]]
    def _parseData3(self, dataY):   
        
        dataYdepth = self._depth(dataY)        
        #default: there are the same type of charts on one char
            

             
        if isinstance(dataY[0], list) == True:
            
            dataList=[]
            row=0
            for eldY1 in range(0, len(dataY)):
                column=0
                for eldY2 in range(0, len(dataY[eldY1])):
                    dataList.append([column, row, dataY[eldY1][eldY2]])
                    column+=1
                row+=1
                    
        data='data: ' + str(dataList) + ', '
        
        return data
    
    def _parseData4(self, dataY):   
        
        dataYdepth = self._depth(dataY)        
        #default: there are the same type of charts on one char
         
        if isinstance(dataY[0], list) == True:
            
            dataList="<pre id='csv' style='display:none'>data,x,y"
            row=0
            for eldY1 in range(0, len(dataY)):
                column=0
                for eldY2 in range(0, len(dataY[eldY1])):
                    dataList+= str(column) + ',' + str(row) + ',' + str(dataY[eldY1][eldY2]) + '\n'
                    column+=1
                row+=1
        
        dataList += '\n</pre>'
        
        return dataList
    

    
    def _useAttribute1(self, att, attName):
        if att is None:
            att= attName + ": '',"
        else:
            if type(att)==int or type(att)==float:
                att = attName + ": " + str(att) + ", "
            else:
                att = attName + ": '" + str(att) + "', "
            
        return att
    
    
    def _useAttribute2(self, att, attName):
        if att is None:
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
        if att is None:
            att= ''
        else:
            if type(att)==int or type(att)==float:
                att = attName + ": " + str(att) + ", "
            else:
                att = attName + ": '" + str(att) + "', "
            
        return att
    
    def _useAttribute5(self, att, attName):
        
        if att is None:
            att =''
        else:
            if type(att)==int or type(att)==float:
                att = attName + ": " + str(att) + ", "
            else:
                att = attName + ": '" + str(att) + "', "
        return att
    
        
    def _useAttribute6(self, att, attName):
        if att is None:
            att= attName + ": '',"
        else:
            att = attName + ": " + str(att) + ", "
            
            
        return att
    
        
    def _useXAxis(self, xAxisTitle, tickInterval, tickMinValue, categories, typeAxisXScale, \
                  xAxisRotation, labelX, interaction, type, histogram, plotLines, plotLinesName, \
                   plotBands, plotBandsColor, multiXAxis, xAxisMulti):
        
        #print self.__class__.count
        #print interaction
        #print self._interactionNumberStart
        #print self._interactionNumberEnd
        
        if type!='bubble':
            minX = 'min:0,'
        else:
            minX=''
       
        
        
        if plotLines!=None:
            plLin=''
            if isinstance(plotLines, list):
                plLin += """plotLines: ["""
                id=0
                for el in plotLines:
                    
                    plName=''
                    if plotLinesName!=None:
                        plName = plotLinesName[id]
                    
                    width=1
                    if type == 'column':
                        el = el-0.5
                        width = 2
                        
                    if plotBandsColor == None:
                        plotBandsColorV = '#a8a8a8'
                    elif plotBandsColor == True:
                        plotBandsColorV = self._colorList[id]
                        
                    id+=1
                    plLin += """{
                    id: '"""+str(id)+ """',
                    color: '""" + str(plotBandsColorV) + """', // Color value
                    dashStyle: 'solid', // Style of the plot line. Default to solid
                    value: """ + str(el) + """, // Value of where the line will appear
                    width: """ + str(width) + """, 
                    label: { text: '""" + str(plName) + """', style: { color:'""" + str(plotBandsColorV) + """' },
                    }    
                    },
                    """
                plLin+="],"
                plotLines=plLin
            else:
                
                plName=''
                if plotLinesName!=None:
                    plName = plotLinesName
                
                width=1
                if type == 'column':
                    el = el-0.5
                    width = 2
                    
                plLin += """plotLines: [{
                color: '#a8a8a8', // Color value
                dashStyle: 'solid', // Style of the plot line. Default to solid
                value: """ + str(plotLines) + """, // Value of where the line will appear
                width: """ + str(width) + """, 
                    label: { text: '""" + str(plName) + """', style: { color:'#a8a8a8' },
                    }        
                }],"""
                plotLines=plLin
        else:
            plotLines=''
            
            
#         if plotBands!=None:
#             
#             plLin=''
#             if isinstance(plotBands, list):
#                 plLin += """plotBands: ["""
#                 id=0
#                 for el in plotBands:
#                     
#                     plName=''
#                     if plotLinesName!=None:
#                         plName = plotLinesName[id]
#                     
#                     
#                     if type == 'column':
#                         for eNum in range(0, len(el)):
#                             el[eNum] = el[eNum]-0.5
#                     
#                         
#                     if plotBandsColor == None:
#                         plotBandsColorV = '#a8a8a8'
#                     elif plotBandsColor == True:
#                         plotBandsColorV = self._colorList[id]
#                         
#                     id+=1
#                     plLin += """{
#                     id: '"""+str(id)+ """',
#                     color: '""" + str(plotBandsColorV) + """', // Color value
#                     from: """ + str(el[0]) + """, // Value of where the line will appear
#                     to: """ + str(el[1]) + """, // Value of where the line will appear
#                      
#                     label: { text: '""" + str(plName) + """', style: { color:'#000000' },
#                     }    
#                     },
#                     """
#                 plLin+="],"
#                 plotLines=plLin
#             else:
#                 plName=''
#                 if plotLinesName!=None:
#                     plName = plotLinesName
#                 
#                 
#                 if type == 'column':
#                     plotBands[0] = plotBands[0]-0.5
#                     plotBands[1] = plotBands[1]-0.5
#                 
#                     
#                 plLin += """plotBands: [{
#                 color: '#a8a8a8', // Color value
#                 from: """ + str(plotBands[0]) + """, // Value of where the line will appear
#                 to: """ + str(plotBands[1]) + """, // Value of where the line will appear
#                  
#                     label: { text: '""" + str(plName) + """', style: { color: '#000000' },
#                     }        
#                 }],"""
#                 plotLines=plLin
#         else:
#             plotLines=''
                 
        
        if type == 'heatmap' or type=='largeHeatmap':
            if categories!=None and categories!='':
                cat= 'categories: ' + str(categories) + ', '
            else:
                cat=''
            xAxis = """ xAxis: { labels: {rotation: """ + str(xAxisRotation)  + """ },  """  + str(cat)
        
        
        
        if histogram == True:
            categoriesNew=[]
            for elN in range(0, len(categories)):
                if elN > 0:
                    categoriesNew.append('> '+str(categories[elN-1]) + ' =< ' + str(categories[elN]))
            categories = "categories: " +str(categoriesNew) + ", "
        else:
            categories = self._useAttribute6(categories, "categories")
        
        
        if type!='heatmap' and type!='largeHeatmap':

            xAxis = ''
            if multiXAxis == True:

                for wel in range(0, len(xAxisMulti)):

                    if wel==0:
                        xAxis += """
                            xAxis:["""

                    leftVal = 200 * wel


                    if wel ==0:
                        leftVal = 'width: 100,'
                    else:
                        leftVal = 'left:' + str(leftVal) + ', offset:0,' + 'width: 100,'

                    xAxis += """
                         {
                         """ + str(minX) + str(plotLines) + str(leftVal) + """
                         title: {
                         """ + self._useAttribute1(xAxisTitle, "text") + """
                         },
                         """ + self._useAttribute2(tickInterval, "tickInterval") + self._useAttribute4(tickMinValue,
                                                                                                       "min") + categories + self._useAttribute1(
                        typeAxisXScale, "type") + """
                         labels: {
                             """ + self._useAttribute1(xAxisRotation, "rotation") + """
                         }
                         """ + labelX + ",},"
                    wel+=2
                xAxis += """],"""

            else:

                xAxis = """
                 xAxis: {
                  """ + str(minX) + str(plotLines) + """
                  title: { 
                  """ + self._useAttribute1(xAxisTitle, "text") + """
                  }, 
                  """ + self._useAttribute2(tickInterval, "tickInterval") + self._useAttribute4(tickMinValue, "min") + categories +  self._useAttribute1(typeAxisXScale, "type") + """
                  labels: {
                      """ + self._useAttribute1(xAxisRotation, "rotation")  + """
                  }
                  """ + labelX
        
        
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
        if multiXAxis != True:
            xAxis += "},"
        
        return xAxis
    
    
    def _useYAxis(self, yAxisTitle, allowDecimals, maxY, yAxisType, minY, type, categoriesY):
        
        if yAxisType is None:
            yAxisType=''
        else:
            yAxisType = 'type: ' + str(yAxisType) + ', '
        
        if allowDecimals is None:
            allowDecimals=''
        elif allowDecimals==True:
            allowDecimals = ' allowDecimals: true, '
        elif allowDecimals==False:
            allowDecimals = ' allowDecimals: false, '
            
        if maxY is None:
            maxY=''
        else:
            maxY=' max: ' + str(maxY) + ', '
            
        if minY is None:
            minY=''
        else:
            minY=' min: ' + str(minY) + ', '
            
        if type == 'heatmap' or type=='largeHeatmap':
            if categoriesY!=None and categoriesY!='':
                cat= 'categories: ' + str(categoriesY) + ', '
            else:
                cat=''
            return """ yAxis: {  
                            labels: {
                                format: '{value}'
                            },
                            labels: {
                                useHTML: true,
                                formatter: function () {
                                    
                                    if (typeof yAxisNameOverMouse != 'undefined')
                                    {
                                        console.log('a');
                                        return '<div class="hastip" title="'  + 'Track: ' + this.value + ' ' + yAxisNameOverMouse[this.value] +  '" >' + this.value + '</div>';
                                    }
                                    else
                                    {
                                        console.log('b');
                                        return '<div class="hastip" title="'  + 'Track: ' + this.value + '" >' + this.value + '</div>';
                                    }
                                }},
                                minPadding: 0,
                            maxPadding: 0,
                            startOnTick: false,
                            endOnTick: false,
                            tickWidth: 1,
                            tickInterval: 1
              }, """
        else:
            return """
        yAxis: { """ + maxY + minY + allowDecimals + yAxisType + """
                   title: { 
                  """ + self._useAttribute1(yAxisTitle, "text") + """
                  },
            },
        """
        
    def _useMultiYAxis(self, yAxisTitle, reversed, minY):
        
        reversedOpposite=''
        if reversed == None or reversed==False:
            reversed = "reversed: false, height: '35%' ,"
            reversedOpposite= " height: '70%', top: '30%',  "
        elif reversed==True:
            reversed = "reversed: true, height: '35%',"
            reversedOpposite= " height: '70%', top: '30%',  "
        
        
        if minY is None:
            minY=''
        else:
            minY=' min: ' + str(minY) + ', '
        
        yAxis = "yAxis: ["
        
        
        for elNum in range(0, len(yAxisTitle)):
            if elNum < len(yAxisTitle)/2:
                yAxis += """
                     { """+minY+"""
                           title: { 
                          """ +  self._useAttribute1(yAxisTitle[elNum], "text") + """
                          }, """ + reversedOpposite + """
                    },
                """    
            else:
                yAxis += """
                     {"""+minY+"""
                           title: { 
                          """ +self._useAttribute1(yAxisTitle[elNum], "text") + """
                          },
                          opposite: true,
                          """ + reversed + """
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
    def _useChart(self, height, polar, marginTop, zoomType, countNum, type):
        
        if type == 'heatmap' or type =='largeHeatmap':
            chart = """
                chart: { 
                height: """ + str(height) + """, """+ self._useAttribute5(zoomType, 'zoomType') + """
                renderTo: 'container""" + str(self.__class__.count) + """',"""
        else:
        
            chart = """
        chart: { 
                height: """ + str(height) + """,
                renderTo: 'container""" + str(self.__class__.count) + """',
                isZoomed:false,
                """ + self._useAttribute5(zoomType, 'zoomType') + self._useAttribute3(polar, 'polar', 'true') +  self._useAttribute5(marginTop, 'marginTop') + """
            """
        if type == 'pie' or type=='scatter' or type=='heatmap':
            chart += "type: '" + str(type) + "',"
        if type=='largeHeatmap':
            chart += "type: 'heatmap',"
            
        chart += "},"
        return chart
    
    def _usePlotOptions(self, type, stacking, lineWidth, dataLabels, showInLegend, extraArg, histogram, plotOptions):
        
        if showInLegend == True:
            showInLegend='showInLegend: true, '
        elif showInLegend == False:
            showInLegend='showInLegend: false, '
        else:
            showInLegend=''
        
        
        if type == 'scatter':
            return """
            plotOptions: {
                    """ + type + """: { 
                    
                    }
                },
            """
        
        if histogram == True:
            histogram = """
                        pointPadding: 0,
                        borderWidth: 0,
                        groupPadding: 0,
                        shadow: false,
                        """
        else:
            histogram = ""
            
        if plotOptions is None:
            plotOptions = ''
        else:
            plotOptions = """
            pointPadding: 0, // Defaults to 0.1
            groupPadding: 0, // Defaults to 0.2
            """


        if extraArg is None: 
            return """
            plotOptions: {
                    """ + type + """: { 
                        """ + str(showInLegend)  +  histogram + self._useAttribute3(stacking, "stacking", 'normal') + self._useAttribute5(lineWidth, 'lineWidth') + dataLabels + plotOptions  + """
                    }
                },
            """
        if extraArg == 'pie':
            return """
            plotOptions: {
                    """ + type + """: { 
            allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: false
                    },
                    """ + str(showInLegend) + """
             }
                },
            """
        
    def _useToolTip(self, label, shared, extraArg, tooltipVal, histogram, extraScriptButton, type):


        if extraScriptButton:
            if extraScriptButton[1] == 'yAxisType':
                return """
                    tooltip: {
                    formatter: function () {
                        return 'Linear scale: ' +  this.y + ', Log10 scale: ' + Math.log10(this.y)  + ' <br \>' ;
                    }
                    },
                    """


        
        if type=='heatmap' or type =='largeHeatmap':
            return """
            tooltip: {
            formatter: function () {
            
                if (typeof yAxisNameOverMouse != 'undefined')
                {
                    return '<b>' +yAxisNameOverMouse[this.point.y] + '</b>' + '<br><b>' +
                        this.series.xAxis.categories[this.point.x] + '</b> <br>' + this.point.value;
                }
                else
                {
                    return '<b>' + this.point.y + '</b>' + '<br><b>' + this.series.xAxis.categories[this.point.x] + '</b> <br>' + this.point.value;
                }
            }
        },
        """
        
        if histogram == True:
            return """
            tooltip: {
            formatter: function () {
                return this.y + ' <br \>' ;
            }
            },
            """


        if tooltipVal=='categories':
            return """
            tooltip: {
            formatter: function () {
                return '<b>' + this.x + ': </b>' + this.y + ' <br \>' ;
            }
            },
            """

        if tooltipVal=='mix':
            return """
        tooltip: {

                pointFormat: '""" + label + """',
                footerFormat: '',
                shared: """ + shared + """,
                crosshairs: true,
                useHTML: true,
                crosshairs: true
            },
            """

        if extraArg is None or tooltipVal=='seriesName':
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
        if extraArg=='pie':
            return """
            tooltip: {
            formatter: function () {
               
            
                return '<b>' + this.point.name + ': </b>' + this.y + ' <br \>' ;
            }
            },
            """





    def _addButton(self, name):
        return '<div class="buttonArea"><input type="button" name="1" id="button' + str(self.__class__.count) + '" value="' + str(name) + '" ></input></div>';
    
    
    def _draw(self, dataY, legendSize, legendSizeExtra, type, height,addOptions,  tickInterval, tickMinValue, label, lineWidth, titleText, subtitleText, xAxisTitle, yAxisTitle, categories, 
               legend, xAxisRotation, dataLabels, polar, stacking, shared, overMouseAxisX, overMouseLabelX, showChartClickOnLink, typeAxisXScale, pointStartLog, zoomType, marginTop, 
               interaction, multiYAxis, multiXAxis,xAxisMulti, showInLegend, extraArg, allowDecimals, maxY, yAxisType, extraScriptButton, addTable, histogram, sortableAccordingToTable, sortableAccordingToTableDataY, tableName,
               sortableAccordingToTableIndexWithTrackTitle, plotOptions, tooltipVal, reversed, minY, plotLines, categoriesY, plotLinesName,
               plotBands, plotBandsColor):
        
        
        container=''
        
        if self.__class__.count==1:
            container += self._addLib() + self._addStyle()
            if tableName is None:
                container += self._addGuidelineV1('tableName')
            else:
                container += self._addGuidelineV1(tableName)

        
            
        container += self._buildContainer(addOptions, addTable, titleText)
        
        if type == 'largeHeatmap':
            container += str(dataY)
        
        jsCodeShowChartClickOnLink=''
        
                
        if overMouseAxisX==True:
            labelX = """
                ,
                useHTML: true,
                formatter: function () {
                    console.log(this);
                    return '<div class="hastip" title="' + this.value + ' ">' """ + overMouseLabelX + """ '</div>';
                }
        """
            yAxisMO = """ $('.hastip').tooltipsy(); """
        else:
            labelX=''
            yAxisMO=''
    
        #default legend center
        if legend is None:
            legend = "align: 'center', "
        if legend == False:
            legend = "enabled: false, "



        if legendSize != '':
            legendSize = legendSize*6+36 
            legendSizeExtra = legendSizeExtra+100
            legendSize = """maxHeight: """ + str(legendSizeExtra) + """, itemWidth: """ + str(legendSize) + ","
            
        if type=='heatmap' or type=='largeHeatmap':
            legend=""
#             legend = """
#              legend: {
#             align: 'right',
#             layout: 'vertical',
#             margin: 0,
#             verticalAlign: 'middle',
#             y: 25,
#             symbolHeight: 280
#             },
#             """
        else:
            
            legend = """ legend: { """ + str(legend) + str(legendSize) + 'itemMarginBottom: 10,' + """},"""
        
        if height is None:
            height = self._height
            
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

        
        if type=='largeHeatmap':
            catNew=" var yAxisNameOverMouse =[];  "
            if categories!=None:
                catNew = " var yAxisNameOverMouse =" + str(categoriesY) + ";  "
            functionJS1 = " <script> $(function () { " +  self._themePlot() + self._addToLargeHeatmap() + catNew  + "chart"+ str(self.__class__.count)+" = new Highcharts.Chart({"
        else:
            functionJS1 = " <script> $(function () { " +  self._themePlot() + "chart"+ str(self.__class__.count)+" = new Highcharts.Chart({"
        
        
        functionJS1 += str(self._useChart(height, polar, marginTop, zoomType, self.__class__.count, type)) 
        functionJS1 += str(self._useTitle(titleText)) 
        functionJS1 += str(self._useSubTitle(subtitleText))
        functionJS1 += str(self._useXAxis(xAxisTitle, tickInterval, tickMinValue, categories, typeAxisXScale, xAxisRotation, \
                                          labelX, interaction, type, histogram, plotLines, plotLinesName,
                                          plotBands, plotBandsColor, multiXAxis,xAxisMulti))
        
        if multiYAxis==True:
            functionJS1 += str(self._useMultiYAxis(yAxisTitle, reversed, minY))
        else:
            functionJS1 += str(self._useYAxis(yAxisTitle, allowDecimals, maxY, yAxisType, minY, type, categoriesY))




        if type != 'bubble' and type !='heatmap':
            functionJS1 += str(self._usePlotOptions(type, stacking, lineWidth, dataLabels, showInLegend, extraArg, histogram, plotOptions)) 
        functionJS1 += str(self._useToolTip(label, shared, extraArg, tooltipVal, histogram, extraScriptButton, type))
        functionJS1 += legend 
        
        if type == 'largeHeatmap':
            functionJS1 += """
            data: {
                csv: document.getElementById('csv').innerHTML,
                parsed: function () {
                    start = +new Date();
                }
            },
            
            series: [{
            borderWidth: 0,
            nullColor: '#EFEFEF',
            colsize: 1.01,
            turboThreshold: Number.MAX_VALUE // #3404, remove after 4.0.5 release
        }],
            
            """
        else:
        
            functionJS1 += " series: [{ " + self._useAttribute4(pointStartLog, "pointStart") 
        
        
        if extraScriptButton is None:
            extraScriptButton=''
            button=''
        else:
            if extraScriptButton[0].keys():
                if len(extraScriptButton[0].keys()) == 0:
                    extraScriptButton[0]['Update']= ''
                    extraScriptButton[0]['Previous'] =''
                elif len(extraScriptButton[0].keys()) == 1:
                        extraScriptButton[0]['Previous'] =''
                button = self._addButton(extraScriptButton[0].keys()[1])
            else:
                extraScriptButton[0]={'Update': '', 'Previous':''}
                button = self._addButton(extraScriptButton[0].keys()[1])
            
            extraSc1=''
            extraSc2=''
            if extraScriptButton[1]:
                if extraScriptButton[1] == 'yAxisType':
                    extraSc1 = """chart.yAxis[0].update({ type: '""" + extraScriptButton[0][extraScriptButton[0].keys()[1]]  +  """'});"""
                    extraSc2 = """chart.yAxis[0].update({ type: '""" + extraScriptButton[0][extraScriptButton[0].keys()[0]]  +  """'});"""
                
                
            
            
            extraScriptButton = """\n
                 $('#button""" + str(self.__class__.count)   + """').click(function(e) {
                 
                 var chart = $('#container""" + str(self.__class__.count) + """').highcharts();
                 
                 if(document.getElementById('button""" + str(self.__class__.count)   + """').name == 1)
                 {
                    document.getElementById('button""" + str(self.__class__.count)     + """').value = '""" + extraScriptButton[0].keys()[0] + """';
                    """ + extraSc1  + """
                    document.getElementById('button""" + str(self.__class__.count)   + """').name=0
                 }
                 else
                 {
                    document.getElementById('button""" + str(self.__class__.count)     + """').value = '""" + extraScriptButton[0].keys()[1] + """';
                    """ + extraSc2  + """
                    document.getElementById('button""" + str(self.__class__.count)   + """').name=1
                 }
                 
                 });
                 """
        
        if sortableAccordingToTable is None:
            sortableAccordingToTable=''   
        elif sortableAccordingToTable == True:
            
            try:
                sortableAccordingToTableDataY = json.dumps(sortableAccordingToTableDataY).replace('"', "")
            except Exception, e:
                sortableAccordingToTableDataY=sortableAccordingToTableDataY
            
            
            
            sortableAccordingToTable = """
                
                var el = 0;
                var x = document.getElementById('""" + str(tableName) + """').getElementsByTagName("th");
                
                //console.log('x', x);
                
                var specInd  = parseInt(""" + str(sortableAccordingToTableIndexWithTrackTitle) + """);
                
                
                for (i = 0; i < x.length; i++) 
                {
                    wString  = x[i].innerHTML;
                    if(wString.indexOf('"""+titleText+"""') >= 0)
                    {
                        el=i;
                    }
                }
                
                resTabJS  = """ + str(sortableAccordingToTableDataY) + """;
                
                function depthOfData(A)
                {
                    var depth = 0;
                    //console.log('A', A, 'A[0]', A[0])

                    var i=0;
                    for (var i=0; i< A.length; i++)
                    {
                        if (A[i]!= undefined)
                        {
                            break;
                        }
                    }

                    console.log('i', i, 'A[i]', A[i])

                    if (A[i]!= undefined)
                    {
                        depth=1;

                        var j=0;
                        for (var j=0; j< A.length; j++)
                        {
                            if (A[i][j]!= undefined)
                            {
                                break;
                            }
                        }

                        if (A[i][j]!= undefined)
                        {
                            depth=2;
                            if (A[i][j][0]!= undefined)
                            {
                                depth=3;
                            }
                        }
                    }



                    return depth;
                }
                

                
                $(document.getElementById('""" + str(tableName) + """').getElementsByTagName("th")[el]).click(function(e) 
                {
                
                    //depthYdata = depthOfData(""" + str(sortableAccordingToTableDataY) + """);
                    depthYdata = depthOfData(resTabJS);
                    
                    console.log('1 ---- ', resTabJS, depthYdata );
                    
                    var xx = document.getElementById('""" + str(tableName) + """').getElementsByTagName("td");
                    var yy = document.getElementById('""" + str(tableName) + """').getElementsByTagName("th");
                    
                    
                    namesFromTable=[]
                    var j=0;
                    for (i = 0; i < xx.length; i++) 
                    {
                        if (i%yy.length==0)
                        {
                            //console.log('xx[i].innerHTML', xx[i].innerHTML);
                            namesFromTable[j] = xx[i+specInd].innerHTML;
                            j=j+1
                        }
                    }
                    
                    var containerEl = el-specInd;
                    
                    //console.log('++++++++el+', el, namesFromTable);
                
                    for (var i = 1; i < x.length; i++)
                    {
                        //console.log('el==i', el, i, specInd, depthYdata);
                        
                        
                        
                        if (containerEl == i)
                        {
                            containerName = '#container'+ containerEl;
                            
                            //console.log('1', containerName, el, '""" + str(tableName) + """');
                            
                            classNameTH = document.getElementById('""" + str(tableName) + """').getElementsByTagName("th")[el].className;   
                            
                            var chart = $(containerName).highcharts();
                            
                            if (chart != undefined)
                            {
                                
                                //console.log('11', chart, namesFromTable, resTabJS);
                                
                                //console.log('depthYdata', depthYdata);
                                
                                if (classNameTH.replace(/\s+/g, '') == 'header sorttable_sorted_reverse'.replace(' ', ''))
                                {
                                    elN=el-1-specInd;
                                    
                                    console.log('1111', 'elN', elN);
                                    
                                    if (depthYdata==1)
                                    {
                                        sL = sortTwoLists(resTabJS, """ + str(categories) + """, namesFromTable, 'asc');
                                    }
                                    else
                                    {
                                        sL = sortTwoLists(resTabJS[elN], """ + str(categories) + """, namesFromTable, 'asc');
                                    }
                                    
                                    //console.log('111',chart, elN, sL[0], namesFromTable, sL[0][elN]);
                                    
                                    chart.xAxis[0].setCategories(namesFromTable);
                                    chart.series[0].setData(sL[0]);
                                    //console.log('a');
                                }
                                else if(classNameTH.replace(/\s+/g, '')== 'header sorttable_sorted'.replace(' ', ''))
                                {
                                    elN=el-1-specInd;
                                    
                                    console.log('1112', 'elN', elN);
                                    
                                    if (depthYdata==1)
                                    {
                                        console.log('1', resTabJS, namesFromTable);
                                        sL = sortTwoLists(resTabJS, """ + str(categories) + """, namesFromTable, 'desc');
                                    }
                                    else
                                    {
                                        console.log('2', resTabJS[elN], namesFromTable);
                                        sL = sortTwoLists(resTabJS[elN], """ + str(categories) + """, namesFromTable, 'desc');
                                    }
                                    
                                    //console.log('112',chart, elN, sL[0], namesFromTable, sL[0][elN]);

                                    //console.log(sL[0]);
                                    chart.xAxis[0].setCategories(namesFromTable);
                                    chart.series[0].setData(sL[0]);
                                    //console.log('b');
                                }
                            }
                        }
                    }
                    
                    //console.log('------------x.length', x.length);
                    
                    for (var i = 1; i < x.length; i++)
                    {
                        //console.log('el!=i', el, i, depthYdata);
                        
                        if (containerEl != i)
                        {
                            containerName = '#container'+ i;
                            classNameTH = document.getElementById('""" + str(tableName) + """').getElementsByTagName("th")[el].className;   
                            
                            //console.log('2', containerName);
                            var chart = $(containerName).highcharts();
                            
                            //console.log('22', resTabJS);
                            
                            if (chart != undefined)
                            {
                                //console.log('222', chart);
                                if (classNameTH.replace(/\s+/g, '') == 'header sorttable_sorted_reverse'.replace(' ', ''))
                                {
                                    elN=i-1;
                                    
                                    //console.log('222', chart, elN);
                                    
                                    newSL = sortListAccordingToOtherList(sL[1], resTabJS[elN]);
                                    //console.log(resTabJS[elN], namesFromTable, 'asc', newSL);
                                    chart.xAxis[0].setCategories(namesFromTable);
                                    chart.series[0].setData(newSL);
                                }
                                else if(classNameTH.replace(/\s+/g, '')== 'header sorttable_sorted'.replace(' ', ''))
                                {
                                    elN=i-1;
                                    
                                    //console.log('223', chart, elN);
                                    newSL = sortListAccordingToOtherList(sL[1], resTabJS[elN]);
                                    //console.log(resTabJS[elN], namesFromTable, 'desc', newSL);
                                    chart.xAxis[0].setCategories(namesFromTable);
                                    chart.series[0].setData(newSL);
                                }
                            }
                        }
                    
                    }
                    
                });
                
                
                
               
                """
                
            
                
        if type!='heatmap' and type != 'largeHeatmap':
            functionJS2 = """ ] } """ + inter  + """    );"""+ sortableAccordingToTable +  extraScriptButton + """  }  , function(chart) {  $('.hastip').tooltipsy(); }   ); </script> """
        else:
            if type == 'largeHeatmap':
                functionJS2 = """
                    colorAxis: {
            stops: [
                [0, '#ffffff'],
                [0.1, '#f2f2f2'],
                [0.2, '#ffcc00'],
                [0.3, '#ff9900'],
                [0.4, '#b35900'],
                [0.5, '#ff1ab3'],
                [0.6, '#ff3333'],
                [0.7, '#33cc33'],
                [0.8, '#206040'],
                [0.9, '#0099ff'],
                [1, '#00004d']
            ],
            startOnTick: false,
            endOnTick: false,
            labels: {
                format: '{value}'
            }
            },
                     """ + inter  + """     }); """+ sortableAccordingToTable +  extraScriptButton + """ }); </script> """
        
            else:
                functionJS2 = """ }],
                colorAxis: {
                min: 0,
                minColor: '#FFFFFF',
                maxColor: Highcharts.getOptions().colors[0]
                },
                 """ + inter  + """     }); """+ sortableAccordingToTable +  extraScriptButton + """ }); </script> """
        
        
        
        self.__class__.count +=1  
        
        if type=='largeHeatmap':
            return '{0}{1}{2}{3}{4}'.format(button, jsCodeShowChartClickOnLink, container, functionJS1, functionJS2)
        else:
            return '{0}{1}{2}{3}{4}{5}'.format(button, jsCodeShowChartClickOnLink, container, functionJS1, dataY, functionJS2)

    
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
    
    def drawLineChart(self, 
                      dataY, 
                      height=None, 
                      addOptions = None,
                      tickInterval=None, 
                      tickMinValue=None, 
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
                      overMouseAxisX=False, 
                      overMouseLabelX=' + this.value + ', 
                      showChartClickOnLink=False, 
                      typeAxisXScale=None, 
                      pointStartLog=None,
                      zoomType='x',
                      marginTop=60,
                      interaction=False,
                      extraArg=None,
                      allowDecimals=None,
                      maxY=None,
                      yAxisType=None,
                      extraScriptButton=None,
                      visible=None,
                      addTable=None,
                      minY=None,
                      plotLines=None,
                      plotLinesName=None,
                      plotBands=None, 
                      plotBandsColor=None
                     ):
        
        graph=''
        
        if len(dataY) > 0:

            tooltipVal=None
            if categories is not None:
                tooltipVal = 'categories'
            if seriesName is not None:
                tooltipVal = 'seriesName'
        
            type='line'
            data, legendSize, legendSizeExtra = self._parseData(dataY=dataY, type = type, seriesType=seriesType, seriesName=seriesName, multiYAxis=False, 
                                                                visible=visible, yAxisMulti=None, multiXAxis=False, xAxisMulti=None, markerRadius=None)


            graph = self._draw(
                           data, legendSize, legendSizeExtra, 
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
                           stacking=None, 
                           shared=shared, 
                           overMouseAxisX=overMouseAxisX, 
                           overMouseLabelX=overMouseLabelX, 
                           showChartClickOnLink=showChartClickOnLink, 
                           typeAxisXScale=typeAxisXScale, 
                           pointStartLog=pointStartLog, 
                           zoomType=zoomType, 
                           marginTop=marginTop, 
                           interaction=interaction,
                           multiYAxis=False,multiXAxis=False,xAxisMulti=None,
                           showInLegend=None,
                           extraArg=extraArg,
                           allowDecimals=allowDecimals,
                           maxY=maxY,
                           yAxisType=yAxisType,
                           extraScriptButton=extraScriptButton,
                           addTable=addTable,
                           histogram=None,
                           sortableAccordingToTable=None,
                           sortableAccordingToTableDataY=None,
                           tableName = None,
                           sortableAccordingToTableIndexWithTrackTitle=0,
                           plotOptions=None,
                            tooltipVal=tooltipVal, 
                            reversed=None, 
                            minY=minY, 
                            plotLines=plotLines, 
                            categoriesY=None,
                            plotLinesName=plotLinesName,
                            plotBands=plotBands, 
                      plotBandsColor=plotBandsColor
                           )
        return graph

    def drawAreaChart(self,
                          dataY,
                          height=None,
                          addOptions=None,
                          tickInterval=None,
                          tickMinValue=None,
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
                          overMouseAxisX=False,
                          overMouseLabelX=' + this.value + ',
                          showChartClickOnLink=False,
                          typeAxisXScale=None,
                          pointStartLog=None,
                          zoomType='x',
                          marginTop=60,
                          interaction=False,
                          extraArg=None,
                          allowDecimals=None,
                          maxY=None,
                          yAxisType=None,
                          extraScriptButton=None,
                          visible=None,
                          addTable=None,
                          minY=None,
                          plotLines=None,
                          plotLinesName=None,
                          plotBands=None,
                          plotBandsColor=None
                          ):


        graph = ''

        if len(dataY) > 0:

            tooltipVal = None
            if categories is not None:
                tooltipVal = 'categories'
            if seriesName is not None:
                tooltipVal = 'seriesName'

            type = 'area'
            data, legendSize, legendSizeExtra = self._parseData(dataY=dataY, type=type, seriesType=seriesType,
                                                                seriesName=seriesName, multiYAxis=False,
                                                                visible=visible, yAxisMulti=None, multiXAxis=False,
                                                                xAxisMulti=None, markerRadius=None)

            graph = self._draw(
                data, legendSize, legendSizeExtra,
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
                stacking=None,
                shared=shared,
                overMouseAxisX=overMouseAxisX,
                overMouseLabelX=overMouseLabelX,
                showChartClickOnLink=showChartClickOnLink,
                typeAxisXScale=typeAxisXScale,
                pointStartLog=pointStartLog,
                zoomType=zoomType,
                marginTop=marginTop,
                interaction=interaction,
                multiYAxis=False, multiXAxis=False, xAxisMulti=None,
                showInLegend=None,
                extraArg=extraArg,
                allowDecimals=allowDecimals,
                maxY=maxY,
                yAxisType=yAxisType,
                extraScriptButton=extraScriptButton,
                addTable=addTable,
                histogram=None,
                sortableAccordingToTable=None,
                sortableAccordingToTableDataY=None,
                tableName=None,
                sortableAccordingToTableIndexWithTrackTitle=0,
                plotOptions=None,
                tooltipVal=tooltipVal,
                reversed=None,
                minY=minY,
                plotLines=plotLines,
                categoriesY=None,
                plotLinesName=plotLinesName,
                plotBands=plotBands,
                plotBandsColor=plotBandsColor
            )
        return graph
    
    def drawHeatmapLargeChart(self, 
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
                      overMouseAxisX=False, 
                      overMouseLabelX=' + this.value + ', 
                      showChartClickOnLink=False, 
                      typeAxisXScale=None, 
                      pointStartLog=None,
                      zoomType='x',
                      marginTop=60,
                      interaction=False,
                      extraArg=None,
                      allowDecimals=None,
                      maxY=None,
                      yAxisType=None,
                      extraScriptButton=None,
                      visible=None,
                      addTable=None,
                      showInLegend=None,
                      histogram=None,
                      sortableAccordingToTable=None,
                      sortableAccordingToTableDataY=None,
                      tableName = None, 
                      sortableAccordingToTableIndexWithTrackTitle=0,
                      plotOptions=None,
                      minY=None,
                      plotLines=None,
                      categoriesY=None,
                      plotBands=None, 
                      plotBandsColor=None
                     ):
        
        
        type='largeHeatmap'

        graph=''
        
        if seriesName is not None:
            graph += """<script> 
                        if (typeof yAxisNameOverMouse == 'undefined')
                        {
                             yAxisNameOverMouse = """ + str(seriesName) + """;
                        }     
                        </script>"""
        
        if len(dataY) > 0:


            tooltipVal=None
            if categories is not None:
                tooltipVal = 'categories'
            if seriesName is not None:
                tooltipVal = 'seriesName'
            if seriesName is not None and categories is not None:
                tooltipVal='mix'

            legendSize=0 
            legendSizeExtra=0
            data = self._parseData4(dataY=dataY)
            
            
            
            graph += self._draw(
                               data, legendSize, legendSizeExtra, 
                               type=type, 
                               height=height, 
                               addOptions=addOptions,
                               tickInterval=tickInterval, 
                               tickMinValue=None,  
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
                               stacking=None, 
                               shared=shared, 
                               overMouseAxisX=overMouseAxisX, 
                               overMouseLabelX=overMouseLabelX, 
                               showChartClickOnLink=showChartClickOnLink, 
                               typeAxisXScale=typeAxisXScale, 
                               pointStartLog=pointStartLog, 
                               zoomType=zoomType, 
                               marginTop=marginTop, 
                               interaction=interaction,
                               multiYAxis=False,multiXAxis=False,xAxisMulti=None,
                               showInLegend=showInLegend,
                               extraArg=extraArg,
                               allowDecimals=allowDecimals,
                               maxY=maxY,
                               yAxisType=yAxisType,
                               extraScriptButton=extraScriptButton,
                               addTable=addTable,
                               histogram=histogram,
                               sortableAccordingToTable=sortableAccordingToTable,
                               sortableAccordingToTableDataY=sortableAccordingToTableDataY,
                               tableName =tableName,
                               sortableAccordingToTableIndexWithTrackTitle=sortableAccordingToTableIndexWithTrackTitle,
                               plotOptions=plotOptions,
                tooltipVal=tooltipVal, reversed=None, minY=minY,plotLines=plotLines, categoriesY=categoriesY,plotLinesName=None,
                plotBands=None, 
                      plotBandsColor=None
                               )
            
        return graph
    
    
    def drawHeatmapSmallChart(self, 
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
                      overMouseAxisX=False, 
                      overMouseLabelX=' + this.value + ', 
                      showChartClickOnLink=False, 
                      typeAxisXScale=None, 
                      pointStartLog=None,
                      zoomType='x',
                      marginTop=60,
                      interaction=False,
                      extraArg=None,
                      allowDecimals=None,
                      maxY=None,
                      yAxisType=None,
                      extraScriptButton=None,
                      visible=None,
                      addTable=None,
                      showInLegend=None,
                      histogram=None,
                      sortableAccordingToTable=None,
                      sortableAccordingToTableDataY=None,
                      tableName = None, 
                      sortableAccordingToTableIndexWithTrackTitle=0,
                      plotOptions=None,
                      minY=None,
                      plotLines=None,
                      categoriesY=None,
                      plotLinesName=None,
                      plotBands=None, 
                      plotBandsColor=None
                     ):
        
        
        type='heatmap'

        graph=''
        
        if len(dataY) > 0:


            tooltipVal=None
            if categories is not None:
                tooltipVal = 'categories'
            if seriesName is not None:
                tooltipVal = 'seriesName'
            if seriesName is not None and categories is not None:
                tooltipVal='mix'

            legendSize=0 
            legendSizeExtra=0
            data = self._parseData3(dataY=dataY)
            
            if seriesName is not None:
                graph += """<script> 
                            if (typeof yAxisNameOverMouse == 'undefined')
                            {
                                 yAxisNameOverMouse = """ + str(seriesName) + """;
                            }     
                            </script>"""
            
            
            graph += self._draw(
                               data, legendSize, legendSizeExtra, 
                               type=type, 
                               height=height, 
                               addOptions=addOptions,
                               tickInterval=tickInterval, 
                               tickMinValue=None,  
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
                               stacking=None, 
                               shared=shared, 
                               overMouseAxisX=overMouseAxisX, 
                               overMouseLabelX=overMouseLabelX, 
                               showChartClickOnLink=showChartClickOnLink, 
                               typeAxisXScale=typeAxisXScale, 
                               pointStartLog=pointStartLog, 
                               zoomType=zoomType, 
                               marginTop=marginTop, 
                               interaction=interaction,
                               multiYAxis=False,multiXAxis=False,xAxisMulti=None,
                               showInLegend=showInLegend,
                               extraArg=extraArg,
                               allowDecimals=allowDecimals,
                               maxY=maxY,
                               yAxisType=yAxisType,
                               extraScriptButton=extraScriptButton,
                               addTable=addTable,
                               histogram=histogram,
                               sortableAccordingToTable=sortableAccordingToTable,
                               sortableAccordingToTableDataY=sortableAccordingToTableDataY,
                               tableName =tableName,
                               sortableAccordingToTableIndexWithTrackTitle=sortableAccordingToTableIndexWithTrackTitle,
                               plotOptions=plotOptions,
                tooltipVal=tooltipVal, reversed=None, minY=minY,plotLines=plotLines, categoriesY=categoriesY,plotLinesName=None,
                plotBands=None, 
                      plotBandsColor=None
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
                      overMouseAxisX=False, 
                      overMouseLabelX=' + this.value + ', 
                      showChartClickOnLink=False, 
                      typeAxisXScale=None, 
                      pointStartLog=None,
                      zoomType='x',
                      marginTop=60,
                      interaction=False,
                      extraArg=None,
                      allowDecimals=None,
                      maxY=None,
                      yAxisType=None,
                      extraScriptButton=None,
                      visible=None,
                      addTable=None,
                      showInLegend=None,
                      histogram=None,
                      sortableAccordingToTable=None,
                      sortableAccordingToTableDataY=None,
                      tableName = None, 
                      sortableAccordingToTableIndexWithTrackTitle=0,
                      plotOptions=None,
                      minY=None,
                      plotLines=None,
                      plotLinesName=None,
                      plotBands=None, 
                      plotBandsColor=None,
                      stacking = None
                     ):
        
        
        type='column'

        graph=''
        
        if len(dataY) > 0:

            tooltipVal=None
            if categories is not None:
                tooltipVal = 'categories'
            if seriesName is not None:
                tooltipVal = 'seriesName'
            if seriesName is not None and categories is not None:
                tooltipVal='mix'


            
            data, legendSize, legendSizeExtra = self._parseData(dataY=dataY, type = type, seriesType=seriesType, seriesName=seriesName, multiYAxis=False, 
                                                                visible=visible, yAxisMulti=None, multiXAxis=False, xAxisMulti=None, markerRadius=None)
            
            #print 'data' + str(data)
            
            graph=''
            if sortableAccordingToTableDataY is None:
                sortableAccordingToTableDataY = dataY
                if addTable==True:
                    if tableName is None:
                        tableName ='resultsTable'
                    graph += self.addTable(titleText, tableName=tableName, option=2, indexSpecial=sortableAccordingToTableIndexWithTrackTitle)
                    addTable = 'option2'
            
            
            graph += self._draw(
                               data, legendSize, legendSizeExtra, 
                               type=type, 
                               height=height, 
                               addOptions=addOptions,
                               tickInterval=tickInterval, 
                               tickMinValue=None,  
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
                               multiYAxis=False,multiXAxis=False,xAxisMulti=None,
                               showInLegend=showInLegend,
                               extraArg=extraArg,
                               allowDecimals=allowDecimals,
                               maxY=maxY,
                               yAxisType=yAxisType,
                               extraScriptButton=extraScriptButton,
                               addTable=addTable,
                               histogram=histogram,
                               sortableAccordingToTable=sortableAccordingToTable,
                               sortableAccordingToTableDataY=sortableAccordingToTableDataY,
                               tableName =tableName,
                               sortableAccordingToTableIndexWithTrackTitle=sortableAccordingToTableIndexWithTrackTitle,
                               plotOptions=plotOptions,
                tooltipVal=tooltipVal, reversed=None, minY=minY,plotLines=plotLines, categoriesY=None,plotLinesName=plotLinesName,
                plotBands=plotBands, 
                      plotBandsColor=plotBandsColor
                               )
            
        return graph
    
    def drawScatterChart(self, 
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
                      overMouseAxisX=False, 
                      overMouseLabelX=' + this.value + ', 
                      showChartClickOnLink=False, 
                      typeAxisXScale=None, 
                      pointStartLog=None,
                      zoomType='x',
                      marginTop=60,
                      interaction=False,
                      extraArg=None,
                      allowDecimals=None,
                      maxY=None,
                      yAxisType=None,
                      extraScriptButton=None,
                      visible=None,
                      addTable=None,
                      markerRadius=None,
                      minY=None,
                      plotLines=None,
                      plotLinesName=None,
                      plotBands=None, 
                      plotBandsColor=None
                     ):
        
        
        type='scatter'
        
        graph=''
        
        if len(dataY) > 0:

            tooltipVal=None
        
            data, legendSize, legendSizeExtra = self._parseData(dataY=dataY, type = type, seriesType=seriesType, seriesName=seriesName, multiYAxis=False, 
                                                                visible=visible, yAxisMulti=None, multiXAxis=False, xAxisMulti=None, markerRadius=markerRadius)
            
            #print 'data' + str(data)
            
            graph = self._draw(
                               data, legendSize, legendSizeExtra, 
                               type=type, 
                               height=height, 
                               addOptions=addOptions,
                               tickInterval=tickInterval, 
                               tickMinValue=None,  
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
                           stacking=None, 
                           shared=shared, 
                           overMouseAxisX=overMouseAxisX, 
                           overMouseLabelX=overMouseLabelX, 
                           showChartClickOnLink=showChartClickOnLink, 
                           typeAxisXScale=typeAxisXScale, 
                           pointStartLog=pointStartLog, 
                           zoomType=zoomType, 
                           marginTop=marginTop, 
                           interaction=interaction,
                           multiYAxis=False,multiXAxis=False,xAxisMulti=None,
                           showInLegend=None,
                           extraArg=extraArg,
                           allowDecimals=allowDecimals,
                           maxY=maxY,
                           yAxisType=yAxisType,
                           extraScriptButton=extraScriptButton,
                           addTable=addTable,
                           histogram=None,
                          sortableAccordingToTable=None,
                          sortableAccordingToTableDataY=None,
                          tableName = None,
                          sortableAccordingToTableIndexWithTrackTitle=None,
                          plotOptions=None,
                tooltipVal=tooltipVal, reversed=None, minY=minY,plotLines=plotLines, categoriesY=None,plotLinesName=plotLinesName,
                plotBands=plotBands, 
                      plotBandsColor=plotBandsColor
                           )
        
        return graph
    
    def drawBubbleChart(self, 
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
                      overMouseAxisX=False, 
                      overMouseLabelX=' + this.value + ', 
                      showChartClickOnLink=False, 
                      typeAxisXScale=None, 
                      pointStartLog=None,
                      zoomType='x',
                      marginTop=60,
                      interaction=False,
                      extraArg=None,
                      allowDecimals=None,
                      maxY=None,
                      yAxisType=None,
                      extraScriptButton=None,
                      visible = None,
                      addTable=None,
                      tableName=None,
                      minY=None,
                      plotLines=None,
                      plotLinesName=None,
                     ):
        
        
        type='bubble'
        
        
        graph=''
        
        if len(dataY) > 0:

            tooltipVal=None

            data, legendSize, legendSizeExtra = self._parseData(dataY=dataY, type = type, seriesType=seriesType, seriesName=seriesName, multiYAxis=False, 
                                                                visible=visible, yAxisMulti=None, multiXAxis=False, xAxisMulti=None, markerRadius=None)
            
            #print 'data' + str(data)
            
            
            
            graph = self._draw(
                               data, legendSize, legendSizeExtra, 
                           type=type, 
                           height=height, 
                           addOptions=addOptions,
                           tickInterval=tickInterval, 
                           tickMinValue=None,  
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
                           stacking=None, 
                           shared=shared, 
                           overMouseAxisX=overMouseAxisX, 
                           overMouseLabelX=overMouseLabelX, 
                           showChartClickOnLink=showChartClickOnLink, 
                           typeAxisXScale=typeAxisXScale, 
                           pointStartLog=pointStartLog, 
                           zoomType=zoomType, 
                           marginTop=marginTop, 
                           interaction=interaction,
                           multiYAxis=False,multiXAxis=False,xAxisMulti=None,
                           showInLegend=None,
                           extraArg=extraArg,
                           allowDecimals=allowDecimals,
                           maxY=maxY,
                           yAxisType=yAxisType,
                           extraScriptButton=extraScriptButton,
                           addTable=addTable,
                           histogram=None,
                           sortableAccordingToTable=None,
                           sortableAccordingToTableDataY=None,
                           tableName = tableName,
                           sortableAccordingToTableIndexWithTrackTitle=None,
                           plotOptions=None,
                tooltipVal=tooltipVal, reversed=None, minY=minY,plotLines=plotLines, categoriesY=None, plotLinesName=plotLinesName,
                plotBands=None, 
                      plotBandsColor=None
                           )
        
        return graph
    
    def drawBarChart(self, 
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
                      overMouseAxisX=False, 
                      overMouseLabelX=' + this.value + ', 
                      showChartClickOnLink=False, 
                      typeAxisXScale=None, 
                      pointStartLog=None,
                      zoomType='x',
                      marginTop=60,
                      interaction=False,
                      extraArg=None,
                      allowDecimals=None,
                      maxY=None,
                      yAxisType=None,
                      extraScriptButton=None,
                      visible=None,
                      addTable=None,
                      minY=None,
                      plotLines=None,
                      plotLinesName=None,
                      plotBands=None, 
                      plotBandsColor=None
                     ):
        
        
        type='bar'
        
        graph=''
        
        if len(dataY) > 0:

            tooltipVal=None
            if categories is not None:
                tooltipVal = 'categories'
            if seriesName is not None:
                tooltipVal = 'seriesName'
        
            data, legendSize, legendSizeExtra = self._parseData(dataY=dataY, type = type, seriesType=seriesType, seriesName=seriesName, multiYAxis=False, 
                                                                visible=visible, yAxisMulti=None, multiXAxis=False, xAxisMulti=None, markerRadius=None)
            
            #print 'data' + str(data)
            
            graph = self._draw(
                           data, legendSize, legendSizeExtra, 
                           type=type, 
                           height=height, 
                           addOptions=addOptions,
                           tickInterval=tickInterval, 
                           tickMinValue=None,  
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
                           stacking=None, 
                           shared=shared, 
                           overMouseAxisX=overMouseAxisX, 
                           overMouseLabelX=overMouseLabelX, 
                           showChartClickOnLink=showChartClickOnLink, 
                           typeAxisXScale=typeAxisXScale, 
                           pointStartLog=pointStartLog, 
                           zoomType=zoomType, 
                           marginTop=marginTop, 
                           interaction=interaction,
                           multiYAxis=False,multiXAxis=False,xAxisMulti=None,
                           showInLegend=None,
                           extraArg=extraArg,
                           allowDecimals=allowDecimals,
                           maxY=maxY,
                           yAxisType=yAxisType,
                           extraScriptButton=extraScriptButton,
                           addTable=addTable,
                           histogram=None,
                      sortableAccordingToTable=None,
                      sortableAccordingToTableDataY=None,
                      tableName = None,
                      sortableAccordingToTableIndexWithTrackTitle=None,
                      plotOptions=None,
                        tooltipVal=tooltipVal, reversed=None, minY=minY,plotLines=plotLines, categoriesY=None,plotLinesName=plotLinesName,
                        plotBands=None, 
                      plotBandsColor=None
                           )
        
        return graph
    
    
    
    def drawLineChartMultiYAxis(self, 
                      dataY, 
                      height=None,
                      addOptions=None,
                      tickInterval=None, 
                      tickMinValue=None, 
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
                      overMouseAxisX=False, 
                      overMouseLabelX=' + this.value + ', 
                      showChartClickOnLink=False, 
                      typeAxisXScale=None, 
                      pointStartLog=None,
                      zoomType='x',
                      marginTop=60,
                      interaction=False,
                      extraArg=None,
                      allowDecimals=None,
                      yAxisType=None,
                      extraScriptButton=None,
                      visible=None,
                      addTable=None,
                      yAxisMulti=None,
                      markerRadius=None,
                      reversed=None,
                      minY=None,
                      plotLines=None,
                      plotLinesName=None,
                      plotBands=None, 
                      plotBandsColor=None
                     ):
        
        graph=''
        
        if len(dataY) > 0:

            tooltipVal=None
            if categories is not None:
                tooltipVal = 'categories'
            if seriesName is not None:
                tooltipVal = 'seriesName'
            
            data, legendSize, legendSizeExtra = self._parseData(dataY=dataY, type = 'line', seriesType=seriesType, seriesName=seriesName, multiYAxis=True, 
                                                                visible=visible, yAxisMulti=yAxisMulti, multiXAxis=False, xAxisMulti=None, markerRadius=markerRadius)
            graph = self._draw(
                           data, legendSize, legendSizeExtra, 
                           type='line', 
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
                           stacking=None, 
                           shared=shared, 
                           overMouseAxisX=overMouseAxisX, 
                           overMouseLabelX=overMouseLabelX, 
                           showChartClickOnLink=showChartClickOnLink, 
                           typeAxisXScale=typeAxisXScale, 
                           pointStartLog=pointStartLog, 
                           zoomType=zoomType, 
                           marginTop=marginTop, 
                           interaction=interaction,
                           multiYAxis=True,multiXAxis=False,xAxisMulti=None,
                           showInLegend=None,
                           extraArg=extraArg,
                           allowDecimals=allowDecimals,
                           maxY=None,
                           yAxisType=yAxisType,
                           extraScriptButton=extraScriptButton,
                           addTable=addTable,
                           histogram=None,
                          sortableAccordingToTable=None,
                          sortableAccordingToTableDataY=None,
                          tableName = None,
                          sortableAccordingToTableIndexWithTrackTitle=None,
                          plotOptions=None,
                tooltipVal=tooltipVal,
                reversed=reversed,
                minY=minY,plotLines=plotLines, categoriesY=None,plotLinesName=plotLinesName,
                plotBands=None, 
                      plotBandsColor=None
                           )
        return graph

    def drawLineChartMultiXAxis(self,
                        dataY,
                        height=None,
                        addOptions=None,
                        tickInterval=None,
                        tickMinValue=None,
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
                        overMouseAxisX=False,
                        overMouseLabelX=' + this.value + ',
                        showChartClickOnLink=False,
                        typeAxisXScale=None,
                        pointStartLog=None,
                        zoomType='x',
                        marginTop=60,
                        interaction=False,
                        extraArg=None,
                        allowDecimals=None,
                        yAxisType=None,
                        extraScriptButton=None,
                        visible=None,
                        addTable=None,
                        yAxisMulti=None,
                        markerRadius=None,
                        reversed=None,
                        minY=None,
                        plotLines=None,
                        plotLinesName=None,
                        plotBands=None,
                        plotBandsColor=None,
                        xAxisMulti=None
                        ):


        graph = ''

        if len(dataY) > 0:

            tooltipVal = None
            if categories is not None:
                tooltipVal = 'categories'
            if seriesName is not None:
                tooltipVal = 'seriesName'

            data, legendSize, legendSizeExtra = self._parseData(dataY=dataY, type='line', seriesType=seriesType,
                                                                seriesName=seriesName, multiYAxis=False,
                                                                visible=visible, yAxisMulti=yAxisMulti, multiXAxis=True, xAxisMulti=xAxisMulti,
                                                                markerRadius=markerRadius)
            graph = self._draw(
                data, legendSize, legendSizeExtra,
                type='line',
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
                stacking=None,
                shared=shared,
                overMouseAxisX=overMouseAxisX,
                overMouseLabelX=overMouseLabelX,
                showChartClickOnLink=showChartClickOnLink,
                typeAxisXScale=typeAxisXScale,
                pointStartLog=pointStartLog,
                zoomType=zoomType,
                marginTop=marginTop,
                interaction=interaction,
                multiYAxis=False,multiXAxis=True,xAxisMulti=xAxisMulti,
                showInLegend=None,
                extraArg=extraArg,
                allowDecimals=allowDecimals,
                maxY=None,
                yAxisType=yAxisType,
                extraScriptButton=extraScriptButton,
                addTable=addTable,
                histogram=None,
                sortableAccordingToTable=None,
                sortableAccordingToTableDataY=None,
                tableName=None,
                sortableAccordingToTableIndexWithTrackTitle=None,
                plotOptions=None,
                tooltipVal=tooltipVal,
                reversed=False,
                minY=minY, plotLines=plotLines, categoriesY=None, plotLinesName=plotLinesName,
                plotBands=None,
                plotBandsColor=None
            )
        return graph
    
    def drawPieChart(self, dataY, height=None, addOptions=None, 
                     seriesType=None, seriesName=None, showInLegend=True,
                     extraArg='pie', titleText=None, addTable=None
                     ):
        
        graph=''
        
        if len(dataY) > 0:


            tooltipVal=None

            data, legendSize, legendSizeExtra = self._parseData2(dataY=dataY, type = 'pie', seriesType=seriesType, seriesName=seriesName)
            
            type='pie'
            graph = self._draw(
                           data, legendSize, legendSizeExtra, 
                           type=type, 
                           height=height, 
                           addOptions=addOptions,
                           tickInterval=None, 
                           tickMinValue=None,  
                           label='{series.name}', 
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
                           multiYAxis=False,multiXAxis=False,xAxisMulti=None,
                           showInLegend=True,
                           extraArg=extraArg,
                           allowDecimals=None,
                           maxY=None,
                           yAxisType=None,
                           extraScriptButton=None,
                           addTable=addTable,
                           histogram=None,
                           sortableAccordingToTable=None,
                           sortableAccordingToTableDataY=None,
                           tableName = None,
                           sortableAccordingToTableIndexWithTrackTitle=None,
                           plotOptions=None,
                           tooltipVal=tooltipVal, reversed=None, minY=None,plotLines=None, categoriesY=None,plotLinesName=None,
                           plotBands=None, 
                      plotBandsColor=None




                           )
        return graph
    
    def drawColumnCharts(self, 
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
                      overMouseAxisX=False, 
                      overMouseLabelX=' + this.value + ', 
                      showChartClickOnLink=False, 
                      typeAxisXScale=None, 
                      pointStartLog=None,
                      zoomType='x',
                      marginTop=60,
                      interaction=False,
                      extraArg=None,
                      allowDecimals=None,
                      maxY=None,
                      yAxisType=None,
                      extraScriptButton=None,
                      visible=None,
                      addTable=None,
                      histogram=None,
                      sortableAccordingToTable=None,
                      tableName = None,
                      sortableAccordingToTableIndexWithTrackTitle=0,
                      plotOptions=None,
                      minY=None,
                      plotLines=None,
                      plotLinesName=None,
                      plotBands=None, 
                      plotBandsColor=None

                 ):
        
        graph=''
        
        if len(dataY) > 0:
        
            dataYdepth = self._depth(dataY)
            graph=''
            
            if addTable==True:
                if tableName is None:
                    tableName ='resultsTable'
                graph += self.addTable(titleText, tableName=tableName, option=1, indexSpecial=sortableAccordingToTableIndexWithTrackTitle)
            
            if dataYdepth >= 2:          
                for eldY in range(0, len(dataY)):
                    if seriesName is None:
                        sN=None
                    else:
                        sN = seriesName[eldY]
                    
                    if categories is None:
                        cat=None
                    else:
                        cat = categories[eldY]
                    
                    pLine=None
                    if plotLines is None:
                        pLine = None
                    else:
                        pLine = plotLines[eldY]
                        
                    pLineName=None
                    if plotLinesName is None:
                        pLineName = None
                    else:
                        pLineName = plotLinesName[eldY]
                    
                        
                    if titleText is None:
                        tT=None
                    else:
                        if isinstance(titleText, basestring):
                            tT=titleText
                        else:
                            tT=titleText[eldY]
                        
                    graph += self.drawColumnChart(dataY[eldY], height=height, addOptions=addOptions, tickInterval=tickInterval,
                         label=label, lineWidth=lineWidth, titleText=tT, subtitleText=subtitleText, xAxisTitle=xAxisTitle, yAxisTitle=yAxisTitle,
                         categories=cat, seriesType=seriesType, 
                         seriesName=sN, 
                         legend=legend, xAxisRotation=xAxisRotation, dataLabels=dataLabels, 
                         shared=shared, overMouseAxisX=overMouseAxisX, overMouseLabelX=overMouseLabelX, 
                         showChartClickOnLink=showChartClickOnLink, 
                         typeAxisXScale=typeAxisXScale, 
                         pointStartLog=pointStartLog,
                         interaction=interaction,
                         extraArg=extraArg,
                         allowDecimals=allowDecimals,
                         maxY=maxY,
                         yAxisType=yAxisType,
                         extraScriptButton=extraScriptButton,
                         visible=visible,
                         addTable=addTable,
                         histogram=histogram,
                         sortableAccordingToTable=sortableAccordingToTable,
                         sortableAccordingToTableDataY = dataY,
                         tableName =tableName,
                         sortableAccordingToTableIndexWithTrackTitle=sortableAccordingToTableIndexWithTrackTitle,
                         plotOptions=plotOptions, minY=minY, plotLines=pLine, plotLinesName=pLineName,
                         plotBands=None, 
                      plotBandsColor=None
                         )
            else:
                graph += self.drawColumnChart(dataY, height=height, addOptions=addOptions, tickInterval=tickInterval,
                     label=label, lineWidth=lineWidth, titleText=titleText, subtitleText=subtitleText, xAxisTitle=xAxisTitle, yAxisTitle=yAxisTitle,
                     categories=categories, seriesType=seriesType, 
                     seriesName=seriesName, 
                     legend=legend, xAxisRotation=xAxisRotation, dataLabels=dataLabels, 
                     shared=shared, overMouseAxisX=overMouseAxisX, overMouseLabelX=overMouseLabelX, 
                     showChartClickOnLink=showChartClickOnLink, 
                     typeAxisXScale=typeAxisXScale, 
                     pointStartLog=pointStartLog,
                     interaction=interaction,
                     extraArg=extraArg,
                     allowDecimals=allowDecimals,
                     maxY=maxY,
                     yAxisType=yAxisType,
                     extraScriptButton=extraScriptButton,
                     visible=visible,
                     addTable=addTable,
                     histogram=histogram,
                     sortableAccordingToTable=sortableAccordingToTable,
                     sortableAccordingToTableDataY = dataY,
                     tableName =tableName,
                     sortableAccordingToTableIndexWithTrackTitle=sortableAccordingToTableIndexWithTrackTitle,
                     plotOptions=plotOptions, minY=minY, plotLines=plotLines, plotLinesName=plotLinesName,
                     plotBands=None, 
                      plotBandsColor=None
                     )
        return str(graph) + '<div style="clear:both"></div>'
    
    def drawBubbleCharts(self, 
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
                      overMouseAxisX=False, 
                      overMouseLabelX=' + this.value + ', 
                      showChartClickOnLink=False, 
                      typeAxisXScale=None, 
                      pointStartLog=None,
                      zoomType='x',
                      marginTop=60,
                      interaction=False,
                      extraArg=None,
                      allowDecimals=None,
                      maxY=None,
                      yAxisType=None,
                      extraScriptButton=None,
                      visible=None,
                      addTable=None,
                      tableName=None,
                      minY=None,
                      plotLines=None,
                      plotLinesName=None
                 ):
        
        graph=''
        
        if len(dataY) > 0:
        
            dataYdepth = self._depth(dataY)
            graph=''
            
            if addTable==True:
                if tableName is None:
                    tableName ='resultsTable'
                graph += self.addTable(titleText, tableName, option=1)
            
            if dataYdepth >= 2:        
                
                for eldY in range(0, len(dataY)):
                    
                    if seriesName is None:
                        sN=None
                    else:
                        sN = seriesName[eldY]
                    
                    if categories is None:
                        cat=None
                    else:
                        cat = categories[eldY]
                    
                    pLine=None
                    if plotLines is None:
                        pLine = None
                    else:
                        pLine = plotLines[eldY]
                    
                    pLineName=None
                    if plotLinesName is None:
                        pLineName = None
                    else:
                        pLineName = plotLinesName[eldY]
                    
                    
                    if titleText is None:
                        tT=None
                    else:
                        if isinstance(titleText, basestring):
                            tT=titleText
                        else:
                            tT=titleText[eldY]
                    
                        
                    graph += self.drawBubbleChart(dataY[eldY], height=height, addOptions=addOptions, tickInterval=tickInterval,
                         label=label, lineWidth=lineWidth, titleText=tT, subtitleText=subtitleText, xAxisTitle=xAxisTitle, yAxisTitle=yAxisTitle,
                         categories=cat, seriesType=seriesType, 
                         seriesName=sN, 
                         legend=legend, xAxisRotation=0, dataLabels=dataLabels, 
                         shared=shared, overMouseAxisX=overMouseAxisX, overMouseLabelX=overMouseLabelX, 
                         showChartClickOnLink=showChartClickOnLink, 
                         typeAxisXScale=typeAxisXScale, 
                         pointStartLog=pointStartLog,
                         interaction=interaction,
                         extraArg=extraArg,
                         allowDecimals=allowDecimals,
                         maxY=maxY,
                         yAxisType=yAxisType,
                         extraScriptButton=extraScriptButton,
                         visible=visible,
                         addTable=addTable,
                         tableName=tableName,
                         minY=minY,
                         plotLines = pLine,
                         plotLinesName=pLineName
                         )
            else:
                graph += self.drawBubbleChart(dataY, height=height, addOptions=addOptions, tickInterval=tickInterval,
                     label=label, lineWidth=lineWidth, titleText=titleText, subtitleText=subtitleText, xAxisTitle=xAxisTitle, yAxisTitle=yAxisTitle,
                     categories=categories, seriesType=seriesType, 
                     seriesName=seriesName, 
                     legend=legend, xAxisRotation=0, dataLabels=dataLabels, 
                     shared=shared, overMouseAxisX=overMouseAxisX, overMouseLabelX=overMouseLabelX, 
                     showChartClickOnLink=showChartClickOnLink, 
                     typeAxisXScale=typeAxisXScale, 
                     pointStartLog=pointStartLog,
                     interaction=interaction,
                     extraArg=extraArg,
                     allowDecimals=allowDecimals,
                     maxY=maxY,
                     yAxisType=yAxisType,
                     extraScriptButton=extraScriptButton,
                     visible=visible,
                     addTable=addTable,
                     tableName=tableName, minY=minY, plotLines=plotLines, plotLinesName=plotLinesName
                     )
        return str(graph) + '<div style="clear:both"></div>'
    
    def drawPieCharts(self, dataY, height=None, addOptions=None, seriesType=None, 
                      seriesName=None, showInLegend=True, extraArg='pie', titleText=None, addTable=None):
        
        graph=''
        
        if len(dataY) > 0:
            dataYdepth = self._depth(dataY)
            graph=''
            
            
            if dataYdepth >= 2:  
                for eldY in range(0, len(dataY)):
                    if seriesName is not None:
                        sN = seriesName[eldY]
                    else:
                        sN = None
                    
                    graph += self.drawPieChart(dataY[eldY], height=height, addOptions=addOptions, seriesType=seriesType, seriesName=sN, showInLegend=showInLegend, extraArg=extraArg, titleText=titleText, addTable=addTable)
           
        return str(graph) + '<div style="clear:both"></div>'
    
    def drawLineCharts(self, 
                      dataY, 
                      height=None, 
                      addOptions=None,
                      tickInterval=None, 
                      tickMinValue=None, 
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
                      overMouseAxisX=False, 
                      overMouseLabelX=' + this.value + ', 
                      showChartClickOnLink=False, 
                      typeAxisXScale=None, 
                      pointStartLog=None,
                      zoomType='x',
                      marginTop=60,
                      interaction=True,
                      extraArg=None,
                      allowDecimals=None,
                      maxY=None,
                      yAxisType=None,
                      extraScriptButton=None,
                      visible=None,
                      addTable=None, minY=None, plotLines=None, plotLinesName=None,
                      plotBands=None, 
                      plotBandsColor=None
                 ):
        
        graph=''
        
        if len(dataY) > 0:
            dataYdepth = self._depth(dataY)
            graph=''
                    
            numCountList=[]

            print 'dataYdepth' + str(dataYdepth)
            
            if dataYdepth > 2:            
                
                
                
                if interaction==True:
                    self._interactionNumberStart=self.__class__.count
                    self._interactionNumberEnd=len(dataY)
                    graph+= """<button id="btn""" + str(self._interactionNumberStart) +"""" >UNZOOM</button>"""
                    graph += """<style> 
                    #btn""" + str(self._interactionNumberStart) +""" {
                       border-top: 1px solid #96d1f8;
                       background: #65a9d7;
                       background: -webkit-gradient(linear, left top, left bottom, from(#3e779d), to(#65a9d7));
                       background: -webkit-linear-gradient(top, #3e779d, #65a9d7);
                       background: -moz-linear-gradient(top, #3e779d, #65a9d7);
                       background: -ms-linear-gradient(top, #3e779d, #65a9d7);
                       background: -o-linear-gradient(top, #3e779d, #65a9d7);
                       padding: 5px 11px;
                       -webkit-border-radius: 2px;
                       -moz-border-radius: 2px;
                       border-radius: 2px;
                       -webkit-box-shadow: rgba(0,0,0,1) 0 1px 0;
                       -moz-box-shadow: rgba(0,0,0,1) 0 1px 0;
                       box-shadow: rgba(0,0,0,1) 0 1px 0;
                       text-shadow: rgba(0,0,0,.4) 0 1px 0;
                       color: white;
                       font-size: 14px;
                       font-weight:bold;
                       font-family: 'Dosis','sans-serif', 'Lucida Grande', Helvetica, Arial, Sans-Serif;
                       text-decoration: none;
                       vertical-align: middle;
                       cursor:grab;
                    }
                    #btn""" + str(self._interactionNumberStart) +""":hover {
                       border-top-color: #28597a;
                       background: #28597a;
                       color: #ccc;
                    }
                    #btn""" + str(self._interactionNumberStart) +""":active {
                       border-top-color: #1b435e;
                       background: #1b435e;
                    }
                    </style>"""
                    
                for eldY in range(0, len(dataY)):

#                     print 'eldY' + str(eldY) + ' ' + str(dataY[eldY])
                    
                    pLine=None
                    if plotLines is None:
                        pLine = None
                    else:
                        pLine = plotLines[eldY]
                
                    pLineName=None
                    if plotLinesName is None:
                        pLineName = None
                    else:
                        pLineName = plotLinesName[eldY]
                    
                    
                    if interaction == True:
                        numCountList.append(self.__class__.count)
                    
                    graph += self.drawLineChart(dataY[eldY], height=height, addOptions=addOptions, tickInterval=tickInterval, tickMinValue=tickMinValue,
                         label=label, lineWidth=lineWidth, titleText=titleText, subtitleText=subtitleText, xAxisTitle=xAxisTitle, yAxisTitle=yAxisTitle,
                         categories=categories, seriesType=seriesType, 
                         seriesName=seriesName, 
                         legend=legend, xAxisRotation=0, dataLabels=dataLabels, 
                         shared=shared, overMouseAxisX=overMouseAxisX, overMouseLabelX=overMouseLabelX, 
                         showChartClickOnLink=showChartClickOnLink, 
                         typeAxisXScale=typeAxisXScale, 
                         pointStartLog=pointStartLog,
                         interaction=interaction,
                         extraArg=extraArg,
                         allowDecimals=allowDecimals,
                         maxY=maxY,
                         visible=visible,
                         addTable=addTable, minY=minY,plotLines=pLine, plotLinesName=pLineName,
                         plotBands=None, 
                      plotBandsColor=None
                         )
                if interaction == True:
                    graph += self._interactionAmongCharts(numCountList)
                        
            else:
                graph += self.drawLineChart(dataY, height=height, addOptions=addOptions, tickInterval=tickInterval, tickMinValue=tickMinValue, 
                     label=label, lineWidth=lineWidth, titleText=titleText, subtitleText=subtitleText, xAxisTitle=xAxisTitle, yAxisTitle=yAxisTitle,
                     categories=categories, seriesType=seriesType, 
                     seriesName=seriesName, 
                     legend=legend, xAxisRotation=0, dataLabels=dataLabels, 
                     shared=shared, overMouseAxisX=overMouseAxisX, overMouseLabelX=overMouseLabelX, 
                     showChartClickOnLink=showChartClickOnLink, 
                     typeAxisXScale=typeAxisXScale, 
                     pointStartLog=pointStartLog,
                     interaction=interaction,
                     extraArg=extraArg,
                     allowDecimals=allowDecimals,
                     maxY=maxY,
                     visible=visible,
                     addTable=addTable, minY=minY,plotLines=plotLines, plotLinesName=plotLinesName,
                     plotBands=None, 
                      plotBandsColor=None
                     )
        return str(graph) + '<div style="clear:both"></div>'
    
    def visualizeResults(self, result, htmlCore=None):
        
        if htmlCore is None:
            htmlCore = HtmlCore()
        
        htmlCore.line(str(self._addGuideline(htmlCore)))
        htmlCore.begin()
        htmlCore.divBegin('plot')
        htmlCore.line(result)
        htmlCore.divEnd()
        htmlCore.end()
        return str(htmlCore)

#input: data 
class dataTransformer(object):
    
    def __init__(self, results):
        self._results = results
    
    def changeDictIntoList(self):
        categories = self._results.keys()
        data = self._results.values()
        
        for elD in range(0, len(data)):
            if isinstance(data[elD], basestring):
                data[elD] = "".join(i for i in data[elD] if i in "0123456789.")

        return None, categories, data
    
    def changeDictIntoListsByNumber(self, number=None):
        categories = self._results.keys()
        data = self._results.values()
        
        
        if number is not None:
            number = int(number)
            dataList = [data[x:x+number] for x in xrange(0, len(data), number)]
            categoriesList = [categories[x:x+number] for x in xrange(0, len(categories), number)]
        else:
            return None, None, None
        
        return None, categoriesList, dataList
    
    
    def changeDictIntoListByTrackString(self, strNum = "" , numStart=1, numEnd=0): 
        
        seriesName=[]
        categories=[]
        data=[]
        
        
        for elD in range(numStart, numEnd+1):
            elDTF=False
            strD = strNum+str(elD)
            for key, item in self._results.iteritems():
                if strD in key:
                    elDTF=True
                    categories.append(key)
                    data.append(item)
            if elDTF==True:
                seriesName.append([strD])
        
        return seriesName, categories, data
    
    def changeDictIntoListsByTrackString(self, strNum = "" , numStart=1, numEnd=0): 
        
        seriesName=[]
        categories=[]
        data=[]
        
        for elD in range(numStart, numEnd+1):
            categoriesPart=[]
            dataPart=[]
            elDTF=False
            strD = strNum+str(elD)
            for key, item in self._results.iteritems():
                if strD in key:
                    elDTF=True
                    categoriesPart.append(key)
                    dataPart.append(item)
            if elDTF==True:
                seriesName.append([strD])
            categories.append(categoriesPart)
            data.append(dataPart)
        
        return seriesName, categories, data
    
    def changeDictIntoListsByLevel(self):
        categories = self._results.keys()
        data = self._results.values()
        
        newCategories=[]
        newData=[]
        
        for elD in range(0, len(data)):
            if isinstance(data[elD], basestring):
                data[elD] = "".join(i for i in data[elD] if i in "0123456789.")
              
        if categories:
            for tNum in range(1,len(map(int,str(categories[0])))):
                newCategoriesPart=[]
                newDataPart=[]
                for catNum in range(0, len(categories)):
                    if sum(map(int,str(categories[catNum]))) == tNum:
                        newCategoriesPart.append(categories[catNum])
                        newDataPart.append(data[catNum])
                newCategories.append(newCategoriesPart)
                newData.append(newDataPart)
        
        
        return None, newCategories, newData
        
        
        
class plotFunction(object):
    
    def __init__(self, tableId):
        self._tableId = tableId
        
    def createButton(self, bText):
        return """<button type="button" id='bID'>""" + str(bText) + """</button>"""
        
    def hideColumns(self, indexList):
        
        return """
        
        <script>
        
        indexList = """ + str(indexList) + """;
        lenIndexList = """ + str(len(indexList)) + """;
        thLen = document.getElementById('""" + str(self._tableId) + """').getElementsByTagName("th").length;
        tdLen = document.getElementById('""" + str(self._tableId) + """').getElementsByTagName("td").length;
        trLen = document.getElementById('""" + str(self._tableId) + """').getElementsByTagName("tr").length;
        
        console.log('trLen', trLen);
        
        var jqnc = jQuery.noConflict();
        
        jqnc(document).ready(function() {
        
        for(var i=0; i<lenIndexList; i++)
        {
            for(var j=0; j < trLen; j++)
            {
                divid = '#hidethis-'+indexList[i]+'-'+j;
                jqnc(divid).hide();
            }
        }
        
        jqnc('#bID').on('click',function(e) 
        {
            for(var i=0; i<lenIndexList; i++)
            {
                for(var j=0; j < trLen; j++)
                {
                    divid = '#hidethis-'+indexList[i]+'-'+j;
                    jqnc(divid).slideToggle("fast");
                }
            }
        });
        
        
        });
        
        //console.log(document.getElementById('""" + str(self._tableId) + """').getElementsByTagName("td"), document.getElementById('""" + str(self._tableId) + """').getElementsByTagName("td").length);
        
        
        for (var j=0; j < lenIndexList; j++)
        {
            document.getElementById('""" + str(self._tableId) + """').getElementsByTagName("th")[indexList[j]].id = 'hidethis-'+indexList[j]+'-0'; 
            document.getElementById('""" + str(self._tableId) + """').getElementsByTagName("th")[indexList[j]].style.color ='#545C6A';
        }
        
        var nr=-1;
        var nrJ=-1;
        for(var i=0; i<lenIndexList; i++)//
        {
            for (var j=0; j < trLen-1; j++)//rows
            {
                //console.log(indexList[i], thLen*j, indexList[i] + thLen*j);
                
                nr = indexList[i] + thLen*j;
                nrJ=j+1;
                
                //console.log('nr', nr, nrJ);
                
                document.getElementById('""" + str(self._tableId) + """').getElementsByTagName("td")[nr].id = 'hidethis-'+indexList[i]+'-'+nrJ; 
            }
        }
        
        </script>
        
        
        """

