<%!
import sys, traceback
from cgi import escape
from urllib import quote, unquote
import json

import proto.hyperbrowser.hyper_gui as gui
%>
<%
#reload(gui)
#trans.response.content_type = 'text/json'
data = {'exception': False}
try:

    galaxy = gui.GalaxyWrapper(trans)
    params = galaxy.params
    genome = params.get('dbkey', 'hg18')

    datasets = galaxy.getHistory(hyper.getSupportedGalaxyFileFormats())
    username = galaxy.getUserName()

    tracks = [None] * 3

    tracks[0] = gui.TrackWrapper('track1', hyper, [], galaxy, datasets, genome)
    tracks[1] = gui.TrackWrapper('track2', hyper, [('', '', False)], galaxy, datasets, genome)
    tracks[2] = gui.TrackWrapper('trackIntensity', hyper, [('', '', False)], galaxy, datasets, genome)

    stats = params.get('stats')
    _stats = params.get('_stats')
    region = params.get('region', '*')
    binsize = params.get('binsize', '*')
    method = params.get('method');

    if _stats:
        configOptions = hyper.getConfigOptions(_stats)
        trackTypeOptions = hyper.getTrackTypeOptions(_stats)

        optDict = {}
        for opt in configOptions[0]:
            optDict[opt] = params.get('config_' + quote(opt))
        for opt in trackTypeOptions[0]:
            optDict[opt] = params.get('config_' + quote(opt))
        config_stats = hyper.setConfigChoices(_stats, optDict)

    if method in ['__chrs__', '__chrBands__', '__chrArms__', '__genes__']:
        region = method
        binsize = params.get(method)
    elif method == '__brs__':
        region = method
        binsize = '*'
    elif method in ['binfile', '__history__']:
        binfile = params.get('binfile','')
        binsize, region = galaxy.getHistoryOptionSecureIdAndExt(binfile)
        if not region:
            region = '__history__'
            binsize = ''

##         binfile = params.get('binfile','').split(',')
##         if len(binfile) > 3:
##             region = binfile[2]
##             binsize = galaxy.getDataFilePath(binfile[1])
##         else:
##             region = '__history__'
##             binsize = ''

        #print binsize
        #region = userBins.split(',')[2]



    valid = True
#    if stats:
#        valid = hyper.runValid(tracks[0].definition(), tracks[1].definition(), config_stats, region, binsize, genome)

    #raise Exception('test')

    # AJAX call
    ajax = params.get('ajax')
    if ajax:
        if ajax == 'validate':
            if stats and region:
                valid = hyper.runValid(tracks[0].definition(), tracks[1].definition(), config_stats, region, binsize, genome, tracks[2].definition())
                if valid == True:
                    data['valid'] = 'OK'
                    data['job_name'], data['job_info'] = hyper.getRunNameAndDescription(tracks[0].definition(), tracks[1].definition(), config_stats, region, binsize, genome)
                else:
                    data['valid'] = valid
            else:
                data['valid'] = 'No region defined'

        elif ajax == 'config':
            optDict = {}
            for opt in configOptions[0]:
                optDict[opt] = params.get('config_' + quote(opt))
            data['stats'] = quote(config_stats)
            data['stats_text'] = hyper.getTextFromAnalysisDef(data['stats'], genome, tracks[0].definition(), tracks[1].definition())


        elif ajax == 'trackinfo':
            trackname = params.get('about')
            data = hyper.getTrackInfo(genome, trackname.split(':'))

        elif ajax == 'genomeinfo':
            genomename = params.get('about')
            data = hyper.getGenomeInfo(genomename)

        elif ajax == 'help':
            about = params.get('about')
            data = hyper.getHelpText(about)
            #data = 'HB: Help on '+about

        elif ajax == 'rundescription':
#            if method in ['__chrs__', '__chrBands__', '__chrArms__', '__genes__']:
#                region = method
#                binsize = params.get(method)
            description = ''
            if tracks[0].selected() and tracks[1].selected() and region != None:
                description = hyper.getRunDescription(tracks[0].definition(), tracks[1].definition(), config_stats, region, binsize, genome, username, tracks[2].definition())
            data = description
            #data = description + '; ' + region + '; ' + binsize;

except:
    #data = sys.exc_info()[0]
    data['exception'] = traceback.format_exc()

%>
${json.dumps(data)}
