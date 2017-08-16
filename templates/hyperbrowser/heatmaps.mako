<%!
import sys, os
from cgi import escape
from urllib import quote, unquote

import proto.hyperbrowser.hyper_gui as gui
import quick.extra.GoogleMapsInterface as gmi

%>
<%
galaxy = gui.GalaxyWrapper(trans)
%>
<%inherit file="base.mako"/>
<%namespace name="functions" file="functions.mako" />

<%def name="title()">View heatmaps</%def>

%if hyper.userHasFullAccess(galaxy.getUserName()):
    <table border="1">
    %for map in gmi.Map.getMaps():
        <tr><td><b><a href="${map.getUrl()}">${map.getPrettyName()}</a></b></td>
		   <td><a href="${map.getRunDescriptionUrl()}">Run Description</a></td>
		   <td><a href="${map.getCountUrl()}">Counts</a></td>
		   <td><a href="${map.getEffectSizeUrl()}">Effect size</a></td>
		   <td><a href="${map.getPvalUrl()}">P-values</a><br/></td></tr>
    %endfor
    </table>

%else:
    ${functions.accessDenied()}
%endif
