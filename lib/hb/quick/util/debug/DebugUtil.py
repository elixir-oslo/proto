'''
Created on Oct 1, 2014

@author: boris
'''

def insertBreakPoint(username=None, currentUser=None, ipAddress='localhost', 
                     errorToServer=True, outToServer=True):
    if username is None or username == currentUser:
        pydevPath = '/software/VERSIONS/python2-packages-2.7_2/lib/python2.7/site-packages/pysrc'
        import sys
        if pydevPath not in sys.path:
            sys.path.append(pydevPath)
#         import pydevd_file_utils
#         print str(pydevd_file_utils.PATHS_FROM_ECLIPSE_TO_PYTHON)
#         pydevd_file_utils.PATHS_FROM_ECLIPSE_TO_PYTHON = [('/home/boris/workspace/HBdev/HBdev','/hyperbrowser/src/hb_core_developer/trunk')]
        import pydevd
        pydevd.settrace(ipAddress, stderrToServer=errorToServer, stdoutToServer=outToServer)
        print 'Debugging... Reached breakpoint!'