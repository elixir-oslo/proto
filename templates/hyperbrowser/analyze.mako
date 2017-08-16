<%!
import sys
from cgi import escape
from urllib import quote, unquote

import proto.hyperbrowser.hyper_gui as gui

%>
<%
#print context.get('self')
#reload(hyper)

#print dir(trans.webapp)
#print trans.app.config.root
#print dir(trans.response.cookies)

galaxy = gui.GalaxyWrapper(trans)

#trans.response.cookies['test'] = 'test'
#print trans.response.cookies.js_output()
#print trans.response.cookies.values()

#trans.sa_session.save(cookies)

params = galaxy.params

genomes = [('----- Select -----', '', False)]
genomes += hyper.getAllGenomes(galaxy.getUserName())
#genomes.append(('----- Select -----', '', True))

genome = params.get('dbkey', genomes[0][1])

params['dbkey'] = genome
genomeElement = gui.SelectElement('dbkey', genomes, genome)
genomeElement.onChange = "resetAll();" + genomeElement.onChange 

username = None
datasets = []
try:
#    if galaxy.trans.galaxy_session_is_valid():
    datasets = galaxy.getHistory(hyper.getSupportedGalaxyFileFormats())
    username = galaxy.getUserName()
except:
    pass

formAction = '?'
demoID = params.get('demoID')

tracks = [None] * 3
catsElement = None
valid = ''
job_name, job_info = ('', '')

if hyper.isAccessibleGenome(genome, username):
    tracks[0] = gui.TrackWrapper('track1', hyper, [], galaxy, datasets, genome)
    tracks[0].fetchTracks()
    tracks[0].legend = 'First Track'
    
    tracks[1] = gui.TrackWrapper('track2', hyper, [('-- No track (single track analysis) --', '', True)], galaxy, datasets, genome)
    tracks[1].fetchTracks()
    tracks[1].legend = 'Second Track'    
    
    tracks[2] = gui.TrackWrapper('trackIntensity', hyper, [('-- No intensity track --', '', False)], galaxy, datasets, genome)
    tracks[2].fetchTracks()
    tracks[2].legend = 'Intensity Track (when needed)'
    show_intensity_track = False
    
    stats = params.get('stats', '')
    _stats = params.get('_stats')
    
    analysisTitle = params.get('analysis')
    if analysisTitle and not _stats:
        _stats = hyper.getValidAnalysisDefFromTitle(analysisTitle, genome, tracks[0].definition(), tracks[1].definition())
        print 'getValidAnalysisDefFromTitle( %s ) = %s' % (analysisTitle, _stats)
    
    _stats_text = params.get('_stats_text')
    region = params.get('region', '*')
    binsize = params.get('binsize', '1m')
    chrspec = params.get('chrspec', '*')
    method = params.get('method', '__chrs__')
    
    configOptions = None
    description = None
    
    if _stats:
        configOptions = hyper.getConfigOptions(_stats)
        trackTypeOptions = hyper.getTrackTypeOptions(_stats)
    
        if analysisTitle:
            optDict = {}
            for opt in configOptions[0]:
                val = params.get('config_' + opt)
                optDict[opt] = (val) if val else configOptions[1][opt][0]
            for opt in trackTypeOptions[0]:
                val = params.get('config_' + opt)
                optDict[opt] = (val) if val else trackTypeOptions[1][opt][0]
            stats = quote(hyper.setConfigChoices(_stats, optDict))
    
        if stats:
            valid = hyper.runValid(tracks[0].definition(), tracks[1].definition(), stats, region, binsize, genome, tracks[2].definition())
            if valid == True:
                formAction = h.url_for('/tool_runner')
                description = hyper.getRunDescription(tracks[0].definition(), tracks[1].definition(), stats, region, binsize, genome, username, tracks[2].definition())
    
                job_name, job_info = hyper.getRunNameAndDescription(tracks[0].definition(), tracks[1].definition(), stats, region, binsize, genome)
    
    statOptions = None
    
    imgURL = None
    analcat = params.get('analcat')

    #print 'xx:', tracks[0].valueLevel(0)
    if tracks[0].selected() and tracks[1].selected():
    #        if analcat == 'R':
    #            statOptions = []
        analCats = []
        statCatOptions = {}
        
        #if tracks[0].selected() and tracks[1].selected():
        _analCats = hyper.getAnalysisCategories(genome, tracks[0].definition(), tracks[1].definition())
        if _analCats and len(_analCats) > 0:
            for cat in _analCats:
                analList = hyper.getAnalysisList(genome, cat[1], tracks[0].definition(), tracks[1].definition(), tracks[0].getState(False), tracks[1].getState(False))
                #print analList
                # discard empty categories
                if analList and len(analList) > 0:
                    statCatOptions[cat[1]] = analList
                    analCats.append(cat)
                    
                    # set category if not supplied in link
                    if analysisTitle and not analcat:
                        for a in analList:
                            if a[1] == _stats:
                                analcat = cat[1]
                    
        rscripts = galaxy.getHistory(['R'])
        if len(rscripts) > 0 and tracks[0].selected() and tracks[1].selected():
            analCats.append(('Custom R-scripts', 'R', False))
            
            statCatOptions['R'] = gui.optionListFromDatasets(rscripts)
            
        if len(analCats) > 0:
            if not analcat or not statCatOptions.has_key(analcat):
                analcat = analCats[0][1]
            catsElement = gui.SelectElement('analcat', analCats, analcat)
            catsElement.onChange = "this.form.stats.value='';" + catsElement.onChange
    
            if analcat:
                #statOptions = hyper.getAnalysisList(genome, analcat, tracks[0].definition(), tracks[1].definition())
                statOptions = statCatOptions[analcat]
                #_stats_text = unquote(stats) if stats else ''
                ok = False
                for opt in statOptions:
                    if _stats == opt[1]:
                        ok = True
                        break
                if not ok:
                    stats = None
                    _stats = None
                    _stats_text = ''
                else:
                    if stats:
                        if stats.startswith('galaxy'):
                            _stats_text = ''
                        else:
                            _stats_text = hyper.getTextFromAnalysisDef(stats, genome, tracks[0].definition(), tracks[1].definition())
                            imgURL= hyper.getIllustrationRelURL(stats)
