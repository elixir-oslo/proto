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

tool_id = params.get('tool_id', 'hb_segmentation')

intrack = params.get('intrack', '')
outtrack = params.get('outtrack', '')
method = params.get('method', '')
min_length = params.get('min_length', '0')
formAction = h.url_for('/tool_runner')

%>
<%namespace name="functions" file="functions.mako" />

<%inherit file="base.mako"/>

<%def name="title()">Create segmentation</%def>
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

    <fieldset><legend>Input track</legend>
    <p><label>Name: <input size="50" name="intrack" value="${intrack}"></label></p>
    </fieldset>
    <fieldset><legend>Output track</legend>
    <p><label>Name: <input size="50" name="outtrack" value="${outtrack}"></label></p>
    </fieldset>
    <fieldset><legend>Method</legend>
    <p><label>def categorizerMethod(val,diff): <br><textarea cols="80" rows="10" name="method">${method}</textarea></label></p>
    </fieldset>
    <fieldset><legend>Minimum segment length:</legend>
    <p><label>Name: <input size="20" name="min_length" value="${min_length}"></label></p>
    </fieldset>


    <p><input id="start" type="submit" value="Execute"></p>
%else:
    ${functions.accessDenied()}

%endif

    <INPUT TYPE="HIDDEN" NAME="mako" VALUE="segmentation">
    <INPUT TYPE="HIDDEN" NAME="tool_id" VALUE="${tool_id}">
    <INPUT TYPE="HIDDEN" NAME="URL" VALUE="http://dummy">

</form>
