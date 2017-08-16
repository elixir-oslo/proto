<%!
import sys
from cgi import escape
from urllib import quote, unquote

import proto.hyperbrowser.hyper_gui as gui


def _disabled(opt, sel):
    return ' disabled="disabled" ' if opt != sel else ''

%>
<%
#reload(gui)

galaxy = gui.GalaxyWrapper(trans)

params = galaxy.params

genomes = hyper.getAllGenomes(galaxy.getUserName())
genome = params.get('dbkey', genomes[0][1])
genomeElement = gui.SelectElement('dbkey', genomes, genome)

integratedname = params.get('integratedname', '')
historyitem = params.get('historyitem')

track = gui.TrackWrapper('integratedname', hyper, [], galaxy, [], genome)
track.fetchTracks()
track.legend = 'Integrated Track'

formAction = h.url_for('/tool_runner')

%>
<%namespace name="functions" file="functions.mako" />

<%inherit file="base.mako"/>

<%def name="title()">Integrate track from history</%def>
<%def name="head()">
    <script type="text/javascript">
        <%include file="common.js"/>
        
        function validate(form) {
            var integratedname = form.integratedname.value;
            var histindex = form.historyitem.selectedIndex;
            if (integratedname && histindex > 0)
                return true;
            alert('Please select history item and fill in track name!');
            return false;
        }
    </script>
</%def>

<form method="post" action="${formAction}" onsubmit="return validate(this)">

%if hyper.userHasFullAccess(galaxy.getUserName()):    

<p>
##    Genome build: ${genomeElement.getHTML()} ${genomeElement.getScript()}    
    ${functions.genomeChooser(galaxy, genomeElement, genome)}
</p>


        <fieldset><legend>History</legend>
            <select name="historyitem">
            	<option value=""> - Choose from history - </option>
                ${galaxy.optionsFromHistory(hyper.getSupportedGalaxyFileFormats(), historyitem)}
            </select>        
        </fieldset>
${functions.trackChooserTest(track, 0, params)}
<!--    <fieldset><legend>Integrated track</legend>
    <label>Name: <input size="50" name="integratedname" value="${integratedname}"></label>
    </fieldset>
    -->
    <div><input type="checkbox" name="access_public" value="True" ${'checked' if params.get('access_public') else ''}> Make track publicly available</div>
    <p><input id="start" type="submit" value="Integrate track"></p>
%else:
        <p>You must be one of us to integrate tracks from history</p>

%endif


    <INPUT TYPE="HIDDEN" NAME="mako" VALUE="integrate">
    <INPUT TYPE="HIDDEN" NAME="tool_id" VALUE="hb_integrate">
    <INPUT TYPE="HIDDEN" NAME="URL" VALUE="http://dummy">

</form>