%>

<%namespace name="functions" file="/hyperbrowser/functions.mako" />
<%inherit file="base.mako"/>

<%def name="title()">The Genomic HyperBrowser (${hyper.getHbVersion()})</%def>
<%def name="head()">
    <script type="text/javascript">    	    
	//if (window == top && document.referrer.indexOf('hyperbrowser.uio.no') == -1) location.href = "${h.url_for('/')}";
        <%include file="common.js"/>        
    </script>
</%def>


<form name="form" id="form" method="post" action="${formAction}">
%if demoID:
    ${hyper.getDemoAnalysisIntro(demoID)}
    <INPUT TYPE="HIDDEN" NAME="demoID" VALUE="${demoID}">
%endif

<div class="genome">
##    Genome build: ${genomeElement.getHTML()}  ${genomeElement.getScript()}
    ${functions.genomeChooser(galaxy, genomeElement, genome)}
</div>

<div style="clear:both;height:0"></div>

%if tracks[0] and tracks[1]:
    ${functions.trackChooser(tracks[0], 0, params)} 
    ${functions.trackChooser(tracks[1], 1, params)} 
%endif

%if catsElement:
<fieldset><legend>Analysis</legend>

        <label>Category: ${catsElement.getHTML()}</label>
        ${catsElement.getScript()}

        %if statOptions and len(statOptions) > 0:

            %if True:
            <select id="_stats" name="_stats" onchange="$('#stats').val($(this).val());reloadForm(this.form, this);">
                <option value=""> --- Select --- </option>
                    <% in_optgroup = False %>
                    %for stat in statOptions:
                        %if stat[2]:
                            %if in_optgroup:
                                </optgroup>
                            %endif
                            <optgroup label="${stat[0]}">
                            <% in_optgroup = True %>
                        %else:
                            <option value="${stat[1]}" ${gui.selected(stat[1], _stats)}>${stat[0].split(':')[0] if analcat != 'R' else stat[0]}</option>
                        %endif
                    %endfor
            </select>
            ${self.help('analysis')}
            %if _stats_text:
                <p id="_stats_text" class="infomessagesmall explanation">${_stats_text}
            %endif
            %if imgURL:
            <p><img width="100%" src="${imgURL}" style="max-width: 640px; width: expression(this.width > 640 ? 640: true);"></p>
            %endif
            </p>
            <!-- ${unquote(stats) if stats else ''} -->

            %else:
        <input id="_stats_button" type="button" onclick="optionsToggle('_stats')" value="Select option">
            <div id="_stats_display" onclick="optionsToggle('_stats')"><b>${_stats_text}</b></div>
            <div id="_stats_options" class="options" style="${'display:block' if not _stats else 'display:none'}">
                    %for stat in statOptions:
                <a href="javascript:;" class="${gui.selected(stat[1], _stats)} option" rev="${stat[1]}" rel="_stats">${stat[0]}</a>
                <!-- <label><input class="option" type="radio" ${gui.checked(stat[1], _stats)} value="${stat[1]}" name="_stats">${stat[0]}</label> -->
                    %endfor
            </div>
            <input id="_stats" name="_stats" type="hidden" value="${_stats if _stats else ''}" on_select="$('#stats').val($('#_stats').val());">
            <input id="_stats_text" name="_stats_text" type="hidden" value="${_stats_text if _stats_text else ''}">
            %endif


        %endif
        <p></p>

        %if _stats and trackTypeOptions and len(trackTypeOptions[0]):
            <fieldset><legend>Track type</legend>                
            %for opt in trackTypeOptions[0]:
                <div style="margin-bottom:4px"><label>${opt}: <select name="config_${quote(opt)}" onchange="setConfigChoices(form)">
                    %for val in trackTypeOptions[1][opt]:
                        <option value="${quote(val)}" ${gui.selected(quote(val), params.get('config_'+quote(opt)))}>${val}</option>
                        <%
                            if val.find('intensity') > -1:
                                show_intensity_track = True
                        %>
                    %endfor
                    </select>
                </label></div>
            %endfor
            ${self.help('trackType')}
            </fieldset>
        %endif


        %if _stats and configOptions and len(configOptions[0]):
            <fieldset><legend>Options</legend>
            <%
                hasMcFdr = False
            %>
            %for opt in configOptions[0]:
                <div style="margin-bottom:4px"><label>${opt}: <select name="config_${quote(opt)}" onchange="setConfigChoices(form)">
                    <%
                        in_val = params.get('config_'+opt)
                        if in_val == None:
                            in_val = params.get('config_'+quote(opt))
                        else:
                            in_val = quote(in_val)
                    %>
                    %for val in configOptions[1][opt]:
                        <option value="${quote(val)}" ${gui.selected(quote(val), in_val)}>${val}</option>
                        <%
                            if val.find('intensity') > -1:
                                show_intensity_track = True
                        %>
                    %endfor
                    </select>
                </label></div>
                %if 'Null model' in opt:
                    <p><a href="#help_null_model" title="Help" onclick="getHelp('null_model')">What is a null model?</a>
                       <div id="help_null_model" class="infomessagesmall help"></div></p>
                %endif
                <%
                    if 'MCFDR' in opt:
                        hasMcFdr = True
                %>
            %endfor
            %if hasMcFdr:
                <p><a href="#help_mcfdr" title="Help" onclick="getHelp('mcfdr')">What do the MCFDR options mean?</a>
                   <div id="help_mcfdr" class="infomessagesmall help"></div></p>
            %endif
            ${self.help('options')}
            </fieldset>
        %endif

    <input id="stats" name="stats" type="hidden" value="${stats if stats else ''}">
        
    <div style="text-align:right">
    <a href="#" onclick="this.href='mailto:'+ 'on.oiu.tisu@stseuqer-resworbrepyh'.split('').reverse().join('')+
        '?subject=Request new analysis'" class="codedirection">Did you not find your question here?</a>
    </div>
        
