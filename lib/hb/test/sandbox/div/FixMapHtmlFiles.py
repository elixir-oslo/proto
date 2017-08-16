from config.Config import MAPS_PATH
from subprocess import Popen, PIPE

import os, shutil

for dir in [MAPS_PATH + os.sep + x for x in os.listdir(MAPS_PATH) if os.path.isdir(MAPS_PATH + os.sep + x) and x not in ['common', 'old']]:
    print dir
    fn = dir + os.sep + 'index.html'
    if os.path.exists(fn + '.old_javascript'):
        #output = Popen(["diff", '-u', fn, fn + '.old_javascript'], stdout=PIPE).communicate()[0]
        #print output
#        continue
        shutil.move(fn + '.old_javascript', fn)
        print fn + '.old_javascript'
    shutil.copy(fn, fn + '.old_javascript')
    f = open(fn, 'r').readlines()
    out = open(fn,'w')
    for line in f[:6]:
        out.write(line)
    
    out.write(\
'''        <script type="text/javascript" src="../../../static/scripts/libs/jquery/jquery.js"></script>
''')
    
    for line in f[7:]:
        out.write(line)
    out.close()
