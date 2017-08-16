import sys

from proto.generictool import getController

sys.path = sys.path[1:]  # to remove the '/proto' directory from the Python path
getController(None, sys.argv[1]).execute()