</fieldset>

    %if stats:

        %if show_intensity_track:
            ${functions.trackChooser(tracks[2], 2, params, False)}
        %endif

        <a name="region_scale"></a>
        <fieldset><legend>Region and scale</legend>
            <%include file="binoptions.mako" args="galaxy=galaxy,gui=gui,hyper=hyper,genome=genome,track1=tracks[0],track2=tracks[1],category=analcat"/>
                    ${self.help('binning')}        
        </fieldset>

        <p id="status" class="errormessagesmall" style="display:${'block' if valid != True else 'none'}">${valid if valid != True else ''}</p>
    
            <%
            srd_val = params.get('showrundescription', '0')
            if srd_val == '1':
                srd_class = 'hideInfo'
                srd_display = ''
            else:
                srd_class = 'showInfo'
                srd_display = 'display:none'
            %>
        <input type="hidden" name="showrundescription" id="showrundescription" value="${srd_val}">
        %if description:
##          <img class="${srd_class}" src="${h.url_for('/static/style/info_small.png')}" alt="Run description" title="Run description" onclick="getRunDescription(document.forms[0], this, '#rundescription')"/>
            <a style="vertical-align: top" class="${srd_class} run_description_link" href="#" onclick="getRunDescription(document.forms[0], this, '#rundescription'); return false;">Inspect parameters of the analysis</a>
            <img id="gettingrundescription" style="display:none; vertical-align: bottom;" src="${h.url_for('/static/images/loading_small_white_bg.gif')}">
        <div id="rundescription" class="infomessagesmall" style="${srd_display}">${description if description else ''}</div>
        %endif

    %endif #stats
