import unittest
from collections import OrderedDict

from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GSuiteTrack
import gold.gsuite.GSuiteComposer as GSuiteComposer
import gold.gsuite.GSuiteParser as GSuiteParser

from test.gold.gsuite.GSuiteTestWithMockEncodingFuncs import GSuiteTestWithMockEncodingFuncs

class TestGSuiteComposer(GSuiteTestWithMockEncodingFuncs):
    def testEmptyCompose(self):
        gSuite = GSuite()

        output = GSuiteComposer.composeToString(gSuite)

        targetOutput = \
            '##location: unknown\n' \
            '##file format: unknown\n' \
            '##track type: unknown\n' \
            '##genome: unknown\n'

        self.assertEquals(targetOutput, output)


    def testComposeRemoteOnlyUrl(self):
        gSuite = GSuite()
        gSuite.addTrack(GSuiteTrack('ftp://server.somewhere.com/path/to/file1'))
        gSuite.addTrack(GSuiteTrack('http://server.other.com/path/to/file2'))

        output = GSuiteComposer.composeToString(gSuite)

        targetOutput = \
            '##location: remote\n' \
            '##file format: unknown\n' \
            '##track type: unknown\n' \
            '##genome: unknown\n' \
            '###uri\ttitle\n' \
            'ftp://server.somewhere.com/path/to/file1\tfile1\n' \
            'http://server.other.com/path/to/file2\tfile2\n'

        self.assertEquals(targetOutput, output)


    def testComposeRemoteUrlGenomeFileFormat(self):
        gSuite = GSuite()
        gSuite.addTrack(GSuiteTrack('ftp://server.somewhere.com/path/to/file1.bed', genome='hg18'))
        gSuite.addTrack(GSuiteTrack('http://server.other.com/path/to/file2', genome='hg18'))

        output = GSuiteComposer.composeToString(gSuite)

        targetOutput = \
            '##location: remote\n' \
            '##file format: unknown\n' \
            '##track type: unknown\n' \
            '##genome: hg18\n' \
            '###uri\ttitle\tfile_format\n' \
            'ftp://server.somewhere.com/path/to/file1.bed\tfile1.bed\tprimary\n' \
            'http://server.other.com/path/to/file2\tfile2\tunknown\n'

        self.assertEquals(targetOutput, output)


    def testComposeUrlTitleLocationTrackType(self):
        gSuite = GSuite()
        gSuite.addTrack(GSuiteTrack('ftp://server.somewhere.com/path/to/file1',
                                    title='Track1', trackType='points'))
        gSuite.addTrack(GSuiteTrack('file:/path/to/file2',
                                    trackType='segments'))

        output = GSuiteComposer.composeToString(gSuite)

        targetOutput = \
            '##location: multiple\n' \
            '##file format: unknown\n' \
            '##track type: multiple\n' \
            '##genome: unknown\n' \
            '###uri\ttitle\ttrack_type\n' \
            'ftp://server.somewhere.com/path/to/file1\tTrack1\tpoints\n' \
            'file:/path/to/file2\tfile2\tsegments\n'

        self.assertEquals(targetOutput, output)


    def testComposeLocalUrlGenomeAttributes(self):
        gSuite = GSuite()
        gSuite.addTrack(GSuiteTrack('galaxy:/12345abc', genome='hg18',
                                    attributes=OrderedDict([('one', 'yes')])))
        gSuite.addTrack(GSuiteTrack('file:/path/to/file2', genome='hg19',
                                    attributes=OrderedDict([('two', 'no')])))
        
        output = GSuiteComposer.composeToString(gSuite)

        targetOutput = \
            '##location: local\n' \
            '##file format: unknown\n' \
            '##track type: unknown\n' \
            '##genome: multiple\n' \
            '###uri\ttitle\tgenome\tone\ttwo\n' \
            'galaxy:/12345abc\t12345abc\thg18\tyes\t.\n' \
            'file:/path/to/file2\tfile2\thg19\t.\tno\n'

        self.assertEquals(targetOutput, output)


    def testFullCompose(self):
        gSuite = GSuite()
        gSuite.addTrack(GSuiteTrack('ftp://server.somewhere.com/path/to/file1.bed',
                                    title='Track', \
                                    attributes=OrderedDict([('cell', 'k562'),
                                                            ('antibody', 'cMyb')])))
        gSuite.addTrack(GSuiteTrack('http://server.other.com/path/to/file2.bed',
                                    title='Track2', \
                                    attributes=OrderedDict([('cell', 'GM12878'),
                                                            ('antibody', 'cMyc')])))
        gSuite.addTrack(GSuiteTrack('https://server.other.com/path/to/file3.bed',
                                    attributes=OrderedDict([('cell', 'GM12878'),
                                                            ('antibody', 'cMyb')])))
        gSuite.addTrack(GSuiteTrack('rsync://server.other.com/path/to/file4;wig',
                                    title='Track4', \
                                    attributes=OrderedDict([('cell', 'NHFL')])))
        gSuite.addTrack(GSuiteTrack('hb:/track/name/hierarchy',
                                    title='Track'))
        gSuite.addTrack(GSuiteTrack('galaxy:/ad123dd12fg;btrack?track=track:name',
                                    title='Track', \
                                    attributes=OrderedDict([('cell', 'k562'),
                                                            ('antibody', 'cMyb')])))
        gSuite.addTrack(GSuiteTrack('file:/path/to/file.btrack?track=track:name',
                                    title='Track name7', \
                                    attributes=OrderedDict([('antibody', 'cMyb'),
                                                            ('extra', 'yes')])))
        gSuite.setGenomeOfAllTracks('hg18')

        output = GSuiteComposer.composeToString(gSuite)

        targetOutput = \
            '##location: multiple\n' \
            '##file format: multiple\n' \
            '##track type: unknown\n' \
            '##genome: hg18\n' \
            '###uri\ttitle\tfile_format\tcell\tantibody\textra\n' \
            'ftp://server.somewhere.com/path/to/file1.bed\tTrack\tprimary\tk562\tcMyb\t.\n' \
            'http://server.other.com/path/to/file2.bed\tTrack2\tprimary\tGM12878\tcMyc\t.\n' \
            'https://server.other.com/path/to/file3.bed\tfile3.bed\tprimary\tGM12878\tcMyb\t.\n' \
            'rsync://server.other.com/path/to/file4;wig\tTrack4\tprimary\tNHFL\t.\t.\n' \
            'hb:/track/name/hierarchy\tTrack (2)\tpreprocessed\t.\t.\t.\n' \
            'galaxy:/ad123dd12fg;btrack?track=track%3Aname\tTrack (3)\tpreprocessed\tk562\tcMyb\t.\n' \
            'file:/path/to/file.btrack?track=track%3Aname\tTrack name7\tpreprocessed\t.\tcMyb\tyes\n'

        self.assertEquals(targetOutput, output)


    def testParseAndCompose(self):
        inputContents = \
            '##location: multiple\n' \
            '##file format: multiple\n' \
            '##track type: unknown\n' \
            '##genome: hg18\n' \
            '###uri\ttitle\tfile_format\tcell\tantibody\textra\n' \
            'ftp://server.somewhere.com/path/to/file1.bed\tTrack1\tprimary\tk562\tcMyb\t.\n' \
            'http://server.other.com/path/to/file2.bed\tTrack2\tprimary\tGM12878\tcMyc\t.\n' \
            'https://server.other.com/path/to/file3.bed\tfile3.bed\tprimary\tGM12878\tcMyb\t.\n' \
            'rsync://server.other.com/path/to/file4;wig\tTrack4\tprimary\tNHFL\t.\t.\n' \
            'hb:/track/name/hierarchy\tTrack5\tpreprocessed\t.\t.\t.\n' \
            'galaxy:/ad123dd12fg;btrack?track=track%3Aname\tTrack6\tpreprocessed\tk562\tcMyb\t.\n' \
            'file:/path/to/file.btrack?track=track%3Aname\tTrack name7\tpreprocessed\t.\tcMyb\tyes\n'

        gSuite = GSuiteParser.parseLines(inputContents.split('\n'))
        outputContents = GSuiteComposer.composeToString(gSuite)

        self.assertEquals(inputContents, outputContents)


    def runTest(self):
        pass

if __name__ == "__main__":
    #TestGSuite().debug()
    unittest.main()
