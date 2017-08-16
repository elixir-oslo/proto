<%!
import sys
from cgi import escape
from urllib import quote, unquote

import proto.hyperbrowser.hyper_gui as gui
%>
<%
#reload(gui)

galaxy = gui.GalaxyWrapper(trans)

params = galaxy.params

genomes = hyper.getAllGenomes(galaxy.getUserName())
genome = params.get('dbkey', genomes[0][1])
genomeElement = gui.SelectElement('dbkey', genomes, genome)

customname = params.get('customname', '')
customwinsize = params.get('customwinsize', '1')
customfunction = params.get('customfunction', '')

datasets = []
tracks = gui.TrackWrapper('track1', hyper, [], galaxy, datasets, genome)
tracks.preTracks = [('-- Sequence --', 'sequence', False)]
tracks.legend = 'Original tracks'


formAction = h.url_for('/tool_runner')

%>
<%namespace name="functions" file="functions.mako" />

<%inherit file="base.mako"/>

<%def name="title()">Create a custom track</%def>
<%def name="head()">
    <script type="text/javascript">
        <%include file="common.js"/>
        
        function validate(form) {
            return true;
        }
    </script>
</%def>

<form method="post" action="${formAction}" onsubmit="return validate(this)">

%if hyper.userHasFullAccess(galaxy.getUserName()):    

<p>
    Genome build: ${genomeElement.getHTML()} ${genomeElement.getScript()}    
</p>

${functions.trackChooser(tracks, 0, params)}

    <fieldset><legend>Custom track</legend>
    
    <p><label>Name: <input size="50" name="customname" value="${customname}"></label></p>

    <p><label>Window size (in bps): <input size="20" name="customwinsize" value="${customwinsize}"></label></p>

    <p><label>Function: <br><textarea cols="100" rows="20" name="customfunction">${escape(customfunction)}</textarea></label></p>

    </fieldset>

    <p><input id="start" type="submit" value="Create track"></p>
%else:
        <p>You must be one of us to create custom tracks</p>

%endif


    <INPUT TYPE="HIDDEN" NAME="tool_id" VALUE="hb_customtrack">
    <INPUT TYPE="HIDDEN" NAME="URL" VALUE="http://dummy">

</form>
