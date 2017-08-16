print '.'
import functools
import os
from urllib import unquote, quote
from config.Config import DEFAULT_GENOME#, brk
print '.'
from gold.application.StatRunner import StatRunner
print '.'
from gold.track.Track import Track
from gold.util.CommonFunctions import insertTrackNames, smartStrLower, getClassName, prettyPrintTrackName, createOrigPath
from quick.application.ProcTrackOptions import ProcTrackOptions
from quick.application.UserBinSource import UserBinSource
print ','
from quick.extra.CustomTrackCreator import CustomTrackCreator
from quick.extra.TrackExtractor import TrackExtractor
from gold.result.Results import Results
from quick.extra.FunctionCategorizer import FunctionCategorizer
from gold.statistic.ResultsMemoizer import ResultsMemoizer
print '.'
from gold.description.AnalysisDefHandler import AnalysisDefHandler
print '0'
#from gold.description.AnalysisManager import AnalysisManager
print '.5'
from quick.application.ExternalTrackManager import ExternalTrackManager
from gold.description.TrackInfo import TrackInfo
print 1
from tempfile import NamedTemporaryFile
import re
from gold.util.CustomExceptions import ShouldNotOccurError
from quick.util.CommonFunctions import extractIdFromGalaxyFn
print '2'
from gold.origdata.GenomeElementSource import GenomeElementSource
from quick.extra.OrigFormatConverter import OrigFormatConverter
from quick.util.GenomeInfo import GenomeInfo
import traceback
import shutil
from copy import copy
from gold.application.LogSetup import logging, HB_LOGGER, USAGE_LOGGER, usageAndErrorLogging, logException, detailedJobRunHandler
print '3'
