<%!
import sys
from cgi import escape
from urllib import quote, unquote

import proto.hyperbrowser.hyper_gui as gui
%>
<%
reload(gui)

galaxy = gui.GalaxyWrapper(trans)

params = galaxy.params

genomes = hyper.getAllGenomes(galaxy.getUserName())
genome = params.get('dbkey', genomes[0][1])
genomeElement = gui.SelectElement('dbkey', genomes, genome)

tool_id = params.get('tool_id', 'hb_batchrun')
batch = params.get('batch', '')

formAction = h.url_for('/tool_runner')

%>
<%namespace name="functions" file="functions.mako" />

<%inherit file="base.mako"/>

<%def name="title()">Batch run</%def>
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
##    Genome build: ${genomeElement.getHTML()} ${genomeElement.getScript()}    
    ${functions.genomeChooser(galaxy, genomeElement, genome)}
</p>

    <label>Commands:<br><textarea cols="100" rows="20" name="batch">${escape(batch)}</textarea></label>

    <p><input id="start" type="submit" value="Run batch"></p>
%else:
    ${functions.accessDenied()}

%endif


    <INPUT TYPE="HIDDEN" NAME="mako" VALUE="batchrun">
    <INPUT TYPE="HIDDEN" NAME="tool_id" VALUE="${tool_id}">
    <INPUT TYPE="HIDDEN" NAME="URL" VALUE="http://dummy">

</form>
