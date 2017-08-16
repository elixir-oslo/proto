#!python

import sys
import os, os.path
from getopt import GetoptError, getopt
from collections import OrderedDict
from setup.ShellCommands import ShellCommands

def checkDependencies():
    from quick.util.InstallFunctions import executeShellCmd
    pythonVersion = sys.version_info[:2]
    if pythonVersion == ( 2, 7 ):
        print 'OK: Python version as required (2.7).'
    else:
        print 'FAILED: Requires Python version 2.7. Current: %s' % pythonVersion
        sys.exit(1)

    # r = executeShellCmd('Xvfb -help > /dev/null 2>&1', pipe=False, onError='nothing')
    # if r:
    #     print 'FAILED: Requires Xvfb.'
    #     sys.exit(1)
    # else:
    #     print 'OK: Xvfb found.'

    v = executeShellCmd('''perl -Mstrict -wall -e "print join('.', map {ord} split('', \$^V));"''', pipe=True, onError='nothing')
    if float(v.strip()[:3]) < 5.8:
        print 'FAILED: Requires perl > 5.8'
        sys.exit(1)
    else:
        print 'OK: perl found.'

    r = executeShellCmd('pkg-config pkg-config > /dev/null 2>&1', pipe=False, onError='nothing')
    if r:
        print 'FAILED: Requires pkg-config.'
        sys.exit(1)
    else:
        print 'OK: pkg-config found.'

    r = executeShellCmd('pkg-config ImageMagick --atleast-version=6.2.8', pipe=False, onError='nothing')
    if r:
        print 'FAILED: Requires ImageMagick >= 6.2.8'
        sys.exit(1)
    else:
        print 'OK: ImageMagick found.'

    r = executeShellCmd('pkg-config cairo --atleast-version=1.8.8', pipe=False, onError='nothing')
    if r:
        print 'FAILED: Requires cairo >= 1.8.8'
        sys.exit(1)
    else:
        print 'OK: Cairo found.'

    r = executeShellCmd('pkg-config libzmq --atleast-version=2.1.10', pipe=False, onError='nothing')
    if r:
        print 'FAILED: Requires libzmq >= 2.1.10.'
        sys.exit(1)
    else:
        print 'OK: Libzmq found.'

    r = executeShellCmd('rsync --help > /dev/null 2>&1', pipe=False, onError='nothing')
    if r:
        print 'FAILED: Requires rsync.'
        sys.exit(1)
    else:
        print 'OK: rsync found.'

    # from ez_setup import use_setuptools
    # use_setuptools()
    import pkg_resources

    try:
        ver = pkg_resources.require('numpy >= 1.8')
        print 'OK: Numpy version >= 1.8 found: %s' % ver
    except:
        print 'FAILED: Requires Numpy version >= 1.8.'
        sys.exit(1)

    try:
        ver = pkg_resources.require('rpy2 >= 2.7')
        print 'OK: rpy2 version >= 2.7 found: %s' % ver
    except:
        print 'FAILED: Requires rpy2 version >= 2.7.'
        sys.exit(1)

    from proto.RSetup import getRVersion
    rVersion = getRVersion()
    if rVersion >= '3.2':
        print 'OK: R version >= 3.2 found: %s' % rVersion
    else:
        print 'FAILED: Requires R version >= 3.2. Version %s found.' % rVersion

def setupAllInstallationSpecificSetupFiles(hbPath, installationSetupFn):
    extConfigDict = {'HB_CONFIG_BASE_DIR': hbPath + '/config', \
                     'HB_SETUP_CONFIG_BASE_DIR': hbPath + '/config/setup'}

    if not installationSetupFn:
        installationSetupFn = os.sep.join([hbPath, 'config', 'setup', 'default', 'default.setup'])

    if not os.path.exists(installationSetupFn):
        print 'FAILED: The installation setup file (%s) does not exist' % installationSetupFn
        sys.exit(1)

    ShellCommands(installationSetupFn, extConfigDict).apply()

def getWorkingGalaxyPath(galaxyPath):
    if not galaxyPath:
        import config.LocalOSConfig
        galaxyPath = config.LocalOSConfig.__dict__.get('GALAXY_BASE_DIR')
        if not galaxyPath:
            print 'FAILED: LocalOSConfig.py har no GALAXY_BASE_DIR config key. ' + \
                  'Please specify the Galaxy installation path as argument to setup.py (-g PATH).'
            sys.exit(1)

    if not os.path.exists(galaxyPath):
        print 'FAILED: The Galaxy installation path (%s) does not exist.' % galaxyPath
        sys.exit(1)

    if galaxyPath[0] != os.sep:
        print 'FAILED: The Galaxy installation path (%s) must be an absolute path.' % galaxyPath
        sys.exit(1)

    if galaxyPath[-1] == os.sep:
        galaxyPath = galaxyPath[:-1]

    return galaxyPath

