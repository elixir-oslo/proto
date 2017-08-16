<%!
import sys, traceback
from cgi import escape
from urllib import quote, unquote

import quick.extra.GoogleMapsInterface as gmi
import proto.hyperbrowser.hyper_gui as gui
%>
<%
error = ''
infotext = ''
style = ''
geneList = []
colNames = []
rowNames = []
try:
    galaxy = gui.GalaxyWrapper(trans)
    params = galaxy.params
    fro = params['from'].split(',')
    to = params['to'].split(',')
    mapId = params['mapid']

    dirname = params['map']
    info = gmi.MarkInfo(dirname, 0, 0, mapId)
    
    if not info.validMapId():
	error = 'Cluster info is not supported until a valid mapId is chosen.'
    else:
        try:
    	    colmin = min(int(fro[0]), int(to[0]))	
            colmax = max(int(fro[0]), int(to[0]))
            rowmin = min(int(fro[1]), int(to[1]))
            rowmax = max(int(fro[1]), int(to[1]))
        except:
	    colmin, colmax, rowmin, rowmax = 0, 0, 0, 0
            error = 'Column and/or row index is not valid. This may be caused by incorrectly specified map coordinates.'

        cols = range(colmin, 1 + colmax)
        rows = range(rowmin, 1 + rowmax)
        
        infotext = info.getClusterHtmlText(cols, rows)
#    colNames, rowNames = info.getColAndRowNames(cols, rows)
#    geneList = info.getGeneListOfRegulomeCluster(colNames, rowNames)
    #shelfFn = '/work/hyperbrowser/results/developer/static/maps/common/tfAndDisease2rankedGeneLists.shelf'        
    #geneList = hyper._getGeneListOfRegulomeCluster(colNames, rowNames, shelfFn)
    #geneList = hyper.getGeneListOfRegulomeCluster(','.join(colNames), ','.join(rowNames))
        coordtext = 'Cluster for columns ' + str(colmin) + ' to ' + str(colmax) + ', rows ' + str(rowmin) + ' to ' + str(rowmax)
except:
    error = traceback.format_exc()

%>
<div class="clusterinfo" style="height: 250px; overflow: auto">
%if error != '':
    ${error}
%else:
    ${coordtext}
    ${infotext}
%endif
</div>
