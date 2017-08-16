import sys, os, getopt, types
from urllib import quote, unquote

from gold.application.GalaxyInterface import GalaxyInterface
# from quick.util.CommonFunctions import getGalaxyFnFromDatasetId
from proto.CommonFunctions import getSecureIdAndExtFromDatasetInfoAsStr

import proto.hyperbrowser.hyper_gui as hg


def main():
    filename = sys.argv[1]
    tool = None
    if len(sys.argv) > 2:
        tool = sys.argv[2]

    job_params,params = hg.load_input_parameters(filename)
#    print job_params, params

    file_path = None

    trackName1 = ""
    trackName2 = ""
    intensityTrackName = None
    subName1 = ""
    subName2 = ""
    track1State = None
    track2State = None
    intensityTrackFile = None
    intensityTrackFileType = None
    statClassName = ""
    binSize = "*"
    region = "*"
    userBins = None
    output = filename
    extractFile = None
    customFile = None
    statsFile = None
    method = None
    segLength = 0
    overlaps = None
    genome = 'hg18'
    username = None

    for o, a in params.items():
        if a == "":
            continue
        a = str(a)
        if o == "dbkey":
            genome = a
        elif o == "tool":
            tool = a
        elif o == "track1":
            trackName1 = a
        elif o == "track2":
            trackName2 = a
        elif o == "trackIntensity":
            intensityTrackName = a
        elif o == "grptrack1":
            grpName1 = a
        elif o == "grptrack2":
            grpName2 = a
        elif o == "subtrack1":
            subName1 = a
        elif o == "subtrack2":
            subName2 = a
        elif o == "stats":
            statClassName = a
        elif o == "binsize":
            binSize = a
        elif o == "seglength":
            segLength = int(a)
        elif o == "region":
            region = a
        elif o == "method":
            method = a
        elif o == "output":
            output = a
#            sys.stdout = open(a, "w", 0)
        elif o == "extract":
            extractFile = a
        elif o == "custom":
            sys.stdout = open(a, "w", 0)
            customFile = a
        elif o == "binfile":
            region = "bed"
            userBins = a
        elif o == 'track1_state':
            track1State = unquote(a)
        elif o == 'track2_state':
            track2State = unquote(a)
        elif o == "statsfile":
            statsFile = a
        elif o == "file_path":
            file_path = a
        elif o == "overlaps":
            overlaps = unquote(a)
        elif o == "userEmail":
            username = a

    if method in ['__chrs__', '__chrBands__', '__chrArms__', '__genes__']:
        region = method
        binSize = params[method]
    elif method == '__brs__':
        region = method
        binSize = '*'

    if userBins:
        if userBins[0] == 'galaxy':  # For backwards compatibility
            binSize = userBins[1]
            region = userBins[2]
        elif userBins.startswith('galaxy'):
            binSize, region = getSecureIdAndExtFromDatasetInfoAsStr(userBins)

    tracks1 = trackName1.split(':')

    tracks2 = trackName2.split(':')

    if intensityTrackName != None:
        intensityTracks = intensityTrackName.split(':')
    else:
        intensityTracks = []

    # if statClassName.startswith('galaxy'):
    #     statsFileId = statClassName.split(',')[1]
    #     statsFile = getGalaxyFnFromDatasetId(statsFileId)
    #     statClassName = '[scriptFn:=' + statsFile.encode('hex_codec') + ':] -> CustomRStat'

    if tool == 'extract':
        #print 'GalaxyInterface.parseExtFormatAndExtractTrackManyBins*', (genome, tracks1, region, binSize, True, overlaps, output)
        if output != None:
            sys.stdout = open(output, "w", 0)
        if params.has_key('sepFilePrRegion'):
            GalaxyInterface.parseExtFormatAndExtractTrackManyBinsToRegionDirsInZipFile(genome, tracks1, region, binSize, True, overlaps, output)
        else:
            GalaxyInterface.parseExtFormatAndExtractTrackManyBins(genome, tracks1, region, binSize, True, overlaps, output)

    else: #run analysis
        if output != None:
            sys.stdout = open(output, "w", 0)
        demoID = params['demoID'] if params.has_key('demoID') else None
        GalaxyInterface.run(tracks1, tracks2, statClassName, region, binSize, genome, output, intensityTracks, username, track1State, track2State, demoID)


if __name__ == "__main__":
    main()
