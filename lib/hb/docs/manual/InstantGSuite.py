from collections import OrderedDict
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GSuiteTrack, FtpGSuiteTrack, HbGSuiteTrack
import gold.gsuite.GSuiteComposer as GSuiteComposer
import gold.gsuite.GSuiteParser as GSuiteParser

gSuite = GSuite()

uri1 = FtpGSuiteTrack.generateURI(netloc='server.com', path='file.bed')
gSuite.addTrack(GSuiteTrack( uri1, title='Track1', attributes=OrderedDict([('a', 'yes'), ('b', 'no')]) ))

uri2 = HbGSuiteTrack.generateURI(trackName=['Genes and gene subsets', 'Genes', 'Refseq'])
gSuite.addTrack(GSuiteTrack( uri2, attributes=OrderedDict([('b', 'no'), ('c', 'yes')]) ))

gSuite.setGenomeOfAllTracks('hg19')

contents = GSuiteComposer.composeToString(gSuite)

print 'GSuite file contents'
print '--------------------'
print contents

gSuite2 = GSuiteParser.parseFromString(contents)

print 'Various ways of direct access'
print '-----------------------------'
print "genome=%s, location=%s, file format=%s, track type=%s, attributes=%s" % \
    (gSuite.genome, gSuite.location, gSuite.fileFormat, gSuite.trackType, gSuite.attributes)

for track in gSuite2.allTracks():
    print "uri=%s, path=%s, trackName=%s" % (track.uri, track.path, track.trackName)

print "netloc=" + gSuite2.getTrackFromTitle('Track1').netloc

tracks=list(gSuite.allTracks())
print "b=" + tracks[1].attributes['b']
