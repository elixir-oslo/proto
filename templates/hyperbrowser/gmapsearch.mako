<%!
import sys, traceback
from cgi import escape
from urllib import quote, unquote

import quick.extra.GoogleMapsInterface as gmi
import proto.hyperbrowser.hyper_gui as gui
%>
<%
error = ''

try:
    galaxy = gui.GalaxyWrapper(trans)
    params = galaxy.params
    map = params['map']
    mapId = params['mapid']
    query = params['query']
    info = gmi.MarkInfo(map, 0, 0, mapId)
    if info.validMapId():
        rows = info.getIndexesFromRowName(query)
    	cols = info.getIndexesFromColName(query)
    else:
	error = 'Searching is not supported until a valid mapId is chosen.'

except:
    error = traceback.format_exc()

%>
%if error != '':
    ${error}
%else:
    %for (name,index) in cols:
        <a href="javascript:;" onclick="gotoColRow(${index}, -1)">${name} (col: ${index})</a><br/>
    %endfor
    %for (name,index) in rows:
        <a href="javascript:;" onclick="gotoColRow(-1, ${index})">${name} (row: ${index})</a><br/>
    %endfor
%endif
