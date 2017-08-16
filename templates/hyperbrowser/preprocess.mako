<%!
import sys
from cgi import escape
from urllib import quote, unquote

import proto.hyperbrowser.hyper_gui as gui


def selected(opt, sel):
    return ' selected="selected" ' if opt == sel else ''

def disabled(opt, sel):
    return ' disabled="disabled" ' if opt == sel else ''

def _disabled(opt, sel):
    return ' disabled="disabled" ' if opt != sel else ''

%>
<%
#reload(gui)

#print vars(trans.get_user().email)

galaxy = gui.GalaxyWrapper(trans)

params = galaxy.params
#print params


genomes = hyper.getAllGenomes(galaxy.getUserName())
genome = params.get('dbkey', genomes[0][1])
genomeElement = gui.SelectElement('dbkey', genomes, genome)


#datasets = galaxy.getHistory(['bed','wig'])
datasets = []

#track = gui.TrackWrapper('track1', hyper, [], galaxy, datasets, genome)
#track.fetchTracks()


formAction = ''

%>
<%inherit file="base.mako"/>

<%def name="title()">Preprocess tracks</%def>
<%def name="head()">
    <script type="text/javascript">
        <%include file="common.js"/>
    </script>
</%def>

<form method="post" action="${formAction}">
<p>
    Genome build: ${genomeElement.getHTML()} ${genomeElement.getScript()}    
</p>

%if hyper.userHasFullAccess(galaxy.getUserName()):

<input id="start" type="button" value="Preprocess" onclick="form.action='/tool_runner';form.submit()">

%else:
        <p>You must be one of us to start preprocessing</p>

%endif

    <INPUT TYPE="HIDDEN" NAME="tool_id" VALUE="hb_preprocess">
    <INPUT TYPE="HIDDEN" NAME="URL" VALUE="http://dummy">

</form>