%endif #has categories

<p><input id="start" type="submit" value="Start analysis" ${gui._disabled(valid, True)}>
<span id="validating" style="display:none">Validating...<img src="${h.url_for('/static/images/loading_small_white_bg.gif')}"></span></p>

    <INPUT TYPE="HIDDEN" NAME="tool_id" VALUE="hb_test_1">
    <INPUT TYPE="HIDDEN" NAME="URL" VALUE="http://dummy">

    <INPUT TYPE="HIDDEN" ID="job_name" NAME="job_name" VALUE="${quote(job_name)}">
    <INPUT TYPE="HIDDEN" ID="job_info" NAME="job_info" VALUE="${quote(job_info)}">

</form>


%if username:
    <!-- Logged in as ${username} -->
%endif



<%def name="toolHelp()">

<a href="#tutorials" onclick="$('#tutorials').toggle()">Show/hide tutorials</a> 

<div id="tutorials" style="display:none">

<table class="colored" style="text-align: center; margin-left: auto; margin-right: auto; table-layout:auto; word-wrap:break-word; margin-top: 20px; margin-bottom: 20px;">
<tr><td>
    Tutorial&nbsp;1:
</td><td>
    Descriptive statistics
</td><td>
    (Gene coverage)
</td><td>
    <a href='${h.url_for("hyper?dbkey=hg18&demoID=Gene%20Coverage&track1=Genes%20and%20gene%20subsets%3AGenes%3ACCDS&track2=&analysis=Proportional+coverage&method=__chrBands__")}'>Demo</a>
</td><td>
    <a href="javascript:parent.show_in_overlay({url:'${h.url_for('/static/hyperbrowser/html/Descriptive_statistics_draft.html')}',width:576,height:424,scroll:'no'})">Screencast</a>
</td><td>
    <a href="http://sites.google.com/site/hyperbrowserhelp/descriptive-statistics">Text</a>
</td></tr>

<tr class="odd_row"><td>
    Tutorial&nbsp;2:
</td><td>
    Hypothesis testing
</td><td>
    (H3K27me3 vs SINE repeats)
</td><td>
    <a href='${h.url_for("hyper?demoID=H3K27me3+vs+SINE&dbkey=mm8&track1=Chromatin%3AHistone%20modifications%3ABLOC%20segments%3AMEFB1&track2=Sequence%3ARepeating%20elements%3ASINE&analysis=Overlap%3F&method=__custom__&region=chr17:3m-&binsize=5m&config_Null%20model=Preserve%20segments%20%28T2%29%2C%20segment%20lengths%20and%20inter-segment%20gaps%20%28T1%29%3B%20randomize%20positions%20%28T1%29%20%28MC%29&config_Monte%20Carlo%20resamplings=200&config_Random%20seed=0")}'>Demo</a><br>
</td><td>
    <a href="javascript:parent.show_in_overlay({url:'${h.url_for('/static/hyperbrowser/html/Hypothesis_testing_draft.html')}',width:576,height:424,scroll:'no'})">Screencast</a>
</td><td>
    <a href="http://sites.google.com/site/hyperbrowserhelp/hypothesis-testing">Text</a>
</td></tr>

<tr><td>
    Tutorial&nbsp;3:
</td><td>
    Global analysis&nbsp;/ creating &quot;ad hoc&quot; tracks
</td><td>
    (H3K4me3 vs T-cell expression)
