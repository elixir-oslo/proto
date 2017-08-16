htmlMal = '''
<html>
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <base href="https://hyperbrowser.uio.no/gsuite/" />
<style>
body{ font-family:Arial, Helvetica, sans-serif;}
</style>

        <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
        
        <!-- debug content -->
        <!--script type="text/javascript" src="jquery.venny_hbmod.js"></script-->
        <!--script type="text/javascript" src="vennydict.js"></script>
        <script language="Javascript">
        var series = testseries //included in vennydict.js
        var catInfo = testcatInfo
        </script-->



        <script type="text/javascript" src="static/hyperbrowser/files/jsscripts/jquery.venny_hbmod.js"></script>
        <script language="Javascript">
        
        
        var series = { name: {%s}, data: {%s} };
        var catInfo = %s    
       
// debug        
/*        var series = { name: {A:'Gene regulation:Transcription factor regulation:Experimentally determined (ChIP-seq peaks):wgEncodeAwgTfbsUniform:AG04449:CTCF:UW-None-std-wgEncodeEH000928', B:'Gene regulation:Transcription factor regulation:Experimentally determined (ChIP-seq peaks):wgEncodeAwgTfbsUniform:A549:ATF3:HudsonAlpha-EtOH_0.02pct-SL6021', C:'Gene regulation:Transcription factor regulation:Experimentally determined (ChIP-seq peaks):wgEncodeAwgTfbsUniform:BE2_C:CTCF:UW-None-std-wgEncodeEH001892', D:'Gene regulation:Transcription factor regulation:Experimentally determined (ChIP-seq peaks):wgEncodeAwgTfbsUniform:GM12801:CTCF:UW-None-std-wgEncodeEH000456'}, data: {A: 2248772, B: 2679490, C: 8060894, D: 62657, AB: 56133, AC: 5540277, AD: 4834, BC: 85561, BD: 3081, CD: 174775, ABC: 123228, ABD: 242, ACD: 408504, BCD: 12417, ABCD: 36942} };
        var catInfo = {"Gene regulation:Transcription factor regulation:Experimentally determined (ChIP-seq peaks):wgEncodeAwgTfbsUniform:AG04449:CTCF:UW-None-std-wgEncodeEH000928": {"prime": 2, "fullTrackName": "Gene regulation:Transcription factor regulation:Experimentally determined (ChIP-seq peaks):wgEncodeAwgTfbsUniform:AG04449:CTCF:UW-None-std-wgEncodeEH000928", "selection": "in", "label": "A"}, "Gene regulation:Transcription factor regulation:Experimentally determined (ChIP-seq peaks):wgEncodeAwgTfbsUniform:BE2_C:CTCF:UW-None-std-wgEncodeEH001892": {"prime": 5, "fullTrackName": "Gene regulation:Transcription factor regulation:Experimentally determined (ChIP-seq peaks):wgEncodeAwgTfbsUniform:BE2_C:CTCF:UW-None-std-wgEncodeEH001892", "selection": "in", "label": "C"}, "Gene regulation:Transcription factor regulation:Experimentally determined (ChIP-seq peaks):wgEncodeAwgTfbsUniform:GM12801:CTCF:UW-None-std-wgEncodeEH000456": {"prime": 7, "fullTrackName": "Gene regulation:Transcription factor regulation:Experimentally determined (ChIP-seq peaks):wgEncodeAwgTfbsUniform:GM12801:CTCF:UW-None-std-wgEncodeEH000456", "selection": "in", "label": "D"}, "Gene regulation:Transcription factor regulation:Experimentally determined (ChIP-seq peaks):wgEncodeAwgTfbsUniform:A549:ATF3:HudsonAlpha-EtOH_0.02pct-SL6021": {"prime": 3, "fullTrackName": "Gene regulation:Transcription factor regulation:Experimentally determined (ChIP-seq peaks):wgEncodeAwgTfbsUniform:A549:ATF3:HudsonAlpha-EtOH_0.02pct-SL6021", "selection": "in", "label": "B"}}    
        var debugrun = true
  */           
    
       
        if ('' in series.data) // remove empty state, ie where no category covers.
            delete series.data['']
        
        
        // remove common start of track in visualization.
        var tmp=new Array()
        for(key in series.name)
            tmp.push(series.name[key])
        var catprefix = ''
        if(tmp.length > 1) 
        {
            catprefix = sharedStart(tmp)
            if(catprefix.length && catprefix.lastIndexOf(':')!=-1) // only erase prefixes that are trackname parts (:)
            {
                catprefix = catprefix.substring(0 , catprefix.lastIndexOf(':')+1) 
                for(key in series.name)
                    series.name[key]=series.name[key].substring(catprefix.length)
                }
        }
        //found http://stackoverflow.com/questions/1916218/find-the-longest-common-starting-substring-in-a-set-of-strings
        function sharedStart(array)
        {
            var A= array.slice(0).sort();
            var word1= A[0];
            var word2= A[A.length-1];
            var i= 0;
            if(word1==word2) return(word1);
            while(word1.charAt(i)== word2.charAt(i))++i;
            return word1.substring(0, i);
        }
        
        // temp vars to remember last users selection regarding 'ignore' or not.    
        var selectedseries = series
        var lastignoredstring=''
                            

     /*
         Make table with form elements based on the series.
         Update (i.e. draw venn if 5 or less categories.)
     */
     function makecontent()
     {
         
         var categorycoverage = calccategorycoverage(series)
         var catcount = Object.keys(series.name).length 
         var ret =''
         for(var i=0;i<catcount;i++)
         {
             var thiskey = Object.keys(series.name)[i]
             var radiostring = ''            
              radiostring  = '<td><input type="radio" name="' + thiskey + '" id="' + thiskey + 'in"     value="in"      onclick="updatecount()"   checked/></td>'
              radiostring += '<td><input type="radio" name="' + thiskey + '" id="' + thiskey + 'out"    value="out"    onclick="updatecount()"          /></td>'
              radiostring += '<td><input type="radio" name="' + thiskey + '" id="' + thiskey + 'ignore" value="ignore" onclick="updatecount()"          /></td>'
             ret += '<tr>'+radiostring+'</td>'
             ret += '<td><input type="text" size="100" id="name_'+thiskey+'" value="'+series.name[thiskey]+'" onchange="updatecount()"/>'
             //ret += '<input type="hidden" name="fullpathname_'+thiskey+'" value="'+catInfo[thiskey]['fullTrackName']+'" /></td>'
             ret += '<td>'+categorycoverage[thiskey]+'</td></tr>'

         }        
         document.getElementById("selecttable").innerHTML = document.getElementById("selecttable").innerHTML+ret
         if(catprefix.length>0)
             document.getElementById("catprefix").innerHTML = ' ( from '+catprefix + ' ) '
         
         updatecount()

     }
     
     /*
         Count the total base pairs in each category. Done once initially and presented in table.
     */
     function calccategorycoverage(thisseries)
     {     
         var ret = {};         
         for(var thisname in thisseries.name)
             ret[thisname]=0
         for(var key in thisseries.data)
         {             
             for (var i = 0; i < key.length; i++)
                 ret[key[i]] += thisseries.data[key]
         }
         return(ret)         
     }
     
     /*
         Main function run each time input user input changes.
         Counts the numer of base pairs that complies to the selected categories.
         Draw the venn diagram if 5 or less categories are used.
     */
     function updatecount()
     {         
         var inarray = getselected('in')
         var outarray= getselected('out')
         var ignorearray = getselected('ignore')

         if(lastignoredstring != ignorearray.join(''))
         {
             selectedseries = createnewseries(ignorearray)
         }
         lastignoredstring = ignorearray.join('')
         
         setselectioncover(selectedseries.data[inarray.join('')], (inarray.length+outarray.length))
  
        if( Object.keys(selectedseries.name).length==0)
        {
            document.getElementById("vennplot").innerHTML = 'Need at least 1 category for drawing Venn-diagram (max 5).'
        }
        else if(Object.keys(selectedseries.name).length >5)
        {
            document.getElementById("vennplot").innerHTML = 'Too many categories for drawing Venn-diagram (max 5).'
        }
         else
         {             
             var vennysafeseries = translatekeys(selectedseries, ignorearray)            
            // The venny function call with an unfamiliar syntax, but seems to work.
                 $(document).ready(function(){
                  $('#vennplot').venny({
            series: [vennysafeseries],
            disableClick: false,
            fnClickCallback: function()
                        {
                            
                            vennselectionclick(this.keysin, this.keysout)
                            
                        }
              });
            });

        }

  
     }
     
     function setselectioncover(coveragecount, tracksused)
     {
         document.getElementById("counttext").innerHTML = 'Base pairs covered by selection: <b style="font-size:xx-large;">' + coveragecount + '</b>, ' +tracksused + ' tracks used.' 
     }
     
     // sets the radiobuttons according to user selection (clicked on Venn)
     function vennselectionclick(keysin, keysout)
     {
         var thistranslatedict = gettranslatedict(getselected('ignore'), 'venny2org')
         orgin = translatekey(keysin.join(''), thistranslatedict)
         orgout = translatekey(keysout.join(''), thistranslatedict)
         for(ind in keysin)
             document.getElementById(orgin[ind]+'in').checked=true
         for(ind in keysout)
             document.getElementById(orgout[ind]+'out').checked=true
         setselectioncover(selectedseries.data[orgin], (keysin.length+keysout.length))         
     }
     
     
     function createhistoryofseleection()
     {
         if (! (parent.frames && parent.frames.galaxy_history) )
         {
             if( typeof debugrun === 'undefined')
             {
                 alert("Need to be inside HyperBrowser to submit a job to history.")
                 return(false)
             }
          }
        //http://hyperbrowser.uio.no/gsuite/tool_runner?tool_id=create_combination_track&runtool_btn=yes&input=test&dbkey=hg19
                 
         var selection = {}
         //for(key in series.name)
         for(key in catInfo)
         {
             //alert('Key='+key)
             //alert('series.name[key]='+series.name[key])
             //alert(json.stringinfy(catInfo[series.name[key]]))
             var thislabel = catInfo[key]['label']
             catInfo[key]['selection'] =  document.querySelector('input[name="'+thislabel+'"]:checked').value
             //selection[key] = document.querySelector('input[name="'+key+'"]:checked').value
         }
         
         //var inputobject = {'catInfo':catInfo , 'selection':selection}
         var inputobject = {'catInfo': catInfo }
         //var inputobject = { 'selection':selection}
         var jsonstring = JSON.stringify(inputobject)
         var b64input =  btoa(jsonstring)
         
         document.getElementById("dummyinput").value=b64input
         document.getElementById("dummycatselectform").submit();
        window.setTimeout(refreshhistory,3000)
    }
     
     function refreshhistory()
     {
         parent.frames.galaxy_history.location.reload(true);
     }
     /*
     function sendselectiontotool(urlstring)
     {
         document.getElementById("dummyinput").value=urlstring
         document.getElementById("dummycatselectform").submit();
         
        document.getElementById("debug").innerHTML += '<br/><br/><br/>Test url ='+urlstring+'=<br/>'
         document.getElementById("debug").innerHTML += '<a href="'+urlstring+'">testlink</a>' 
         
         }
         */     

      
     
     
     function translatekey(keystring, translatedict)
     {
         var ret=''
         for(var i=0;i<keystring.length;i++)
            ret+=translatedict[keystring[i]]
        return(ret)
     }
         
     /*
         Workaround since venny needed a series without missing letters in the keys.(must have ABC and not ADE as it will be if BC are ignored.)
         Runs through all the keys and swap letters so they are A,B,C for name and data.
         This function can for sure be made quicker. Or not needed at all if venny was smarter.
     */     
     function translatekeys(unsafeseries,ignore)
     {
         var newseries = { name:{}, data:{}}
        translatedict = gettranslatedict(ignore , 'org2venny')
        for(var key in unsafeseries.name)
        {
            var elmid = 'name_'+key
            newseries.name[translatedict[key]] = document.getElementById(elmid).value
        }
            
         for(var key in unsafeseries.data)
        {
            var safekey=translatekey(key, translatedict)                
            newseries.data[safekey] = unsafeseries.data[key]            
        }
        return(newseries)
     }
     
     function gettranslatedict(ignore, direction)
     {
         var matchstring = RegExp('['+ignore.join('')+']', 'g')
         var includedkeys = Object.keys(series.name).join('')
         includedkeys = includedkeys.replace(matchstring,'')
         var allowedkeys = Object.keys(series.name).join('').substring(0,includedkeys.length)
         translatedict = {}
         
        for(var i=0;i<includedkeys.length;i++)
            if(direction=='org2venny')
                translatedict[includedkeys[i]] = allowedkeys[i]
            else if(direction=='venny2org')
                translatedict[allowedkeys[i]] = includedkeys[i]
            else
                alert('error in gettranslatedict')
                
        return(translatedict)
     }
     
     /*
         Creates a new series object where the ignored categories are taken out and all data with a ignored category in the key is added to the corresponding key without the ignored.
         Example: original set: ABC:50, AB:25    new set: AC:75 (50+25), if B is ignored.
     */
     function createnewseries(ignore)
     {
         var newseries = { name:{}, data:{}}
         for(var key in series.name)
        {
            if(ignore.indexOf(key)==-1)
                newseries.name[key] = series.name[key]        
        }
         var matchstring = RegExp('['+ignore.join('')+']', 'g')
         for(var key in series.data)
        {
            var newkey = key.replace(matchstring,'')
            if(newkey != '')
            {
                if(!(newkey in newseries.data))
                    newseries.data[newkey] = 0
                newseries.data[newkey] += series.data[key]
            }
            
        }
         return(newseries)
     }     
     /*
         Returns list with keys that have val selected (val ={'in','out','ignored'})
     */
     function getselected(val)
     {
         var ret = new Array();
         for(var catname in series.name)
         {
             if(document.querySelector('input[name="'+catname+'"]:checked').value==val)
                 ret.push(catname)
         }
        return(ret)
     }
     
     function setallcat(val)
     {
         for(var catname in series.name)
         {
             elmid = catname+val
             document.getElementById(elmid).checked=true
         }
         updatecount()
     }
   
    </script>
    </head>

    
    <body onload="makecontent()">
    <style>
    table#selecttable {
    border-top: solid #CC9E00 1px;
    border-bottom: solid #CC9E00 1px;
    border-collapse: collapse;
    }
    
    table#selecttable tr.header, table#selecttable th.header {
        background: #726e6d;
        background-repeat: repeat-x;
        background-size: auto 100%%;
        background-position: top;
        border-bottom: solid #CC9E00 1px;
        font-weight: bold;
        color: #fffff1;
    }
    table#selecttable a{
        color: #fffff1;
    }
    table#selecttable tr {
        background: white;
    }
    table#selecttable td, table#selecttable th {
        text-align: left;
        padding: 5px;
        border: solid #CC9E00 1px;
    }
    div.results-section {
        padding: 10px;
        margin: 5px 5px 30px 5px;
        background-color: #fffff1;
        border: 1px dotted #323232;
    }
    #results-page {
        background-color: #EAE6D8;
        color: #1e1d1b;
        padding: 10px 0px;
        min-width: 99%%;
        min-height: 100%%;
        position: absolute;
    }
    #results-page h3 {
        text-transform: uppercase;
        color: #707EA1;
        border-bottom: 2px solid #707EA1;
        padding-bottom: 5px;
        padding-top: 10px;
    }
    </style>
        <div id="results-page">
        <div class="results-section">
        <h3>Base pair overlap for tracks/categories</h3>
        <form id="catselectform" name="catselectform" action="tool_runner" method="post" target="tooloutput">
            <table id="selecttable" >
                <tr>
                    <th class="header"><a href="javascript:setallcat('in')">In</a></th><th class="header" ><a href="javascript:setallcat('out')">Out</a></th><th class="header"><a href="javascript:setallcat('ignore')">Ignore</a></th>
                    <th class="header" width="300">Category <i id="catprefix"></i></th>
                    <th class="header">Base pairs in track</th>
                </tr>
            </table>
        <table style="border: 0px solid black;padding:4px" style="vertical-align:bottom"><tr><td>            
        <div style="float:left;" id="counttext"></div> &nbsp;&nbsp;&nbsp;&nbsp;
        <input id="sendselectionbutton" type="button" height="40" value="Create history track of regions in selection" onclick="createhistoryofseleection()" style="font-size: 16px;padding: 5px;" />
        </td></tr></table>
        
        </div>
        </form>
        <br/>
        <br/>
        <div class="container" style="width:700px;height:500px;margin: 0 auto">
            <div id="vennplot"> . </div>
        </div>    
        <!--img id="canvasImg" alt="Right click to save me!"/-->
        <div id="historyframe">
            <iframe id="tooloutput" name="tooloutput" style="width:800px;height:400px;border:none;"><br/></iframe>
        </div>
        <br/>
        <form id="dummycatselectform" name="dummycatselectform" action="tool_runner" method="post" target="tooloutput">
        <input type="hidden" name="tool_id" value="create_combination_track"/>
        <input type="hidden" name="runtool_btn" value="yes"/>
        <input type="hidden" name="dbkey" value="%s"/>
        <input type="hidden" id="dummyinput" name="input" value="NOT_SET"/>
        </form>
        <p id="debug">%s</p>
        </div>
        </div>
    </body>
</html>




'''



