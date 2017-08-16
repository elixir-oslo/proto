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

    filename = params['map']
    mapId = params['mapid']
    
    info = gmi.MarkInfo(filename, 0, 0, mapId)

    if not info.validMapId():
	error = 'Marker info is not supported until a valid mapId is chosen.'
    else:
        try:
    	    row = int(params['row'])
            col = int(params['col'])
        except:
	    row, col = 0, 0
            error = 'Column and/or row index is not valid. This may be caused by incorrectly specified map coordinates.'

        info = gmi.MarkInfo(filename, col, row, mapId)
        infotext = info.getHtmlText()

except:
    error = traceback.format_exc()

%>
<div style="overflow: auto; height: 200px">
%if error != '':
    ${error}
%else:
    ${infotext}
%endif
</div>
