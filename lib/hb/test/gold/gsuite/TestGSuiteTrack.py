import unittest
from collections import OrderedDict
from gold.gsuite.GSuiteTrack import GSuiteTrack, FtpGSuiteTrack, HttpGSuiteTrack, \
                                    HttpsGSuiteTrack, RsyncGSuiteTrack, HbGSuiteTrack, \
                                    GalaxyGSuiteTrack, FileGSuiteTrack
from gold.util.CustomExceptions import InvalidFormatError

from test.gold.gsuite.GSuiteTestWithMockEncodingFuncs import GSuiteTestWithMockEncodingFuncs

class TestGSuiteTrack(GSuiteTestWithMockEncodingFuncs):
    def testCreateGSuiteTrackDefaults(self):
        track = GSuiteTrack('ftp://server/path/to/file')
        self.assertEquals('ftp', track.scheme)
        self.assertEquals('ftp://server/path/to/file', track.uri)
        self.assertEquals('server', track.netloc)
        self.assertEquals('/path/to/file', track.path)
        self.assertEquals(None, track.query)
        self.assertEquals(None, track.suffix)
        self.assertEquals('file', track.title)
        self.assertEquals(None, track.trackName)
        self.assertEquals('remote', track.location)
        self.assertEquals('unknown', track.fileFormat)
        self.assertEquals('unknown', track.trackType)
        self.assertEquals('unknown', track.genome)
        self.assertEquals(OrderedDict(), track.attributes)


    def testCreateRemoteGSuiteTrack(self):
        for scheme, cls in [('ftp', FtpGSuiteTrack), ('http', HttpGSuiteTrack),
                            ('https', HttpsGSuiteTrack), ('rsync', RsyncGSuiteTrack)]:
            uri = cls.generateURI(netloc='server.com', path='/path/to/file',
                                  suffix='btrack', trackName=['trackname'], doQuote=False)
            track = GSuiteTrack(uri, title='MyTrack', fileFormat='preprocessed',
                                trackType='segments', genome='TestGenome',
                                attributes=OrderedDict([('extra', 'yes')]))
            track.trackName

            self.assertEquals(scheme + '://server.com/path/to/file;btrack?track=trackname', uri)
            self.assertEquals(scheme, track.scheme)
            self.assertEquals(scheme + '://server.com/path/to/file;btrack?track=trackname', track.uri)
            self.assertEquals('server.com', track.netloc)
            self.assertEquals('/path/to/file', track.path)
            self.assertEquals('track=trackname', track.query)
            self.assertEquals('btrack', track.suffix)
            self.assertEquals('MyTrack', track.title)
            self.assertEquals(['trackname'], track.trackName)
            self.assertEquals('remote', track.location)
            self.assertEquals('preprocessed', track.fileFormat)
            self.assertEquals('segments', track.trackType)
            self.assertEquals('TestGenome', track.genome)
            self.assertEquals(OrderedDict([('extra', 'yes')]), track.attributes)


    def testCreateHbGSuiteTrack(self):
        uri = HbGSuiteTrack.generateURI(trackName=['My', 'track name', 'hierarchy'], doQuote=True)
        track = GSuiteTrack(uri, title='MyTrack', fileFormat='preprocessed',
                            trackType='points', genome='hg19',
                            attributes=OrderedDict([('extra', 'yes')]))

        self.assertEquals('hb:/My/track%20name/hierarchy', uri)
        self.assertEquals('hb', track.scheme)
        self.assertEquals('hb:/My/track%20name/hierarchy', track.uri)
        self.assertEquals(None, track.netloc)
        self.assertEquals(None, track.path)
        self.assertEquals(None, track.query)
        self.assertEquals(None, track.suffix)
        self.assertEquals('MyTrack', track.title)
        self.assertEquals(['My', 'track name', 'hierarchy'], track.trackName)
        self.assertEquals('local', track.location)
        self.assertEquals('preprocessed', track.fileFormat)
        self.assertEquals('points', track.trackType)
        self.assertEquals('hg19', track.genome)
        self.assertEquals(OrderedDict([('extra', 'yes')]), track.attributes)


    def testCreateGalaxyGSuiteTrack(self):
        uri = GalaxyGSuiteTrack.generateURI(galaxyFn='/path/to/dataset_12345.dat',
                                            extraFileName='specific_file',
                                            trackName=['trackname'],
                                            suffix='btrack', doQuote=False)
        track = GSuiteTrack(uri, title='MyTrack', fileFormat='preprocessed',
                            trackType='points', genome='mm9',
                            attributes=OrderedDict([('extra', 'yes')]))

        self.assertEquals('galaxy:/9085014203344132088/specific_file;btrack?track=trackname', uri)
        self.assertEquals('galaxy', track.scheme)
        self.assertEquals('galaxy:/9085014203344132088/specific_file;btrack?track=trackname', track.uri)
        self.assertEquals(None, track.netloc)
        self.assertEquals('/path/to/dataset_9085014203344132088_files/specific_file', track.path)
        self.assertEquals('track=trackname', track.query)
        self.assertEquals('btrack', track.suffix)
        self.assertEquals('MyTrack', track.title)
        self.assertEquals(['trackname'], track.trackName)
        self.assertEquals('local', track.location)
        self.assertEquals('preprocessed', track.fileFormat)
        self.assertEquals('points', track.trackType)
        self.assertEquals('mm9', track.genome)
        self.assertEquals(OrderedDict([('extra', 'yes')]), track.attributes)


    def testCreateFileGSuiteTrack(self):
        uri = FileGSuiteTrack.generateURI(path='/path/to/file', suffix='btrack',
                                          trackName=['trackname'], doQuote=False)
        track = GSuiteTrack(uri, title='MyTrack', trackType='segments', genome='unknown',
                            attributes=OrderedDict([('extra', 'no')]))

        self.assertEquals('file:/path/to/file;btrack?track=trackname', uri)
        self.assertEquals('file', track.scheme)
        self.assertEquals('file:/path/to/file;btrack?track=trackname', track.uri)
        self.assertEquals(None, track.netloc)
        self.assertEquals('/path/to/file', track.path)
        self.assertEquals('track=trackname', track.query)
        self.assertEquals('btrack', track.suffix)
        self.assertEquals('MyTrack', track.title)
        self.assertEquals(['trackname'], track.trackName)
        self.assertEquals('local', track.location)
        self.assertEquals('preprocessed', track.fileFormat)
        self.assertEquals('segments', track.trackType)
        self.assertEquals('unknown', track.genome)
        self.assertEquals(OrderedDict([('extra', 'no')]), track.attributes)


    #TODO: Add test for changing properties

    def testQuoteInURLRemote(self):
        for scheme, cls in [('ftp', FtpGSuiteTrack), ('http', HttpGSuiteTrack),
                            ('https', HttpsGSuiteTrack), ('rsync', RsyncGSuiteTrack)]:
            uri = cls.generateURI(netloc='server.com%7C', path='/path/to/file_with%20%3B%22%5B',
                                  suffix='bed%7C%2F', query='search=%2Aab&track=My%3Atrack+name%3B%22%5B%3Ahierarchy', doQuote=False)
            track = GSuiteTrack(uri)

            self.assertEquals(scheme + '://server.com%7C/path/to/file_with%20%3B%22%5B;bed%7C%2F?search=%2Aab&track=My%3Atrack+name%3B%22%5B%3Ahierarchy', uri)
            self.assertEquals(scheme, track.scheme)
            self.assertEquals(scheme + '://server.com%7C/path/to/file_with%20%3B%22%5B;bed%7C%2F?search=%2Aab&track=My%3Atrack+name%3B%22%5B%3Ahierarchy', track.uri)
            self.assertEquals('server.com|', track.netloc)
            self.assertEquals('/path/to/file_with ;"[', track.path)
            self.assertEquals('hierarchy', track.title)
            self.assertEquals('bed|/', track.suffix)
            self.assertEquals('search=*ab&track=My:track name;"[:hierarchy', track.query)
            self.assertEquals(['My', 'track name;"[', 'hierarchy'], track.trackName)
            

            uri = cls.generateURI(netloc='server.com|', path='/path/to/file_with ;"[',
                                  suffix='btrack|/', trackName=['My', 'track name;"[', 'hierarchy'], doQuote=True)
            track = GSuiteTrack(uri)

            self.assertEquals(scheme + '://server.com%7C/path/to/file_with%20%3B%22%5B;btrack%7C%2F?track=My%3Atrack+name%3B%22%5B%3Ahierarchy', uri)
            self.assertEquals(scheme, track.scheme)
            self.assertEquals(scheme + '://server.com%7C/path/to/file_with%20%3B%22%5B;btrack%7C%2F?track=My%3Atrack+name%3B%22%5B%3Ahierarchy', track.uri)
            self.assertEquals('server.com|', track.netloc)
            self.assertEquals('/path/to/file_with ;"[', track.path)
            self.assertEquals('hierarchy', track.title)
            self.assertEquals('btrack|/', track.suffix)
            self.assertEquals('track=My:track name;"[:hierarchy', track.query)
            self.assertEquals(['My', 'track name;"[', 'hierarchy'], track.trackName) # Temporarily, should be fixed if remote BTracks are supported


    def testQuoteInURLHb(self):
        uri = HbGSuiteTrack.generateURI(trackName=['My', 'track name;"[', 'hierarchy'], doQuote=True)
        track = GSuiteTrack(uri)

        self.assertEquals('hb:/My/track%20name%3B%22%5B/hierarchy', track.uri)
        self.assertEquals('hb', track.scheme)
        self.assertEquals('hb:/My/track%20name%3B%22%5B/hierarchy', track.uri)
        self.assertEquals(['My', 'track name;"[', 'hierarchy'], track.trackName)
        self.assertEquals('hierarchy', track.title)


    def testQuoteInURLGalaxy(self):
        uri = GalaxyGSuiteTrack.generateURI(galaxyFn='/path/to/dataset_12345.dat',
                                            extraFileName='file_with ;"[',
                                            suffix='btrack', trackName=['My', 'track ;"[', 'name'], doQuote=True)
        track = GSuiteTrack(uri)

        self.assertEquals('galaxy:/9085014203344132088/file_with%20%3B%22%5B;btrack?track=My%3Atrack+%3B%22%5B%3Aname', uri)
        self.assertEquals('galaxy', track.scheme)
        self.assertEquals('galaxy:/9085014203344132088/file_with%20%3B%22%5B;btrack?track=My%3Atrack+%3B%22%5B%3Aname', track.uri)
        self.assertEquals(None, track.netloc)
        self.assertEquals('/path/to/dataset_9085014203344132088_files/file_with ;"[', track.path)
        self.assertEquals('name', track.title)
        self.assertEquals('btrack', track.suffix)
        self.assertEquals('track=My:track ;"[:name', track.query)
        self.assertEquals(['My', 'track ;"[', 'name'], track.trackName)


    def testQuoteInURLFile(self):
        uri = FileGSuiteTrack.generateURI(path='/path/to/file_with ;"[', suffix='btrack',
                                          trackName=['My', 'track ;"[', 'name'], doQuote=True)
        track = GSuiteTrack(uri, fileFormat='preprocessed', trackType='segments')

        self.assertEquals('file:/path/to/file_with%20%3B%22%5B;btrack?track=My%3Atrack+%3B%22%5B%3Aname', uri)
        self.assertEquals('file', track.scheme)
        self.assertEquals('file:/path/to/file_with%20%3B%22%5B;btrack?track=My%3Atrack+%3B%22%5B%3Aname', track.uri)
        self.assertEquals('/path/to/file_with ;"[', track.path)
        self.assertEquals('name', track.title)
        self.assertEquals('track=My:track ;"[:name', track.query)
        self.assertEquals(['My', 'track ;"[', 'name'], track.trackName)
        self.assertEquals('btrack', track.suffix)


    def testSetProperties(self):
        track = GSuiteTrack('http://server.com/path/to/file.bed')

        self.assertRaises(AttributeError, track.__setattr__, 'uri', 'http://server.comm/path/to/other.bed')
        self.assertRaises(AttributeError, track.__setattr__, 'uriWithoutSuffix', 'http://server.com/path/to/other')
        self.assertRaises(AttributeError, track.__setattr__, 'scheme', 'https')
        self.assertRaises(AttributeError, track.__setattr__, 'netloc', 'other.com')
        self.assertRaises(AttributeError, track.__setattr__, 'path', '/path/to/other.bed')
        self.assertRaises(AttributeError, track.__setattr__, 'query', 'download=true')
        self.assertRaises(AttributeError, track.__setattr__, 'trackName', ['track','name'])
        self.assertRaises(AttributeError, track.__setattr__, 'suffix', 'wig')
        self.assertRaises(AttributeError, track.__setattr__, 'location', 'local')

        track.title = 'Title'
        self.assertEquals('Title', track.title)

        track.fileFormat = 'unknown'
        self.assertEquals('unknown', track.fileFormat)

        track.trackType = 'segments'
        self.assertEquals('segments', track.trackType)

        track.genome = 'hg19'
        self.assertEquals('hg19', track.genome)

        track.attributes = OrderedDict([('a', '123'), ('b', '234')])
        self.assertEquals(OrderedDict([('a', '123'), ('b', '234')]), track.attributes)
        self.assertEquals('123', track.a)
        self.assertEquals('234', track.getAttribute('b'))

        track.setAttribute('c', '345')
        self.assertEquals('345', track.getAttribute('c'))

        track.comment = 'Comment'
        self.assertEquals('Comment', track.comment)


    def testIncorrectFileFormat(self):
        uri = FileGSuiteTrack.generateURI(path='/path/to/file')
        #track = GSuiteTrack(uri, fileFormat='doc')
        self.assertRaises(InvalidFormatError, GSuiteTrack, uri, fileFormat='doc')

        track = GSuiteTrack(uri)
        #track.fileFormat = 'doc'
        self.assertRaises(InvalidFormatError, track.__setattr__, 'fileFormat', 'doc')


    def testIncorrectFileFormatGalaxy(self):
        uri = GalaxyGSuiteTrack.generateURI(galaxyFn='/path/to/file')
        #track = GSuiteTrack(uri, fileFormat='doc')
        self.assertRaises(InvalidFormatError, GSuiteTrack, uri, fileFormat='doc')

        track = GSuiteTrack(uri)
        #track.fileFormat = 'doc'
        self.assertRaises(InvalidFormatError, track.__setattr__, 'fileFormat', 'doc')


    def testIncorrectTrackType(self):
        uri = FileGSuiteTrack.generateURI(path='/path/to/file')
        #track = GSuiteTrack(uri, trackType='segment')
        self.assertRaises(InvalidFormatError, GSuiteTrack, uri, trackType='segment')

        track = GSuiteTrack(uri)
        #track.trackType = 'segment'
        self.assertRaises(InvalidFormatError, track.__setattr__, 'trackType', 'segment')


    def runTest(self):
        pass


if __name__ == "__main__":
    #TestGSuiteTrack().debug()
    unittest.main()
