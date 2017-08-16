import os
import sys
import logging
import time
import traceback
from copy import copy
from logging import FileHandler
from logging.handlers import RotatingFileHandler
#from quick.util.CommonFunctions import ensurePathExists
#from gold.util.CommonFunctions import getClassName
from urllib import unquote
from third_party.decorator import decorator
from config.Config import LOG_PATH, IS_EXPERIMENTAL_INSTALLATION, GALAXY_BASE_DIR, \
    DebugModes, DebugConfig

HB_LOGGER = 'hb'
USAGE_LOGGER = 'hb.usage'
RUNTIME_LOGGER = 'hb.runtime'
SIGNATURE_DEVIANCE_LOGGER = 'hb.signatureDeviance'
LACK_OF_SUPPORT_LOGGER = 'hb.lackOfSupport'
PARALLEL_LOGGER = 'hb.parallel'

DETAILED_ROTATING_LOG_FN = LOG_PATH + os.sep + 'detailed.log'
DETAILED_JOBRUN_ROTATING_LOG_FN = LOG_PATH + os.sep + 'detailedJobRun.log'
WARNINGS_LOG_FN = LOG_PATH + os.sep + 'warnings.log'
USAGE_LOG_FN = LOG_PATH + os.sep + 'usage.log'
RUNTIME_LOG_FN = LOG_PATH + os.sep + 'runtimes.log'
SIGNATURE_DEVIANCE_LOG_FN = LOG_PATH + os.sep + 'signatureDeviance.log'
LACK_OF_SUPPORT_LOG_FN = LOG_PATH + os.sep + 'lackOfSupport.log'
PARALLEL_LOG_FN = LOG_PATH + os.sep + 'parallel.log'
if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)
#ensurePathExists(LOG_PATH + os.sep)

defaultFormatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

logging.getLogger(HB_LOGGER).setLevel(5)

detailedHandler = RotatingFileHandler(DETAILED_ROTATING_LOG_FN, maxBytes=10**6, backupCount=5, delay=True)
detailedHandler.setLevel(logging.DEBUG)
detailedHandler.setFormatter(defaultFormatter)
logging.getLogger(HB_LOGGER).addHandler(detailedHandler)

detailedJobRunHandler = RotatingFileHandler(DETAILED_JOBRUN_ROTATING_LOG_FN, maxBytes=10**6, backupCount=5, delay=True)
detailedJobRunHandler.setLevel(logging.DEBUG)
detailedJobRunHandler.setFormatter(defaultFormatter)
#logging.getLogger(HB_LOGGER).addHandler(detailedJobRunHandler)

warningsHandler = FileHandler(WARNINGS_LOG_FN)
warningsHandler.setLevel(logging.WARNING)
warningsHandler.setFormatter(defaultFormatter)
logging.getLogger(HB_LOGGER).addHandler(warningsHandler)

usageHandler = FileHandler(USAGE_LOG_FN)
usageHandler.setFormatter(defaultFormatter)
logging.getLogger(USAGE_LOGGER).addHandler(usageHandler)

runtimeHandler = FileHandler(RUNTIME_LOG_FN)
runtimeHandler.setLevel(5)
runtimeHandler.setFormatter(defaultFormatter)
logging.getLogger(RUNTIME_LOGGER).addHandler(runtimeHandler)

signatureDevianceHandler = FileHandler(SIGNATURE_DEVIANCE_LOG_FN)
signatureDevianceHandler.setLevel(5)
signatureDevianceHandler.setFormatter(defaultFormatter)
logging.getLogger(SIGNATURE_DEVIANCE_LOGGER).addHandler(signatureDevianceHandler)

lackOfSupportHandler = FileHandler(LACK_OF_SUPPORT_LOG_FN)
lackOfSupportHandler.setLevel(5)
lackOfSupportHandler.setFormatter(defaultFormatter)
logging.getLogger(LACK_OF_SUPPORT_LOGGER).addHandler(lackOfSupportHandler)

parallelHandler = FileHandler(PARALLEL_LOG_FN)
parallelHandler.setLevel(5)
parallelHandler.setFormatter(defaultFormatter)
logging.getLogger(PARALLEL_LOGGER).addHandler(parallelHandler)

#from quick.util.DatabaseLogger import MySQLDatabaseLogHandler
#
#databaseHandler = MySQLDatabaseLogHandler("mysql://hb_testing:hb_testing@localhost:3306/hb_testing?unix_socket=/var/lib/mysql/mysql.sock")
#databaseHandler.setLevel(logging.DEBUG)
#databaseHandler.setFormatter(defaultFormatter)
#logging.getLogger(HB_LOGGER).addHandler(databaseHandler)


