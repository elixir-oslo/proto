import sys
from gold.application.GalaxyInterface import *
from proto.hyperbrowser.googlemap import *


image = sys.argv[1]
output = sys.argv[2]
dpi = sys.argv[3]

control = getController(None, None)
control.execute(image, output, int(dpi))