</td><td>
    <a href='${h.url_for("hyper?demoID=H3K4me3+vs+T-cell+expression&dbkey=hg18&track1=Chromatin%3AHistone%20modifications%3ANPS%20preprocessed%3AMethylation%2C%20CD4%20T-cells%2C%20Barski%20et%20al.%202007%3AH3K4me3&track2=Sample%20data%3AExpression%3AT-cells%2C%201kb%20downstream%20for%20TSS&analysis=Located%20in%20segments%20with%20high%20values%3F&method=__chrArms__&config_Null%20model=Preserve%20points%20%28T1%29%20and%20segments%20%28T2%29%3B%20permute%20the%20values%20of%20T2-segments")}'>Demo</a><br>
</td><td>
    <a href="javascript:parent.show_in_overlay({url: '${h.url_for('/static/hyperbrowser/html/Global_analysis_draft.html')}',width:576,height:424,scroll:'no'})">Screencast</a>
</td><td>
    <a href="http://sites.google.com/site/hyperbrowserhelp/global-analysis">Text</a>
</td></tr>

<tr class="odd_row"><td>
    Tutorial 4:
</td><td>
    Local analysis&nbsp;/ import &amp; export
</td><td>
    (MLV virus vs FirstEF promoters)
</td><td>
    <a href='${h.url_for("hyper?demoID=MLV+vs+Expanded FirstEF promoters&dbkey=hg18&track1=Phenotype%20and%20disease%20associations%3AAssorted%20experiments%3AVirus%20integration%2C%20Derse%20et%20al.%20%282007%29%3AMLV&track2=Sample%20data%3APromoters%3AFirstEF%20promoters%20expanded%202kb&analysis=Located%20inside%3F&method=__custom__&region=*&binsize=30m&config_Null%20model=Preserve%20segments%20%28T2%29%20and%20number%20of%20points%20%28T1%29%3B%20randomize%20point%20positions&config_Random%20seed=0")}'>Demo</a><br>
</td><td>
    <a href="javascript:parent.show_in_overlay({url: '${h.url_for('/static/hyperbrowser/html/Local_analysis_draft.html')}',width:576,height:424,scroll:'no'})">Screencast</a>
</td><td>
    <a href="http://sites.google.com/site/hyperbrowserhelp/local-analysis">Text</a>
</td></tr>

<tr><td>
    Tutorial&nbsp;5:
</td><td>
    Intensity tracks
</td><td>
    (Exon boundaries vs melting forks)
</td><td>
    <a href='${h.url_for("hyper?demoID=Exon+boundaries+vs+melting+fork+probs&dbkey=sacCer1&track1=Genes%20and%20gene%20subsets%3AExon%20boundaries%3ALefts&track2=DNA%20structure%3AMelting%3AMelting%20fork%20probabilities%3ALeft-facing%20fork&analysis=Higher%20values%20at%20locations%3F&method=__chrs__&config_Null%20model=Preserve%20function%20%28T2%29%20and%20number%20of%20points%20%28T1%29%3B%20randomize%20positions%20by%20intensity%20%28T1%29%20%28MC%29&config_Monte%20Carlo%20resamplings=200&config_Random%20seed=0&trackIntensity=Sample%20data%3AIntensity%20tracks%3AExon%20lefts%2C%20controlled%20by%20GC%20content")}'>Demo</a><br>
</td><td>
    <a href="javascript:parent.show_in_overlay({url:'${h.url_for('/static/hyperbrowser/html/Intensity_tracks_draft.html')}',width:576,height:424,scroll:'no'})">Screencast</a>
</td><td>
    <a href="http://sites.google.com/site/hyperbrowserhelp/intensity-tracks">Text</a>
</td></tr>

<tr class="odd_row"><td>
    Tutorial 6:
</td><td>
    Generate sample regulome
</td><td>
    (A few TFs vs a few diseases)
</td><td>
	<a href='${h.url_for("hyper?dbkey=hg18&track1=Sample%20data%3AA%20few%20TFs%3A--%20All%20subtypes%20--&track2=Sample%20data%3AA%20few%20diseases%3A--%20All%20subtypes%20--&analysis=Category%20pairs%20differentially%20co-located%3F&method=__custom__&region=chr1&binsize=10m")}'>Demo</a>
</td><td>
    N/A
</td><td>
    N/A
</td></tr>
</table>

<div style="text-align: center;">
Hint: if the window seems cramped after clicking &quot;Text&quot;, try clicking at the right divider bar to hide the history.
</div>

</div>

</%def>
