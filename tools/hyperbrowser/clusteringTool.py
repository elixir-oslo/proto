import sys

from proto.hyperbrowser.clusteringtool import *

control = getController(None, sys.argv[1])
control.execute()
