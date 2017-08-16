<%!
import sys
from cgi import escape
from urllib import quote, unquote

import proto.hyperbrowser.hyper_gui as gui
%>


<%inherit file="/proto/functions.mako" />


<%def name="trackChooser(track, i, params, do_reset=True, readonly=False)">
    <%
        galaxy = gui.GalaxyWrapper(trans)
        genome = params.get('dbkey')
    %>
    <fieldset><legend>${track.legend}</legend>

  %if not readonly:
    <%
    typeElement = gui.TrackSelectElement(track, 0)

    # reset stats parameter when changing track
    if do_reset:
        typeElement.onChange = "if ($('#_stats')){$('#_stats').val('');$('#stats').val('');}" + typeElement.onChange

##     typeElement.onChange = "appendValueFromInputToInput(this, '#" + track.nameMain + "'); " + typeElement.onChange
    %>
    ${typeElement.getHTML()} ${typeElement.getScript()}

    %if track.valueLevel(0) == 'galaxy':
            <select name="${track.nameFile}" onchange="form.action='?';form.submit()">
                ${track.optionsFromHistory(params.get(track.nameFile))}
##                ${galaxy.optionsFromHistory(hyper.getSupportedGalaxyFileFormats(), params.get(track.nameFile))}
            </select>

##    %elif track.valueLevel(0) == '__recent_tracks':
##            <select name="${track.nameRecent}" onchange="setTrackToRecent('${track.nameMain}', this, form)">
##                <option value=""> -- Select -- </option>
##                %for t in track.recentTracks:
##                    <option value="${t}">${t}</option>
##                %endfor
##            </select>
    %else:
        %for j in range(1, 10):
            %if track.getTracksForLevel(j):
                %if track.valueLevel(j - 1) == 'K-mers':
                    <div style="margin-left:${j}em">|_
                    <input type="text" size="25" name="${track.nameLevel(j)}" value="${track.valueLevel(j) if track.valueLevel(j) != None else ''}" onblur="checkNmerReload(event, this)" onkeypress="checkNmerReload(event, this)">
                    </div>
                %else:
                    <%
                        levelElement = gui.TrackSelectElement(track, j)
##                         levelElement.onChange = "appendValueFromInputToInput(this, '#" + track.nameMain + "'); " + levelElement.onChange
                    %>
                    <div style="margin-left:${j}em">|_ ${levelElement.getHTML()} ${levelElement.getScript()}</div>
                %endif
            %endif
        %endfor
    %endif

  %endif

    %if track.main and track.valueLevel(0) != 'galaxy' and track.selected():
        <%
        sti_val = params.get('show_info_'+track.nameMain, '0')
        if sti_val == '1':
            sti_class = 'hideInfo'
            sti_display = ''
        else:
            sti_class = 'showInfo'
            sti_display = 'display:none'

        %>
        <img class="${sti_class}" src="${h.url_for('/static/style/info_small.png')}" alt="Track information" title="Track information" onclick="getInfo(document.forms[0], this, '${track.nameMain}')"/>
        <div id="info_${track.nameMain}" class="infomessagesmall" style="${sti_display}"> ${hyper.getTrackInfo(genome, track.definition())} </div>
        <input type="hidden" name="show_info_${track.nameMain}" id="show_info_${track.nameMain}" value="${sti_val}">

    %endif

        <input type="hidden" name="${track.nameMain}" id="${track.nameMain}" value="${track.asString()}">

        <input type="hidden" name="${track.nameState}" id="${track.nameState}" value="${track.getState()}">

    %if i == 0:
        ${self.help(track.nameMain, 'What is a genomic track?')}
    %else:
        <br>&nbsp;<br>
    %endif

    <%
##    if track.selected():
##        valid = hyper.trackValid(genome, track.definition())
##    else:
##        valid = True
    %>
    %if track.valid != True:
        <div class="errormessagesmall">${track.valid}</div>
    %endif

    </fieldset>

</%def>


<%def name="genomeInfo(params, genome)">
    <%
        sti_val = params.get('show_genome_info', '0')
        if sti_val == '1':
            sti_class = 'hideInfo'
            sti_display = ''
        else:
            sti_class = 'showInfo'
            sti_display = 'display:none'

    %>


    %if hyper:
        <%
            genomeInfo = hyper.getGenomeInfo(genome)
        %>

        %if genomeInfo:
            <img class="${sti_class}" src="${h.url_for('/static/style/info_small.png')}" alt="Genome info" title="Genome information" onclick="getGenomeInfo(document.forms[0], this, '${genome}')"/>
            <div id="genome_info" class="infomessagesmall" style="${sti_display}"> ${genomeInfo} </div>
            <input type="hidden" name="show_genome_info" id="show_genome_info" value="${sti_val}">
        %else:
            %if genome != '?':
                <div class="errormessagesmall">
                ${genome} is not yet supported by HyperBrowser.<br>
            %else:
                <div class="warningmessagesmall">
            %endif
                Please select a genome build from the list above to continue.
                </div>
        %endif
    %endif
</%def>