def checkGalaxyVersion(hbPath, galaxyPath):
    from quick.util.InstallFunctions import executeShellCmd
    #from config.Config import GALAXY_VERSION
    reqVersion = ''
    configFileFn = os.sep.join([hbPath, 'config', 'Config.py'])
    configLines = [line for line in open(configFileFn)]

    for i,line in enumerate(configLines):
        if 'GALAXY_VERSION' in line:
            reqVersion = configLines[i].split('=')[1].strip()[1:-1]

    if not reqVersion:
        print 'FAILED: Not able to read Galaxy version from file: config/Config.py.'
        sys.exit(1)

    try:
        installedVersion = executeShellCmd("hg -R %s parents --template '{node|short}'" \
                                           % galaxyPath, printError=False, onError='exception')
    except Exception, e1:
        print 'FAILED: Not able to retrieve the installed Galaxy version. Errors as follows:'
        print '        ' + str(e1).strip()
        print '        Galaxy version checking is only supported on Galaxy installations using mercury.'
        print '        Please make sure that your Galaxy installation has the correct version and rerun'
        print '        the setup.py file with the -i option. Required version: ' + reqVersion
        sys.exit(1)
        #try:
        #    out = executeShellCmd("grep node %s/.hg_archival.txt" % galaxyPath, \
        #                          printError=False, onError='exception')
        #    installedVersion = out.split(':')[1].strip()[:12]
        #except Exception, e2:
        #    print 'FAILED: Not able to retrieve installed Galaxy version. Errors as follows:'
        #    print '        ' + str(e1).strip()
        #    print '        ' + str(e2).strip()
        #    sys.exit(1)

    if installedVersion != reqVersion:
        print 'FAILED: Installed Galaxy version is not the one required for this version of the Genomic HyperBrowser.'
        print '        %s (installed) != %s (required).' % (installedVersion, reqVersion)
        sys.exit(1)
    else:
        print 'OK: Galaxy version as required (%s)' % reqVersion

def _addPathsToLocalOSConfigIfNecessary(configDict, hbPath):
    configFileFn = os.sep.join([hbPath, 'config', 'LocalOSConfig.py'])
    configLines = [line for line in open(configFileFn)]

    newLines = ''
    for key in configDict.keys():
        found = False
        for i,line in enumerate(configLines):
            if key in line:
                found = True
                storedVal = configLines[i].split('=')[1].strip()[1:-1]
                if configDict[key] != storedVal:
                    print 'FAILED: %s (%s) is not equal to path stored in LocalOSConfig (%s).' \
                          % (key, configDict[key], storedVal)
                    sys.exit(1)
        if not found:
            newLines += "%s = '%s'" % (key, configDict[key]) + os.linesep

    if newLines:
        newLines += os.linesep
        configFile = open(configFileFn, 'w')
        configFile.write(newLines)
        configFile.write(''.join(configLines))
        configFile.close()

    return True

def addPathsToLocalOSConfigIfNecessary(hbPath, galaxyPath):
    baseConfigDict = OrderedDict()
    baseConfigDict['HB_SOURCE_CODE_BASE_DIR'] = hbPath
    baseConfigDict['GALAXY_BASE_DIR'] = galaxyPath

    return _addPathsToLocalOSConfigIfNecessary(baseConfigDict, hbPath)

def _installAndCheckRLibrary(library):
    from proto.RSetup import r
    from config.Config import HB_R_LIBS_DIR
    from quick.util.CommonFunctions import silenceRWarnings, silenceROutput
    silenceRWarnings()
    silenceROutput()

    try:
        raise Exception
        r("library('%s')" % library)
    except:
        try:
            r("library('%s', lib.loc='%s')" % (library, HB_R_LIBS_DIR))
        except:
            try:
                r("install.packages('%s', INSTALL_opts = c('--no-lock'), repos='http://cran.r-project.org', lib='%s')" \
                  % (library, HB_R_LIBS_DIR))
                r("library('%s', lib.loc='%s')" % (library, HB_R_LIBS_DIR))
                print "OK: Installed R package '%s'." % library
                return
            except Exception, e1:
                try:
                    r("install.packages('%s', INSTALL_opts = c('--no-lock'), repos='http://hyperbrowser.uio.no/eggs_repo/R', lib='%s')" \
                        % (library, HB_R_LIBS_DIR))
                    r("library('%s', lib.loc='%s')" % (library, HB_R_LIBS_DIR))
                    print "OK: Installed R package '%s'." % library
                    return
                except Exception, e2:
                    try:
                        r("source('http://www.bioconductor.org/biocLite.R'); biocLite('%s', lib='%s')" \
                          % (library, HB_R_LIBS_DIR))
                        r("library('%s', lib.loc='%s')" % (library, HB_R_LIBS_DIR))
                        print "OK: Installed R package '%s'." % library
                        return

                    except Exception, e3:
                        print "FAILED: Did not find or manage to install R package '%s'. Error:" % library
                        print "        " + str(e1).strip()
                        print "        " + str(e2).strip()
                        raise
