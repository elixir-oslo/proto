import sys

from proto.hyperbrowser.generictool import getController

getController(None, sys.argv[1]).execute()

