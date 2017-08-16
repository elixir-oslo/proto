#
# instance is dynamically imported into namespace of <modulename>.mako template (see web/controllers/hyper.py)

import errno
import os
import shutil
import subprocess

import quick.extra.GoogleMapsInterface as GoogleMapsInterface
import third_party.safeshelve as safeshelve
from config.Config import HB_SOURCE_CODE_BASE_DIR, STATIC_PATH
from proto.BaseToolController import BaseToolController
from proto.hyperbrowser.HyperBrowserControllerMixin import HyperBrowserControllerMixin
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.util.CommonFunctions import getGalaxyFnFromDatasetId

#TILECUTTER_PATH = HB_SOURCE_CODE_BASE_DIR + '/third_party/tileCutter3-test.py'
TILECUTTER_PATH = HB_SOURCE_CODE_BASE_DIR + '/third_party/tileCutter3.py'
PYTHON = 'python'
IDENTIFY = 'identify'
DPI = 150

class GoogleMapController(BaseToolController, HyperBrowserControllerMixin):
    jsonMethods = ('saveMap', 'restoreMap')

    def __init__(self, trans, job):
        BaseToolController.__init__(self, trans, job)
        
    def execute(self, imageFn, html, dpi=None):
        #galaxyId = extractIdFromGalaxyFn(html)
        #outDir = getUniqueWebPath(galaxyId)
        staticDir = GalaxyRunSpecificFile([], html)
        outDir = staticDir.getDiskPath()
        try:
            os.makedirs(outDir + '/tiles')
        except OSError, e:
            if e.errno == errno.EEXIST:
                print e
            else:
                raise e
        info = self.identify(imageFn, dpi)
        #tileDir = STATIC_PATH + '/test'
        maxSize = str(max(info[1], info[2]))
        cmd = [PYTHON, TILECUTTER_PATH, outDir + '/tiles', 'png', imageFn,  \
            '0', '0', maxSize,  maxSize, '0', '0', '0', '255', '255', '#111111']
        if dpi:
            cmd.append(str(dpi))
        out, err = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.STDOUT).communicate()
        shutil.copy(STATIC_PATH + '/maps/common/template-test.html', outDir + '/index.html')
        f = open(html, 'w')
        f.write(out)
        f.write('''
                <html>
                <body>
                    <a href="%s">Google Map</a>
                    <pre>%d x %d</pre>
                </body>
                </html>
                ''' % (staticDir.getURL() + '/index.html', info[1], info[2]))
        f.close()
        #print out, err
        
    def identify(self, image, dpi = None):
        # runs imagemagick tool
        cmd = [IDENTIFY]
        if dpi:
            cmd += ['-density', str(dpi)]
        cmd += [image]
        out, err = subprocess.Popen(cmd, stdout = subprocess.PIPE).communicate()
        info = out.split(' ')
        format = info[1].lower()
        size = info[2].split('x')
        tup = (format, int(size[0]), int(size[1]))
        return tup

    def saveMap(self, args):
        if args['name'].isdigit():
            galaxyFn = getGalaxyFnFromDatasetId( int(args['name']) )
            outDir = GalaxyRunSpecificFile([], galaxyFn).getDiskPath()
        else:
            outDir = '/'.join([GoogleMapsInterface.BASE_DIR, args['name']])

        try:
            os.makedirs(outDir + '/cookies')
        except OSError, e:
            if e.errno == errno.EEXIST:
                pass
            else:
                raise e
        cname = args['id'] if 'id' in args else 'common'
        s = safeshelve.open(outDir + '/cookies/' + cname + '.shelve')
        s['markers'] = args['markers']
        s['clusters'] = args['clusters']
        s['idxclusters'] = args['idxclusters']
        s.close()
        return {'debug': outDir}
        
    def restoreMap(self, args):
        map = GoogleMapsInterface.Map(args['name'])
        return map.getSavedCookies(args['id'])
        #if args['name'].isdigit():
        #    galaxyId = int(args['name'])
        #    outDir = getUniqueWebPath(['%03d' % (galaxyId / 1000), str(galaxyId)])
        #else:
        #    outDir = '/'.join([GoogleMapsInterface.BASE_DIR, args['name']])
        #r = {}
        #cname = args['id'] if 'id' in args else 'common'
        #sname = outDir + '/cookies/' + cname + '.shelve'
        #if os.path.exists(sname):
        #    s = safeshelve.open(sname, 'r')
        #    for x in ('markers', 'clusters'):
        #        if s.has_key(x):
        #            r[x] = s[x]
        #    s.close()
        #return r



def getController(transaction = None, job = None):
    return GoogleMapController(transaction, job)
