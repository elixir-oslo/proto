import unittest
import os

import config.Config
config.Config.ALLOW_GSUITE_FILE_PROTOCOL = True

from collections import OrderedDict
from tempfile import gettempdir, NamedTemporaryFile

from gold.util.CustomExceptions import InvalidFormatError
import gold.gsuite.GSuiteParser as GSuiteParser
import quick.application.ExternalTrackManager

from test.gold.gsuite.GSuiteTestWithMockEncodingFuncs import GSuiteTestWithMockEncodingFuncs

class TestGTrackSuiteParser(GSuiteTestWithMockEncodingFuncs):
    def _parseContents(self, contents):
        return GSuiteParser.parseLines( contents.split('\n') )

    def testDefaults(self):
        contents = ''

        gSuite = self._parseContents(contents)
        self.assertEquals('unknown', gSuite.location)
        self.assertEquals('unknown', gSuite.fileFormat)
        self.assertEquals('unknown', gSuite.trackType)
        self.assertEquals('unknown', gSuite.genome)
        self.assertEquals([], gSuite.attributes)

    def testParseHeaderLinesNoTracks(self):
        self.assertEquals(('track type', 'segments'),
                          GSuiteParser._parseHeaderLine('##track type: segments\n'))
        self.assertEquals(('location', 'local'),
                          GSuiteParser._parseHeaderLine('##location:Local\n'))
        self.assertEquals(('file format', 'primary'),
                          GSuiteParser._parseHeaderLine('##File format:  primary\n'))
        self.assertEquals(('genome', 'HG18'),
                          GSuiteParser._parseHeaderLine('##genome:  HG18\n'))

    def testParseColSpecLineDirectly(self):
        colSpecLine = '###uri\tantibody'

        self.assertEquals(['uri', 'antibody'], GSuiteParser._parseColumnSpecLine(colSpecLine))

    def testParseColSpecLineDirectlyMoreStdCols(self):
        colSpecLine = '###Uri\tTitle\tfile_format\ttrack_type\tgenome\tANTIBODY'

        self.assertEquals(['uri', 'title', 'file_format', 'track_type', 'genome', 'antibody'], \
                          GSuiteParser._parseColumnSpecLine(colSpecLine))

    def _commonAssertTrack(self, track, uri, scheme, netloc, path, query, suffix, trackName,
                           title, location, fileFormat, trackType, genome, attributes=OrderedDict()):
        self.assertEquals(uri, track.uri)
        self.assertEquals(scheme, track.scheme)
        self.assertEquals(netloc, track.netloc)
        self.assertEquals(path, track.path)
        self.assertEquals(query, track.query)
        self.assertEquals(suffix, track.suffix)
        self.assertEquals(trackName, track.trackName)
        self.assertEquals(title, track.title)
        self.assertEquals(location, track.location)
        self.assertEquals(fileFormat, track.fileFormat)
        self.assertEquals(trackType, track.trackType)
        self.assertEquals(genome, track.genome)
        self.assertEquals(attributes, track.attributes)

    def _commonAssertSingleSimpleTrack(self, gSuite, uri, scheme, netloc,
                                       path, query, suffix, trackName, title, location, fileFormat,
                                       trackType, genome, attributes=OrderedDict()):

        tracks = list(gSuite.allTracks())
        self.assertEquals(1, len(tracks))
        track = tracks[0]

        self._commonAssertTrack(track, uri, scheme, netloc, path, query, suffix, trackName,
                                title, location, fileFormat, trackType, genome,
                                attributes)

    def testParseTrackLineSimpleFtp(self):
        contents = \
            'ftp://server.somewhere.com/path/to/file1.bed\n'

        gSuite = self._parseContents(contents)

        self._commonAssertSingleSimpleTrack(gSuite,
                                            uri='ftp://server.somewhere.com/path/to/file1.bed',
                                            scheme='ftp',
                                            netloc='server.somewhere.com',
                                            path='/path/to/file1.bed',
                                            query=None,
                                            suffix='bed',
                                            trackName=None,
                                            title='file1.bed',
                                            location='remote',
                                            fileFormat='primary',
                                            trackType='unknown',
                                            genome='unknown')

        self.assertEquals('remote', gSuite.location)
        self.assertEquals('primary', gSuite.fileFormat)
        self.assertEquals('unknown', gSuite.trackType)
        self.assertEquals('unknown', gSuite.genome)

    def testParseTrackLineSimpleHttp(self):
        contents = \
            'http://server.other.com/path/to/file2.bed\n'

        gSuite = self._parseContents(contents)

        self._commonAssertSingleSimpleTrack(gSuite,
                                            uri='http://server.other.com/path/to/file2.bed',
                                            scheme='http',
                                            netloc='server.other.com',
                                            path='/path/to/file2.bed',
                                            query=None,
                                            suffix='bed',
                                            trackName=None,
                                            title='file2.bed',
                                            location='remote',
                                            fileFormat='primary',
                                            trackType='unknown',
                                            genome='unknown')

        self.assertEquals('remote', gSuite.location)
        self.assertEquals('primary', gSuite.fileFormat)
        self.assertEquals('unknown', gSuite.trackType)
        self.assertEquals('unknown', gSuite.genome)

    def testParseTrackLineSimpleHttps(self):
        contents = \
            'https://server.other.com/path/to/download?search=file2.bed.gz\n'

        gSuite = self._parseContents(contents)

        self._commonAssertSingleSimpleTrack(gSuite,
                                            uri='https://server.other.com/path/to/download?search=file2.bed.gz',
                                            scheme='https',
                                            netloc='server.other.com',
                                            path='/path/to/download',
                                            query='search=file2.bed.gz',
                                            suffix='gz',
                                            trackName=None,
                                            title='file2.bed.gz',
                                            location='remote',
                                            fileFormat='primary',
                                            trackType='unknown',
                                            genome='unknown')

        self.assertEquals('remote', gSuite.location)
        self.assertEquals('primary', gSuite.fileFormat)
        self.assertEquals('unknown', gSuite.trackType)
        self.assertEquals('unknown', gSuite.genome)

    def testParseTrackLineSimpleRsync(self):
        contents = \
            'rsync://server.other.com/path/to/file3\n'

        gSuite = self._parseContents(contents)

        self._commonAssertSingleSimpleTrack(gSuite,
                                            uri='rsync://server.other.com/path/to/file3',
                                            scheme='rsync',
                                            netloc='server.other.com',
                                            path='/path/to/file3',
                                            query=None,
                                            suffix=None,
                                            trackName=None,
                                            title='file3',
                                            location='remote',
                                            fileFormat='unknown',
                                            trackType='unknown',
                                            genome='unknown')

        self.assertEquals('remote', gSuite.location)
        self.assertEquals('unknown', gSuite.fileFormat)
        self.assertEquals('unknown', gSuite.trackType)
        self.assertEquals('unknown', gSuite.genome)

    def testParseTrackLineSimpleHb(self):
        contents = \
            'hb:/track/name/hierarchy\n'

        gSuite = self._parseContents(contents)

        self._commonAssertSingleSimpleTrack(gSuite,
                                            uri='hb:/track/name/hierarchy',
                                            scheme='hb',
                                            netloc=None,
                                            path=None,
                                            query=None,
                                            suffix=None,
                                            trackName=['track', 'name', 'hierarchy'],
                                            title='hierarchy',
                                            location='local',
                                            fileFormat='preprocessed',
                                            trackType='unknown',
                                            genome='unknown')

        self.assertEquals('local', gSuite.location)
        self.assertEquals('preprocessed', gSuite.fileFormat)
        self.assertEquals('unknown', gSuite.trackType)
        self.assertEquals('unknown', gSuite.genome)

    def testParseTrackLineSimpleGalaxy(self):
        contents = \
            'galaxy:/ad123dd12fg;bed\n'

        #todo: add test of error when fileFormat is set manually to different

        gSuite = self._parseContents(contents)

        self._commonAssertSingleSimpleTrack(gSuite,
                                            uri='galaxy:/ad123dd12fg;bed',
                                            scheme='galaxy',
                                            netloc=None,
                                            path='/path/to/dataset_ad123dd12fg.dat',
                                            query=None,
                                            suffix='bed',
                                            trackName=None,
                                            title='ad123dd12fg',
                                            location='local',
                                            fileFormat='primary',
                                            trackType='unknown',
                                            genome='unknown')

        self.assertEquals('local', gSuite.location)
        self.assertEquals('primary', gSuite.fileFormat)
        self.assertEquals('unknown', gSuite.trackType)
        self.assertEquals('unknown', gSuite.genome)

    def testParseTrackLineSimpleGalaxyFilename(self):
        contents = \
            'galaxy:/ad123dd12fg/filename.bed\n'

        gSuite = self._parseContents(contents)

        self._commonAssertSingleSimpleTrack(gSuite,
                                            uri='galaxy:/ad123dd12fg/filename.bed',
                                            scheme='galaxy',
                                            netloc=None,
                                            path='/path/to/dataset_ad123dd12fg_files/filename.bed',
                                            query=None,
                                            suffix='bed',
                                            trackName=None,
                                            title='filename.bed',
                                            location='local',
                                            fileFormat='primary',
                                            trackType='unknown',
                                            genome='unknown')

        self.assertEquals('local', gSuite.location)
        self.assertEquals('primary', gSuite.fileFormat)
        self.assertEquals('unknown', gSuite.trackType)
        self.assertEquals('unknown', gSuite.genome)

    def testParseTrackLineSimpleFile(self):
        contents = \
            'file:/path/to/file.btrack?track=track:name\n'

        gSuite = self._parseContents(contents)

        self._commonAssertSingleSimpleTrack(gSuite,
                                            uri='file:/path/to/file.btrack?track=track%3Aname',
                                            scheme='file',
                                            netloc=None,
                                            path='/path/to/file.btrack',
                                            query='track=track:name',
                                            suffix='btrack',
                                            trackName=['track', 'name'],
                                            title='name',
                                            location='local',
                                            fileFormat='preprocessed',
                                            trackType='unknown',
                                            genome='unknown')

        self.assertEquals('local', gSuite.location)
        self.assertEquals('preprocessed', gSuite.fileFormat)
        self.assertEquals('unknown', gSuite.trackType)
        self.assertEquals('unknown', gSuite.genome)

    def testParseTrackLineFull(self):
        contents = \
            '###uri\ttitle\tcell\tantibody\n' \
            'ftp://server.somewhere.com/path/to/file1.bed.gz\tTrack\tk562\tcMyb\n' \
            'http://server.other.com/path/to/file2.bed?query=something\tTrack2\tGM12878\tcMyc\n' \
            'https://server.other.com/path/to/file3.bed?query=something\tTrack3\tGM12878\tcMyb\n' \
            'rsync://server.other.com/path/to/file4;wig\tTrack4\tNHFL\t.\n' \
            'hb:/track/name/hierarchy\tTrack (2)\t.\t.\n' \
            'galaxy:/ad123dd12fg;btrack?track=track:name\tTrack (3)\tk562\tcMyb\n' \
            'file:/path/to/file.btrack?track=track:name\tTrack name7\t.\tcMyb\n'

        gSuite = self._parseContents(contents)

        tracks = list(gSuite.allTracks())
        self.assertEquals(7, len(tracks))

        self._commonAssertTrack(tracks[0],
                                uri='ftp://server.somewhere.com/path/to/file1.bed.gz',
                                scheme='ftp',
                                netloc='server.somewhere.com',
                                path='/path/to/file1.bed.gz',
                                query=None,
                                suffix='gz',
                                trackName=None,
                                title='Track',
                                location='remote',
                                fileFormat='primary',
                                trackType='unknown',
                                genome='unknown',
                                attributes=OrderedDict([('cell', 'k562'), ('antibody', 'cMyb')]))

        self._commonAssertTrack(tracks[1],
                                uri='http://server.other.com/path/to/file2.bed?query=something',
                                scheme='http',
                                netloc='server.other.com',
                                path='/path/to/file2.bed',
                                query='query=something',
                                suffix='bed',
                                trackName=None,
                                title='Track2',
                                location='remote',
                                fileFormat='primary',
                                trackType='unknown',
                                genome='unknown',
                                attributes=OrderedDict([('cell', 'GM12878'), ('antibody', 'cMyc')]))

        self._commonAssertTrack(tracks[2],
                                uri='https://server.other.com/path/to/file3.bed?query=something',
                                scheme='https',
                                netloc='server.other.com',
                                path='/path/to/file3.bed',
                                query='query=something',
                                suffix='bed',
                                trackName=None,
                                title='Track3',
                                location='remote',
                                fileFormat='primary',
                                trackType='unknown',
                                genome='unknown',
                                attributes=OrderedDict([('cell', 'GM12878'), ('antibody', 'cMyb')]))

        self._commonAssertTrack(tracks[3],
                                uri='rsync://server.other.com/path/to/file4;wig',
                                scheme='rsync',
                                netloc='server.other.com',
                                path='/path/to/file4',
                                query=None,
                                suffix='wig',
                                trackName=None,
                                title='Track4',
                                location='remote',
                                fileFormat='primary',
                                trackType='unknown',
                                genome='unknown',
                                attributes=OrderedDict([('cell', 'NHFL')]))

        self._commonAssertTrack(tracks[4],
                                uri='hb:/track/name/hierarchy',
                                scheme='hb',
                                netloc=None,
                                path=None,
                                query=None,
                                suffix=None,
                                trackName=['track', 'name', 'hierarchy'],
                                title='Track (2)',
                                location='local',
                                fileFormat='preprocessed',
                                trackType='unknown',
                                genome='unknown',
                                attributes=OrderedDict())

        self._commonAssertTrack(tracks[5],
                                uri='galaxy:/ad123dd12fg;btrack?track=track%3Aname',
                                scheme='galaxy',
                                netloc=None,
                                path='/path/to/dataset_ad123dd12fg.dat',
                                query='track=track:name',
                                suffix='btrack',
                                trackName=['track', 'name'],
                                title='Track (3)',
                                location='local',
                                fileFormat='preprocessed',
                                trackType='unknown',
                                genome='unknown',
                                attributes=OrderedDict([('cell', 'k562'), ('antibody', 'cMyb')]))

        self._commonAssertTrack(tracks[6],
                                uri='file:/path/to/file.btrack?track=track%3Aname',
                                scheme='file',
                                netloc=None,
                                path='/path/to/file.btrack',
                                query='track=track:name',
                                suffix='btrack',
                                trackName=['track', 'name'],
                                title='Track name7',
                                location='local',
                                fileFormat='preprocessed',
                                trackType='unknown',
                                genome='unknown',
                                attributes=OrderedDict([('antibody', 'cMyb')]))

        self.assertEquals('multiple', gSuite.location)
        self.assertEquals('multiple', gSuite.fileFormat)
        self.assertEquals('unknown', gSuite.trackType)
        self.assertEquals('unknown', gSuite.genome)
        self.assertEquals(['cell', 'antibody'], gSuite.attributes)

        from cStringIO import StringIO
        GSuiteParser.validateFromString(contents, outFile=StringIO())

    ## Deprecated, but still allowed

    def testParseTrackLinesFileType(self):
        contents = \
            '##file type: text\n' \
            'http://server.other.com/path/to/file2.bed\n'

        gSuite = self._parseContents(contents)
        tracks = list(gSuite.allTracks())
        self.assertEquals(tracks[0].fileFormat, 'primary')
        self.assertEquals('primary', gSuite.fileFormat)

        contents = \
            '##file type: text\n' \
            '###uri\tfile_type\n' \
            'http://server.other.com/path/to/file2.bed\ttext\n'

        gSuite = self._parseContents(contents)
        tracks = list(gSuite.allTracks())
        self.assertEquals(tracks[0].fileFormat, 'primary')
        self.assertEquals('primary', gSuite.fileFormat)

        contents = \
            '##file type: binary\n' \
            'hb:/track/name/hierarchy\n'

        gSuite = self._parseContents(contents)
        tracks = list(gSuite.allTracks())
        self.assertEquals(tracks[0].fileFormat, 'preprocessed')
        self.assertEquals('preprocessed', gSuite.fileFormat)

        contents = \
            '##file type: binary\n' \
            '###uri\tfile_type\n' \
            'hb:/track/name/hierarchy\tbinary\n'

        gSuite = self._parseContents(contents)
        tracks = list(gSuite.allTracks())
        self.assertEquals(tracks[0].fileFormat, 'preprocessed')
        self.assertEquals('preprocessed', gSuite.fileFormat)

        contents = \
            '##file type: multiple\n' \
            '###uri\tfile_type\n' \
            'http://server.other.com/path/to/file2.bed\ttext\n' \
            'hb:/track/name/hierarchy\tbinary\n'

        gSuite = self._parseContents(contents)
        tracks = list(gSuite.allTracks())
        self.assertEquals(tracks[0].fileFormat, 'primary')
        self.assertEquals(tracks[1].fileFormat, 'preprocessed')
        self.assertEquals('multiple', gSuite.fileFormat)

    ##

    def testCommentsAndEmptyLines(self):
        contents = \
            '\n' \
            '# Comment\n' \
            '##track type: unknown\n' \
            '\n' \
            '# Comment\n' \
            '##genome: hg18\n' \
            '###uri\textra\n' \
            '\n' \
            '# New comment\n' \
            '# Comment\n' \
            '\n' \
            'hb:/track/name\tyes\n' \
            '# Comment\n' \
            '\n' \
            'hb:/track/name2\tno\n' \
            '# Comment\n' \
            '\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('local', gSuite.location)
        self.assertEquals('preprocessed', gSuite.fileFormat)
        self.assertEquals('unknown', gSuite.trackType)
        self.assertEquals('hg18', gSuite.genome)
        self.assertEquals(['extra'], gSuite.attributes)
        self.assertEquals(2, len( list(gSuite.allTracks()) ))

    def testImplicitLocationHeaderMultiple(self):
        contents = \
            'ftp://server/file1.bed\n' \
            'file:/path/to/file.bed\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('multiple', gSuite.location)

    def testImplicitLocationHeaderRemote(self):
        contents = \
            'ftp://server/file1.bed\n' \
            'http://server/file2.bed\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('remote', gSuite.location)

    def testImplicitLocationHeaderLocal(self):
        contents = \
            'hb:/track/name\n' \
            'file:/path/to/file.bed\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('local', gSuite.location)

    def testImplicitLocationHeaderEmpty(self):
        contents = \
            '\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('unknown', gSuite.location)

    def testImplicitFileFormatHeaderOneIsUnknown(self):
        contents = \
            '###uri\tfile_format\n' \
            'ftp://server/file1\tunknown\n' \
            'file:/path/to/file.bed\tprimary\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('unknown', gSuite.fileFormat)

    def testImplicitFileFormatHeaderTextFromUnknown(self):
        contents = \
            '###uri\tfile_format\n' \
            'ftp://server/file1.bed\tunknown\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('primary', gSuite.fileFormat)

    def testImplicitFileFormatHeaderMultiple(self):
        contents = \
            '###uri\tfile_format\n' \
            'hb:/track/name\tpreprocessed\n' \
            'file:/path/to/file.bed\tprimary\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('multiple', gSuite.fileFormat)

    def testImplicitFileFormatHeaderSamePreprocessed(self):
        contents = \
            '###uri\tfile_format\n' \
            'hb:/track/name\tpreprocessed\n' \
            'file:/path/to/file.btrack\tpreprocessed\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('preprocessed', gSuite.fileFormat)

    def testImplicitFileFormatHeaderSamePrimary(self):
        contents = \
            '###uri\tfile_format\n' \
            'file:/path/to/file1.bed\tprimary\n' \
            'file:/path/to/file2.bed\tprimary\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('primary', gSuite.fileFormat)

    def testImplicitFileFormatHeaderUnknown(self):
        contents = \
            'file:/path/to/file1\n' \
            'file:/path/to/file2\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('unknown', gSuite.fileFormat)

    def testImplicitFileFormatHeaderEmpty(self):
        contents = \
            '\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('unknown', gSuite.fileFormat)

    def testImplicitTrackTypeHeaderOneIsUnknown(self):
        contents = \
            '###uri\ttrack_type\n' \
            'ftp://server/file1.bed\tunknown\n' \
            'file:/path/to/file.bed\tsegments\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('unknown', gSuite.trackType)

    def testImplicitTrackTypeHeaderMultiple(self):
        contents = \
            '###uri\ttrack_type\n' \
            'hb:/track/name\tsegments\n' \
            'file:/path/to/file.bed\tpoints\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('multiple', gSuite.trackType)

    def testImplicitTrackTypeHeaderSegmentsCommon(self):
        contents = \
            '###uri\ttrack_type\n' \
            'hb:/track/name\tsegments\n' \
            'file:/path/to/file.gtrack\tlinked segments\n' \
            'file:/path/to/file2.gtrack\tvalued segments\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('segments', gSuite.trackType)

    def testImplicitTrackTypeHeaderValuedPointsCommon(self):
        contents = \
            '###uri\ttrack_type\n' \
            'hb:/track/name\tvalued points\n' \
            'file:/path/to/file.gtrack\tlinked valued points\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('valued points', gSuite.trackType)

    def testImplicitTrackTypeHeaderLinkedPointsCommon(self):
        contents = \
            '###uri\ttrack_type\n' \
            'hb:/track/name\tlinked points\n' \
            'file:/path/to/file.gtrack\tlinked valued points\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('linked points', gSuite.trackType)

    def testImplicitTrackTypeHeaderEmpty(self):
        contents = \
            '\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('unknown', gSuite.trackType)

    def testImplicitGenomeHeaderOneIsUnknown(self):
        contents = \
            '###uri\tgenome\n' \
            'ftp://server/file1\tunknown\n' \
            'file:/path/to/file.bed\thg18\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('unknown', gSuite.genome)

    def testImplicitGenomeHeaderMultiple(self):
        contents = \
            '###uri\tgenome\n' \
            'hb:/track/name\thg18\n' \
            'file:/path/to/file.bed\thg19\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('multiple', gSuite.genome)

    def testImplicitGenomeHeaderSame(self):
        contents = \
            '###uri\tgenome\n' \
            'hb:/track/name\thg18\n' \
            'file:/path/to/file.btrack\thg18\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('hg18', gSuite.genome)

    def testImplicitGenomeHeaderUnknown(self):
        contents = \
            'file:/path/to/file1\n' \
            'file:/path/to/file2\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('unknown', gSuite.genome)

    def testImplicitGenomeHeaderEmpty(self):
        contents = \
            '\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('unknown', gSuite.genome)

    def testFileFormatHeaderWithoutColumn(self):
        contents = \
            '##file format: primary\n' \
            '###uri\n' \
            'file:/path/to/file.bed\n' \
            'file:/path/to/file2.bed\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('primary', gSuite.fileFormat)

        for gSuiteTrack in gSuite.allTracks():
            self.assertEquals('primary', gSuiteTrack.fileFormat)

    def testFileFormatHeaderWithoutColumn(self):
        contents = \
            '##track type: segments\n' \
            '###uri\n' \
            'hb:/track/name\n' \
            'hb:/track/name2\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('segments', gSuite.trackType)

        for gSuiteTrack in gSuite.allTracks():
            self.assertEquals('segments', gSuiteTrack.trackType)

    def testGenomeHeaderWithoutColumn(self):
        contents = \
            '##genome: hg18\n' \
            '###uri\n' \
            'file:/path/to/file.bed\n' \
            'hb:/track/name\n'
        
        gSuite = self._parseContents(contents)
        self.assertEquals('hg18', gSuite.genome)

        for gSuiteTrack in gSuite.allTracks():
            self.assertEquals('hg18', gSuiteTrack.genome)

    def testUnknownLocationHeaderNoTrackLines(self):
        contents = \
            '##location: unknown\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('unknown', gSuite.location)

    def testUnknownFileFormatHeaderNoTrackLines(self):
        contents = \
            '##file format: unknown\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('unknown', gSuite.fileFormat)

    def testUnknownTrackTypeHeaderNoTrackLines(self):
        contents = \
            '##track type: unknown\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('unknown', gSuite.trackType)

    def testUnknownGenomeHeaderNoTrackLines(self):
        contents = \
            '##genome: unknown\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('unknown', gSuite.genome)

    def testNoQuotesStdHeaderCol(self):
        contents = \
            '###uri\tfile%5fformat\n' \
            'ftp://server/file1\tprimary\n'

        gSuite = self._parseContents(contents)
        track = list(gSuite.allTracks())[0]
        self.assertEquals(['file%5fformat'], track.attributes.keys())

    def testQuotesColumnName(self):
        contents = \
            '###uri\textra%20col\n' \
            'ftp://server/file1.bed\tyes\n'

        gSuite = self._parseContents(contents)
        self.assertEquals(['extra col'], gSuite.attributes)

    def testQuotesGenome(self):
        contents = \
            '##genome: hg%2019\n' \
            'ftp://server/file1.bed\n'

        gSuite = self._parseContents(contents)
        self.assertEquals('hg 19', gSuite.genome)

    def testQuotesUri(self):
        contents = \
            'ftp://server/file%201.bed\n'

        gSuite = self._parseContents(contents)
        track = list(gSuite.allTracks())[0]
        self.assertEquals('/file 1.bed', track.path)

    def testQuotesUriHb(self):
        contents = \
            'hb:/my/track%20name\n'

        gSuite = self._parseContents(contents)
        track = list(gSuite.allTracks())[0]
        self.assertEquals(['my', 'track name'], track.trackName)

    def testQuotesAttribute(self):
        contents = \
            '###uri\textra\n' \
            'ftp://server/file1.bed\t%c3\n'

        gSuite = self._parseContents(contents)
        track = list(gSuite.allTracks())[0]
        self.assertEquals('\xc3', track.attributes['extra'])

    #
    # Parsing errors
    #

    def _assertInvalidFormatWhenParsing(self, contents):
        self.assertRaises(InvalidFormatError, \
                          GSuiteParser.parseLines, contents.split('\n'))

    def _assertValueErrorWhenParsing(self, contents):
        self.assertRaises(ValueError, \
                          GSuiteParser.parseLines, contents.split('\n'))

    def testNonAscii(self):
        contents = \
            '##location: remote\xaf\n' \
            'ftp://server/file1.bed\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testQuotesStdHeader(self):
        contents = \
            '##track type: valued%20segments\n' \
            'ftp://server/file1.bed\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testQuotesHeaderGenome(self):
        contents = \
            '##genom%65: hg19\n' \
            'ftp://server/file1.bed\t%c3\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testInvalidHeaderVariable(self):
        contents = \
            '##track typex: segments\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testInvalidHeaderValue(self):
        contents = \
            '##track type: segmentation\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testErrorInHeaderLineSpaces(self):
        contents = \
            '##track type : segments\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testSpaceSeparatedColumns(self):
        contents = \
            '###uri title\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testNotUriAsFirstColumn(self):
        contents = \
            '###title\turi\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testExtraColumnBeforeStd(self):
        contents = \
            '###uri\tcell\tfile_format\ttrack_type\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testIncorrectOrderOfStdColumns(self):
        contents = \
            '###uri\tfile_format\tgenome\ttrack_type\ttitle\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testNotUriAsFirstColumn(self):
        contents = \
            '###title\turi\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testDuplicateColumn(self):
        contents = \
            '###uri\tabc\tabc\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testEmptyColumnName(self):
        contents = \
            '###uri\t\tabc\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testNoColumns(self):
        contents = \
            '###\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testIncorrectFileFormatAttributeShouldBePrimary(self):
        contents = \
            '###uri\tfile_format\n' \
            'file:/path/to/file.bed\tpreprocessed\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testIncorrectLocationHeaderShouldBeMultiple(self):
        contents = \
            '##location: local\n' \
            'ftp://server/file1.bed\n' \
            'file:/path/to/file.bed\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testIncorrectLocationHeaderShouldBeRemote(self):
        contents = \
            '##location: unknown\n' \
            'ftp://server/file1.bed\n' \
            'http://server/file2.bed\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testIncorrectFileFormatHeaderShouldBeUnknown(self):
        contents = \
            '##file format: multiple\n' \
            '###uri\tfile_format\n' \
            'ftp://server/file1\tunknown\n' \
            'file:/path/to/file.bed\tprimary\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testIncorrectFileFormatHeaderShouldBePrimary(self):
        contents = \
            '##file format: unknown\n' \
            '###uri\tfile_format\n' \
            'hb:/track/name\tprimary\n' \
            'file:/path/to/file.bed\tprimary\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testIncorrectFileFormatHeaderShouldBeMultiple(self):
        contents = \
            '##file format: unknown\n' \
            '###uri\tfile_format\n' \
            'hb:/track/name\tpreprocessedy\n' \
            'file:/path/to/file.bed\tprimary\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testIncorrectTrackTypeHeaderShouldBeUnknown(self):
        contents = \
            '##track type: multiple\n' \
            '###uri\ttrack_type\n' \
            'ftp://server/file1.bed\tunknown\n' \
            'file:/path/to/file.bed\tsegments\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testIncorrectTrackTypeHeaderShouldBeMultiple(self):
        contents = \
            '##track type: unknown\n' \
            '###uri\ttrack_type\n' \
            'hb:/track/name\tpoints\n' \
            'file:/path/to/file.bed\tsegments\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testIncorrectTrackTypeHeaderShouldBeSegments(self):
        contents = \
            '##track type: valued segments\n' \
            '###uri\ttrack_type\n' \
            'hb:/track/name\tvalued segments\n' \
            'file:/path/to/file.bed\tsegments\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testIncorrectLocationHeaderNoTrackLinesShouldBeUnknown(self):
        contents = \
            '##location: local\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testIncorrectFileFormatHeaderNoTrackLinesShouldBeUnknown(self):
        contents = \
            '##file format: primary\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testIncorrectTrackTypeHeaderNoTrackLinesShouldBeUnknown(self):
        contents = \
            '##track type: segments\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testIncorrectGenomeHeaderNoTrackLinesShouldBeUnknown(self):
        contents = \
            '##genome: hg19\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testIncorrectMultipleFileFormatHeaderNoColumn(self):
        contents = \
            '##file format: multiple\n' \
            '###uri\n' \
            'file:/path/to/file.bed\n' \
            'file:/path/to/file2.bed\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testIncorrectPrimaryFileFormatHeaderNoColumn(self):
        contents = \
            '##file format: primary\n' \
            '###uri\n' \
            'hb:/track/name\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testIncorrectPreprocessedFileFormatHeaderNoColumn(self):
        contents = \
            '##file format: preprocessed\n' \
            '###uri\n' \
            'file:/path/to/file.bed\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testIncorrectMultipleTrackTypeHeaderNoColumn(self):
        contents = \
            '##track type: multiple\n' \
            '###uri\n' \
            'hb:/track/name\n' \
            'file:/path/to/file.bed\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testIncorrectMultipleGenomeHeaderNoColumn(self):
        contents = \
            '##genome: multiple\n' \
            '###uri\n' \
            'hb:/track/name\n' \
            'file:/path/to/file.bed\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testMultipleTracksSameUrl(self):
        contents = \
            '###uri\ttitle\n' \
            'hb:/track/name\tTrack\n' \
            'hb:/track/name\tTrack2\n' \

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testMultipleTracksSameTitle(self):
        contents = \
            '###uri\ttitle\n' \
            'hb:/track/name\tTrack\n' \
            'file:/path/to/file.bed\tTrack\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    ## Deprecated, but still allowed:

    def testErrorInGenomeLine(self):
        contents = \
            '####hg18\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testErrorInGenomeLine2(self):
        contents = \
            '####genome:hg18\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testErrorInGenomeLine3(self):
        contents = \
            '####genomes=hg18\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testWrongHeaderOrder1(self):
        contents = \
            '####genome=hg19\n' \
            '###uri\ttitle\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testWrongHeaderOrder2(self):
        contents = \
            '####genome=hg19\n' \
            '##key: value\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testDoubleGenomeLine(self):
        contents = \
            '####genome=hg19\n' \
            '####genome=hg19\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testTrackBeforeGenomeLine(self):
        contents = \
            'hb://trackname\n' \
            '####genome=hg19\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    ##

    def testWrongHeaderOrder3(self):
        contents = \
            '###uri\ttitle\n' \
            '##key: value\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testDoubleVariableLine(self):
        contents = \
            '##track type: segments\n' \
            '##track type: points\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testDoubleColSpecLine(self):
        contents = \
            '###uri\ttitle\n' \
            '###uri\ttitle\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testTrackBeforeHeaderLine(self):
        contents = \
            'hb://trackname\n' \
            '##key=value\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testTrackBeforeColSpecLine(self):
        contents = \
            'hb://trackname\n' \
            '###uri\ttitle\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testInvalidChar(self):
        contents = \
            'hb://track name %s\n' % chr(134)

        #self._parseContents(contents)3
        self._assertInvalidFormatWhenParsing(contents)

    def testInvalidProtocol(self):
        contents = \
            'fttp://server.somewhere.com/path/to/file1.bed\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testMalformedUriLocalNoProtocol(self):
        contents = \
            'track/name/hierarchy\n' \

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testMalformedUriLocalNoSlash(self):
        contents = \
            'hb:track/name/hierarchy\n' \

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testMalformedUriRemoteNoNetloc(self):
        contents = \
            'ftp:/path/to/file\n' \

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)
    #
    #def testMalformedUriTextWithQueryFtp(self):
    #    contents = \
    #        'ftp://server.somewhere.com/path/to/file1.bed?track:name\n'
    #
    #    #self._parseContents(contents)
    #    self._assertInvalidFormatWhenParsing(contents)


    def testMalformedUriHbWithQuery(self):
        contents = \
            'hb:/track/name/hierarchy?track=track:name\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    #def testMalformedUriHierarchicalGalaxyPath(self):
    #    contents = \
    #        'galaxy:/ad123dd12fg/path/to/filename.bed\n\n'
    #
    #    #self._parseContents(contents)
    #    self._assertInvalidFormatWhenParsing(contents)

    def testMalformedUriFileUnknownWithQuote(self):
        contents = \
            'file:/path/to/file?track=track:name\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testMalformedUriFileTrackNameWithoutKey(self):
        contents = \
            'file:/path/to/file.btrack?track:name\n'

        #self._parseContents(contents)
        self._assertValueErrorWhenParsing(contents)


    def testMalformedUriWithFragment(self):
        contents = \
            'http://server.other.com/path/to/file2.bed#part1\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testMalformedUriHbWithSuffix(self):
        contents = \
            'hb:/track/name;bed\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testIncorrectTrackColumnCount(self):
        contents = \
            '###uri\tantibody\tcell\n' \
            'file:/path/to/file.bed\tcMyb\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testInvalidFileFormatInTrack(self):
        contents = \
            '###uri\tfile_format\n' \
            'ftp://server.somewhere.com/path/to/file1.bed\tstring\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testInvalidFileFormatInHbTrack(self):
        contents = \
            '###uri\tfile_format\n' \
            'hb:/track/name\tprimary\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testInvalidTrackTypeInTrack(self):
        contents = \
            '###uri\ttrack_type\n' \
            'ftp://server.somewhere.com/path/to/file1.bed\tsegmentation\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testErrorInGenomeHeader(self):
        contents = \
            '##genome: .\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def testEmptyMetaDataCell(self):
        contents = \
            '###uri\tantibody\tcell\textra\n' \
            'file:/path/to/file.bed\tcMyb\t\t.\n'

        #self._parseContents(contents)
        self._assertInvalidFormatWhenParsing(contents)

    def runTest(self):
        pass

if __name__ == "__main__":
    #TestGtrackSuite().debug()
    unittest.main()
