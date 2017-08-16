import os
import sys
import subprocess

from gold.util.CustomExceptions import ExecuteError

def _handleError(msg, printError, onError, stdout):
    if printError:
        if not stdout:
            stdout = sys.stdout
        print>>stdout, 'FAILED: ' + msg
    if onError == 'exit':
        sys.exit(1)
    elif onError == 'exception':
        raise ExecuteError(msg)

def _executeCmd(cmd, fn=None, scriptType='', cwd=None, pipe=False, printError=True,
                onError='exit', background=False, stdout=None, stderr=None, noBuffer=True):
    try:
        onError = onError.lower()
        onError.lower() in ['exit', 'exception', 'nothing']

        if noBuffer:
            cmd = 'stdbuf -oL ' + cmd

        p = subprocess.Popen(args=cmd, shell=True, cwd=cwd,
                             stdout=subprocess.PIPE if pipe else stdout,
                             stderr=subprocess.PIPE if pipe else stderr)
        if background:
            return

        if pipe:
            r = p.communicate()
            if r[1]:
                msg = 'Not able to execute %sscript: %s. Error: %s' \
                      % (scriptType + ' ' if scriptType else '', fn if fn else cmd, r[1])
                _handleError(msg, printError, onError, stdout)
            return r[0]
        else:
            r = p.wait()
            if r != 0:
                msg = 'Not able to execute %sscript: %s (Return code: %d)' % (scriptType + ' ' if scriptType else '', fn if fn else cmd, r)
                _handleError(msg, printError, onError, stdout)
            return r
    finally:
        if stdout:
            stdout.flush()
        if stderr:
            stderr.flush()

def executePythonFile(pyFn, args='', cwd=None, printError=True, onError='exit', setPythonPath=False,
                      stdout=None, stderr=None, noBuffer=True):
    from config.Config import GALAXY_LIB_PATH
    
    origPyFn = pyFn
    if not cwd:
        cwd = os.path.dirname(pyFn)
        pyFn = os.path.basename(pyFn)
#    cmd = ' '.join([sys.executable, PYTHON_EXECUTE_OPTIONS, pyFn, args])
    cmd = ' '.join([sys.executable, pyFn, args])

    if noBuffer:
        cmd = 'stdbuf -oL ' + cmd

    if setPythonPath:
        from config.Config import HB_SOURCE_CODE_BASE_DIR, HB_PYTHONPATH, GALAXY_BASE_DIR

        cmd = 'export PYTHONPATH="%s:%s:%s:%s"; ' % \
              (HB_SOURCE_CODE_BASE_DIR, GALAXY_LIB_PATH, GALAXY_BASE_DIR + os.sep + 'eggs', HB_PYTHONPATH) + cmd

    _executeCmd(cmd, origPyFn, 'python', cwd=cwd, printError=printError, onError=onError,
                stdout=stdout, stderr=stderr, noBuffer=False)

def executeShellFile(shFn, args='', cwd=None, printError=True, onError='exit', background=False,
                     stdout=None, stderr=None, noBuffer=True):
    origShFn = shFn
    if not cwd:
        cwd = os.path.dirname(shFn)
        shFn = os.path.basename(shFn)
    _executeCmd(' '.join(['sh', shFn]) + ' '.join(args), \
                origShFn, 'shell', cwd=cwd, printError=printError, onError=onError, background=background,
                stdout=stdout, stderr=stderr, noBuffer=noBuffer)
    
def executeShellCmd(cmd, args='', cwd=None, pipe=True, printError=True, onError='exit', background=False,
                    stdout=None, stderr=None, noBuffer=True):
    return _executeCmd(cmd, None, 'shell', cwd=cwd, pipe=pipe, printError=printError, onError=onError,
                       background=background, stdout=stdout, stderr=stderr, noBuffer=noBuffer)
