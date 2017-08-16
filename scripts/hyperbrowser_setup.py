import sys, os

galaxy_dir = os.path.sep.join(os.path.realpath(__file__).split(os.path.sep)[:-2])
new_path = [os.path.join(galaxy_dir, "lib")]
new_path.extend(sys.path[1:])  # remove scripts/ from the path
sys.path = new_path


def extractTestGenomeAndPreProcess(galaxy_dir):
    hbPath = os.path.join(galaxy_dir, 'lib', 'hb')
    from config.Config import ORIG_DATA_PATH
    from gold.origdata.PreProcessTracksJob import PreProcessAllTracksJob
    from setup.InstallFunctions import executeShellCmd
    from gold.util.CommonFunctions import createDirPath
    from quick.util.GenomeInfo import GenomeInfo
    from quick.application.ProcTrackOptions import ProcTrackOptions
    from gold.description.TrackInfo import TrackInfo
    import shutil

    testGenomeFn = os.sep.join([hbPath, 'data', 'TestGenome.tar.gz'])
    executeShellCmd('tar xfz %s --keep-newer-files -C %s' % (testGenomeFn, ORIG_DATA_PATH), \
                    pipe=False, printError=True, onError='exit')
    print 'OK: Extracted TestGenome files.'

    PreProcessAllTracksJob.PASS_ON_EXCEPTIONS = True
    try:
        PreProcessAllTracksJob('TestGenome').process()
        PreProcessAllTracksJob('TestGenome', GenomeInfo.getChrTrackName('TestGenome')).process()
        print 'OK: Finished preprocessing TestGenome.'
    except Exception, e:
        print 'FAILED: Error when preprocessing TestGenome. Error:'
        print '        ' + str(e).strip()
        sys.exit(1)

    for allowOverlaps in [False, True]:
        fromDir = createDirPath(['GESourceTracks'], 'TestGenome', allowOverlaps=allowOverlaps)
        toDir = createDirPath([], 'ModelsForExternalTracks', allowOverlaps=allowOverlaps)
        try:
            if not os.path.exists(toDir):
                shutil.copytree(fromDir, toDir)
                print 'OK: Copied from %s to %s.' % (fromDir, toDir)
        except Exception, e:
            print 'FAILED: Error occurred copying from %s to %s: ' % (fromDir, toDir) + str(e).strip()
            sys.exit(1)

    for track in ProcTrackOptions.getSubtypes('TestGenome', ['GESourceTracks']):
        ti = TrackInfo('TestGenome', ['GESourceTracks', track])
        ti.trackName = [track]
        ti.genome = 'ModelsForExternalTracks'
        ti.store()

    from quick.util.GenomeInfo import GenomeInfo
    from datetime import datetime
    gi = GenomeInfo('TestGenome')
    gi.fullName = 'TestGenome'
    gi.sourceUrls = ['http://hgdownload.cse.ucsc.edu/goldenPath/hg18/chromosomes/chr21.fa.gz', \
                     'http://hgdownload.cse.ucsc.edu/goldenPath/hg18/chromosomes/chrM.fa.gz']
    #gi.sourceChrNames = ['chr21', 'chrM']
    gi.installedBy = 'Setup.py'
    gi.genomeBuildSource = 'NCBI'
    gi.genomeBuildName = 'hg18'
    gi.species = 'Homo Sapiens'
    gi.speciesTaxonomyUrl = 'http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id=9606'
    gi.assemblyDetails = 'Chromosome 21 and M from the hg18 genome, used for testing purposes.'
    gi.isPrivate = False
    gi.privateAccessList = []
    gi.isExperimental = False
    gi.timeOfInstallation = datetime.now()
    gi.store()

extractTestGenomeAndPreProcess(galaxy_dir)
