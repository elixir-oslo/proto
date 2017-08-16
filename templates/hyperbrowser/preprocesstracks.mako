<%!
import sys, traceback
from cgi import escape
from urllib import quote, unquote
%>
<%
galaxy = control.galaxy
params = galaxy.params
error = ''
try:
    control.action()
except:
    error = traceback.format_exc()

%>
<%inherit file="base.mako"/>
<%namespace name="functions" file="functions.mako" />


<%def name="title()">Preprocess tracks</%def>
<%def name="head()">
    <script type="text/javascript">
        <%include file="common.js"/>
    </script>
</%def>

<form method="post" action="">
<p>
##    Genome build: ${control.genomeElement.getHTML()} ${control.genomeElement.getScript()}    
    ${functions.genomeChooser(control)}
</p>
${functions.trackChooser(control.track, 0, control.params)}

%if control.userHasFullAccess():

<input id="start" type="button" value="Preprocess" onclick="form.action='${h.url_for("/tool_runner")}';form.submit()">

%else:
        <p>You must be one of us to start preprocessing</p>

%endif

    <INPUT TYPE="HIDDEN" NAME="tool_id" VALUE="hb_preprocess">
    <INPUT TYPE="HIDDEN" NAME="mako" VALUE="preprocesstracks">
    <INPUT TYPE="HIDDEN" NAME="URL" VALUE="http://dummy">

</form>
${error}