@decorator
def usageAndErrorLogging(func, *args, **kwArgs):
    try:
        MAX_ARG_LEN = 25000

        if len(args) >= 3 and isinstance(args[2], basestring):
            args = list(args)
            args[2] = unquote(args[2])
        modifiedKwArgs = copy(kwArgs)
        #if 'analysisDef' in modifiedKwArgs:
            #modifiedKwArgs['analysisDef'] = unquote( modifiedKwArgs['analysisDef'] )

        kwArgsStr = unquote(str(copy(kwArgs)))
        if len(kwArgsStr) > MAX_ARG_LEN:
            kwArgsStr = kwArgsStr[:MAX_ARG_LEN] + '...'

        starttime = time.time()

        argsStr = unquote(str(args))
        if len(argsStr) > MAX_ARG_LEN:
            argsStr = argsStr[:MAX_ARG_LEN] + '...'

        logging.getLogger(USAGE_LOGGER).info('Running ' + func.__name__ + '() in module ' + func.__module__ +\
                                             ', with arguments: ' + argsStr + ', ' + kwArgsStr)
        ret = func(*args, **kwArgs)
        runtime = time.time() - starttime
        logging.getLogger(USAGE_LOGGER).info('Finished ' + func.__name__ + '() in module ' + func.__module__  + '. ' +\
                                             ('Runtime: %.1f seconds' % runtime) )
        return ret
    except Exception,e:
        logging.getLogger(HB_LOGGER).error('Exception in ' + func.__name__ + '() in module ' + func.__module__  + \
                                           ' - ' + e.__class__.__name__ + ': ' + str(e))
        logging.getLogger(HB_LOGGER).debug(traceback.format_exc())
        raise

@decorator
def runtimeLogging(func, *args, **kwArgs):
    if not IS_EXPERIMENTAL_INSTALLATION:
        return func(*args, **kwArgs)

    try:
        #if len(args) >= 3 and isinstance(args[2], basestring):
        #    args = list(args)
        #    args[2] = unquote(args[2])
        modifiedKwArgs = copy(kwArgs)
        #if 'analysisDef' in modifiedKwArgs:
        #    modifiedKwArgs['analysisDef'] = unquote( modifiedKwArgs['analysisDef'] )
        starttime = time.time()
        #logging.getLogger(USAGE_LOGGER).info('Running ' + func.__name__ + '() in module ' + func.__module__ +\
                                             #', with arguments: ' + str(args) + ', ' + str(modifiedKwArgs) )
        ret = func(*args, **kwArgs)
        runtime = time.time() - starttime
        logging.getLogger(RUNTIME_LOGGER).log(5, 'Runtime for ' + func.__name__ + ', with arguments: ' + str(args) + ', ' + str(modifiedKwArgs) \
                                                                   + ': %.2f ms' % (runtime*1000))
        return ret
    except Exception,e:
        logging.getLogger(RUNTIME_LOGGER).error('Exception in ' + func.__name__ + '() in module ' + func.__module__  + \
                                           ' - ' + e.__class__.__name__ + ': ' + str(e))
        logging.getLogger(RUNTIME_LOGGER).debug(traceback.format_exc())
        raise

def exceptionLogging(exceptClass = Exception, level=logging.DEBUG, message='', raiseFurther=False):
    def _exceptionLogging(func, *args, **kwArgs):
        try:
            return func(*args, **kwArgs)
        except exceptClass,e:
            logging.getLogger(HB_LOGGER).log(level, 'Exception in ' + func.__name__ + '() in module ' + func.__module__  + \
                                               ' - ' + e.__class__.__name__ + ': ' + str(e) +'. ' + message)
            logging.getLogger(HB_LOGGER).debug(traceback.format_exc())
            if raiseFurther:
                raise
    return decorator(_exceptionLogging)

def logException(e, level = logging.ERROR, message = ''):
    logging.getLogger(HB_LOGGER).log(level, 'Exception' + \
                                   ' - ' + e.__class__.__name__ + ': ' + str(e) +'. ' + message)
    logging.getLogger(HB_LOGGER).debug(traceback.format_exc())

def logMessage(message, level = logging.DEBUG, logger=HB_LOGGER):
    #from traceback import extract_stack
    #logging.getLogger(logger).log(level, str(extract_stack()))
    logging.getLogger(logger).log(level, message)

def logLackOfSupport(message, level = logging.DEBUG, logger=LACK_OF_SUPPORT_LOGGER):
    logging.getLogger(logger).log(level, message)

LOG_ONCE_CACHE = set([])
def logMessageOnce(message, id=None, level = logging.DEBUG, logger=HB_LOGGER):
    if id is None:
        id = message
    if not id in LOG_ONCE_CACHE:
        LOG_ONCE_CACHE.add(id)
        #logging.getLogger(HB_LOGGER).log(level, message)
        logMessage(message, level, logger)

def logExceptionOnce(e, level = logging.DEBUG, message='', id=None):
    if id is None:
        id = message
    assert id!='' #should not have empty id as this is used to avoid future logging of same id..
    if not id in LOG_ONCE_CACHE:
        LOG_ONCE_CACHE.add(id)
        #logging.getLogger(HB_LOGGER).log(level, message)
        logException(e, level, message)

def setupDebugModeAndLogging(mode=DebugModes.RAISE_HIDDEN_EXCEPTIONS_NO_VERBOSE):
    debugHandler = logging.StreamHandler(sys.stdout)
    debugHandler.setLevel(logging.DEBUG)
    debugHandler.setFormatter(defaultFormatter)
    logging.getLogger(HB_LOGGER).addHandler(debugHandler)

    errorHandler = logging.StreamHandler(sys.stderr)
    errorHandler.setLevel(logging.ERROR)
    errorHandler.setFormatter(defaultFormatter)
    logging.getLogger(HB_LOGGER).addHandler(errorHandler)

    DebugConfig.changeMode(mode)
    #r('options(warn=2)') #To get all R warnings..