#                        sys.exit(1)

    print "OK: Found R package '%s'." % library

def installAndCheckRLibraries():
    from quick.util.InstallFunctions import executeShellCmd
    r = executeShellCmd('Xvfb :8.0 -screen 0 1600x1200x24 -nolisten tcp > \dev\null 2>&1 &', pipe=False, onError='nothing', background=True)

    old_display = os.environ.get('DISPLAY')
    os.environ['DISPLAY'] = ":8.0"
    exit = False

    try:
        _installAndCheckRLibrary('Biobase')
        _installAndCheckRLibrary('bioDist')
        _installAndCheckRLibrary('flashClust')
        _installAndCheckRLibrary('cluster')
        _installAndCheckRLibrary('gdata')
        _installAndCheckRLibrary('gtools')
        _installAndCheckRLibrary('bitops')
        _installAndCheckRLibrary('caTools')
        _installAndCheckRLibrary('gplots')
        _installAndCheckRLibrary('maptree')
        _installAndCheckRLibrary('pi0')
        _installAndCheckRLibrary('plotrix')

        import config.LocalOSConfig
        extraRLibraries = config.LocalOSConfig.__dict__.get('HB_EXTRA_R_LIBRARIES').strip().split('\n')
        if extraRLibraries != ['']:
            for library in extraRLibraries:
                _installAndCheckRLibrary(*library.strip().split())
    except Exception, e:
        print 'R installation error:', e
        exit = True

    r = executeShellCmd('pkill -f "Xvfb :8.0"', pipe=True, onError='nothing')

    if old_display:
        os.environ['DISPLAY'] = old_display
    else:
        del os.environ['DISPLAY']

    if exit:
        sys.exit(1)

def extractTestGenomeAndPreProcess(hbPath):
    from config.Config import ORIG_DATA_PATH
    from gold.origdata.PreProcessTracksJob import PreProcessAllTracksJob
    from quick.util.InstallFunctions import executeShellCmd
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

def setupHB(galaxyPath='', ignoreVersionChecking=False, installationSetupFn=''):
    hbPath = os.path.dirname(os.path.realpath(sys.argv[0])) + '/lib/hb'
    os.chdir(hbPath)

    checkDependencies()
    setupAllInstallationSpecificSetupFiles(hbPath, installationSetupFn)

    # galaxyPath = getWorkingGalaxyPath(galaxyPath)
    # if not ignoreVersionChecking:
    #     checkGalaxyVersion(hbPath, galaxyPath)

    # addPathsToLocalOSConfigIfNecessary(hbPath, galaxyPath)

    from quick.util.InstallFunctions import executePythonFile
    executePythonFile(os.sep.join(['setup', 'Install.py']), cwd=hbPath, setPythonPath=False)
    # executePythonFile(os.sep.join(['scripts', 'hb_scramble.py']), cwd=os.path.realpath(galaxyPath), setPythonPath=True)
    # executePythonFile(os.sep.join(['setup', 'CompileStyle.py']), cwd=hbPath, setPythonPath=True)
    # installAndCheckRLibraries()
    # extractTestGenomeAndPreProcess(hbPath)

def usage():
    print '''
Setup script of The Genomic HyperBrowser

Usage: python setup.py [options] [-g FILE] [-s FILE]

OPTIONS:
    -g PATH:
        Path to the Galaxy installation on which the Genomic HyperBrowser
        should be installed.

        (Default: The Galaxy path specified in config/LocalOSConfig.py, if any)

    -h, --help:
        Returns this help screen.

    -s FILE:
        Main setup file for configuring all installation specific setup files.

        (Default: config/setup/default/default.setup)
'''

if __name__ == '__main__':
    galaxyPath = ''
    installationSetupFn = ''
    ignoreVersionChecking = False

    try:
        opts, args = getopt(sys.argv[1:], 'hig:s:', ['help', 'ignore-version'])
    except GetoptError:
        usage()
        sys.exit(1)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(0)
        if opt in ('-i', '--ignore-version'):
            ignoreVersionChecking = True
        elif opt == '-g':
            galaxyPath = arg
        elif opt == '-s':
            installationSetupFn = arg

    if len(args) > 0:
        usage()
        sys.exit(0)

    try:
        setupHB(galaxyPath, ignoreVersionChecking, installationSetupFn)
    except Exception, e:
        from gold.application.LogSetup import logException
        logException(e)
        raise
