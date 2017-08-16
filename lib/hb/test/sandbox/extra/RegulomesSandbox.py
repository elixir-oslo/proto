import quick.extra.GoogleMapsInterface as gmi
from quick.extra.RenameTrack import renameTrack

genome = 'hg18'
regulomes = [x.strip() for x in open('test/sandbox/extra/regulomes.txt')]
fixTns = dict([tuple([tuple(tn.strip().split(':')) for tn in x.strip().split('\t')]) for x in open('test/sandbox/extra/regulomeFixTns.txt')])

maps = gmi.Map.getMaps()
regMaps = [x for x in maps if x.getName() in regulomes]

def getMarkInfo(curMap):
    mi = gmi.MarkInfo(curMap.getName(), 0, 0, '')
    curDir = '/'.join(mi._resultDir.split('/')[:-1])
    mapId = [x.strip().split("'")[1] for x in open(curDir + '/index.html') if x.strip().startswith('mapId')][0]
#    print 'MapId: ', mapId
    return gmi.MarkInfo(curMap.getName(), 0, 0, mapId)

def updateTrackName(mi, fn, tnFrom, tnTo):
    tn = mi._getBaseTrackName(fn)
    if tnFrom == tuple(tn):
        baseTrackNameFn = '/'.join([mi._commonDir, fn])
        open(baseTrackNameFn, 'w').write(':'.join(tnTo))
        print 'Writing to %s: %s' % (baseTrackNameFn, ':'.join(tnTo))

#for tnFrom, tnTo in fixTns.iteritems():
#    print tnFrom, ' -> ', tnTo
##    renameTrack(genome, list(tnFrom), list(tnTo))
#    for curMap in maps:
#        mi = getMarkInfo(curMap)
#        updateTrackName(mi, 'rowBaseTrackName.txt', tnFrom, tnTo)
#        updateTrackName(mi, 'colBaseTrackName.txt', tnFrom, tnTo)

tns = set()
for curMap in regMaps:
    mi = getMarkInfo(curMap)
#    titleFn = curDir + '/data/Title.txt'
#    title = curMap.getPrettyName()
#    print title
#    if not title.startswith('**'):
#        open(titleFn, 'w').write('*' + title)

    rowTn = mi._getBaseTrackName('rowBaseTrackName.txt')
    colTn = mi._getBaseTrackName('colBaseTrackName.txt')
    tns.add(tuple(rowTn))
    tns.add(tuple(colTn))
    print rowTn, ' - ', colTn
    #if len( colTn ) == 1:
    #    fn = '/'.join([mi._commonDir, 'colBaseTrackName.txt'])
    #    open(fn, 'w').write(':'.join(colTn[0].split('/')))
    #    print fn, (':'.join(colTn[0].split('/')))

for x in sorted(tns):
    print ':'.join(x)
