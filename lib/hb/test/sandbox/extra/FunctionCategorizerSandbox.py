#!/usr/bin/env python
import os
from gold.application.GalaxyInterface import GalaxyInterface
from quick.extra.FunctionCategorizer import FunctionCategorizer

def extremeMelt(val,diff):
    if val < 55:
        return -1
    elif val > 85:
        return 1

def meltSeg(val,diff):
    if diff < -0.13:
        return -2
    elif diff > 0.13:
        return 2
    elif -0.01 <= diff <= 0.01:
        return 0
    else:
        return None

meltSegLines = '''
    if diff < -0.13:
        return -2
    elif diff > 0.13:
        return 2
    elif -0.01 <= diff <= 0.01:
        return 0
    else:
        return None
'''.split(os.linesep)

#FunctionCategorizer(['melting'], meltSeg).createNewTrack(['melting','meltMapSeg'])
GalaxyInterface.createSegmentation('hg18',['melting'], ['melting','meltMapSeg2'], meltSegLines)
#exec( os.linesep.join( ['def categorizerMethod(val,diff):'] + meltSegLines) )
#a = categorizerMethod
#print a(3,-1)


