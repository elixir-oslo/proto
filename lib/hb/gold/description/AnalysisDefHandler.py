import re
from gold.description.AnalysisOption import AnalysisOption
from gold.util.CustomExceptions import ShouldNotOccurError
from gold.application.LogSetup import logging, logException, logMessage

# An analysisDef is a text string from analysisList.py and consists of text and
# configs A config has a name (referred to as label) and a set of choices. Both
# the option and each choice is a tuple of (key,text). Thus, both options and
# choices can be referred to by the keyname and the text. The syntax of a config
# in analysisDef is:
#
# [labelKey:labelText=choiceKey1:choiceText1/choiceKey2:choiceText2]

# A '_' prefix can be used to mark hidden behavior. Text-parts are set equal to
# key if omitted.
#
# The class AnalysisDefHandler is used to handle a whole analysisDef, with each
# option again handled by a AnalysisOption-object

class AnalysisSpec(object):
    #Only supports a single stat, at least for now
    #Takes a MagicStatFactory, as this will resolve into either an unsplittable or a splittable statistic according to what's suited
    #Note: maybe MagicStatFactory should have a synonomous class name that would appear less intrusive in a setting like this?
    #@takes(AnalysisSpec, MagicStatFactory)
    def __init__(self, statistic):
        self._statClassList = [statistic]
        self._analysisParts = []
        
    #@takes(str, str)
    def addParameter(self, paramName, paramValue):
        self._analysisParts.append(AnalysisOption('[%s=%s]' % (paramName, paramValue) ))

    def getDefAfterChoices(self, filterByActivation=False):
        defAfterChoices = ''
        for part in self._analysisParts:
            if isinstance(part, AnalysisOption):
                if (not filterByActivation or part.isActivated(self)):
                    defAfterChoices += part.getDefAfterChoice()
            else:
                defAfterChoices += str(part)
        defAfterChoices += ' -> ' + ','.join([x.__name__ for x in self._statClassList])
        return defAfterChoices
        
        #return ''.join( [( part.getDefAfterChoice() if isinstance(part, AnalysisOption) else str(part) ) \
        #                 for part in self._analysisParts] ) \
        #                 + ' -> ' + ','.join([x.__name__ for x in self._statClassList])
        
class AnalysisDefHandler(AnalysisSpec):
    H0_KEY = 'H0'
    H1_KEY = 'H1'
    TAIL_KEY = 'tail'
    TAIL_CHOICE_LEFT  = 'less'
    TAIL_CHOICE_RIGHT = 'more'
    TAIL_CHOICE_BOTH = 'different'
    ASSUMP_LABEL_KEY = 'assumptions'
    ILLUSTRATION_FN_KEY = 'illustrationFn'
    TF1_KEY = 'tf1'
    TF2_KEY = 'tf2'
    
    def __init__(self, analysisLine, reversed=False):
        self._reversed = reversed
        self._analysisLine = analysisLine
        self._parseDef(analysisLine)

    def _parseDef(self, id):
        self._analysisParts = []
        self._statClassList = []

#                           ([^-[]* #pure text - not '['
        #print 'NOWAG id:', id
        parts = re.findall('''
                            # Match pure text (part[0]):
                           ( (?: [^-[]* (?:-(?!>))? )* #1. pure text - not '[' or '-',
                                                       #2. separated by a possible '-' that is not before a '>'
                                                       #1 and 2 is repeated as long as necessary
                           [^-[\s]+) #should not end with whitespace,
                                     #as this may belong to the '->'-expression
                           # Match option clause (part[1])            
                           |( \[ [^[\]]* \] ) #Matches an expression inside brackets '[]'
                           # Match specification of statistic classes (part[2])
                           |( \s? \-> \s? .* )
                           # Match any additional whitespace (part[3])
                           |(\s*)
                           ''', id, flags=re.VERBOSE)
        
        from gold.statistic.AllStatistics import STAT_CLASS_DICT
        for part in parts:
            if part[0] != '':
                self._analysisParts.append(part[0])
            if part[1] != '':
                self._analysisParts.append(AnalysisOption(part[1]))
            if part[2] != '':
                statNames = part[2].replace('->','').replace(' ','').split(',')
                #self._statClassList = statNames                
                self._statClassList = [STAT_CLASS_DICT[statName] for statName in statNames \
                                       if STAT_CLASS_DICT.get(statName) is not None]
                if len(self._statClassList)==0:
                    if len(statNames)==0:
                        logMessage('No statistic found when parsing analysisDef: ' + self._analysisLine)
                    else:
                        logMessage('Specified statistics not found in STAT_CLASS_DICT. Statistics:%s, and keys in STAT_CLASS_DICT: %s' % (str(statNames), str(STAT_CLASS_DICT)) )
            if part[3] != '':
                self._analysisParts.append(part[3])

    def setChoice(self, optionLabelKeyOrText, choiceKeyOrText):
        for part in self._analysisParts:
            if isinstance(part, AnalysisOption):
                if optionLabelKeyOrText in [part.getLabelKey(), part.getLabelText()]:
                    part.setChoice(choiceKeyOrText)
                    #self.resetValidStat()
                    return
        raise ShouldNotOccurError
    
    def setDefaultChoice(self, optionLabelKeyOrText):
        for part in self._analysisParts:
            if isinstance(part, AnalysisOption):
                if optionLabelKeyOrText in [part.getLabelKey(), part.getLabelText()]:
                    part.setDefaultChoice()
                    return
        raise ShouldNotOccurError        

    def reduceChoices(self, optionLabelKey, choiceKeyList):
        for part in self._analysisParts:
            if isinstance(part, AnalysisOption):                 
                if part.getLabelKey() == optionLabelKey:
                    if len(choiceKeyList) == 0:
                        self._analysisParts.remove(part)
                    else:
                        part.reduceChoices(choiceKeyList)
                    #self.resetValidStat()
                    return
        raise ShouldNotOccurError
        
    def changeChoices(self, optionLabelKey, choiceList):
        for part in self._analysisParts:
            if isinstance(part, AnalysisOption):                 
                if part.getLabelKey() == optionLabelKey:
                    if len(choiceList) == 0:
                        self._analysisParts.remove(part)
                    else:
                        part.changeChoices(choiceList)
                    return
        raise ShouldNotOccurError

    def getChoice(self, optionLabelKey):
        for part in self._analysisParts:
            if isinstance(part, AnalysisOption):
                if part.getLabelKey() == optionLabelKey:
                    return part.getChoice()
        return None

    def getChoiceText(self, optionLabelKey):
        for part in self._analysisParts:
            if isinstance(part, AnalysisOption):
                if part.getLabelKey() == optionLabelKey:
                    return part.getChoiceText()
        return None
    
    def getOptionLabelsAsText(self):
        return [part.getLabelText() for part in self._analysisParts if isinstance(part, AnalysisOption)\
                 and part.getLabelText()!='']
    
    def getOptionsAsText(self):
        return dict([(part.getLabelText(), part.getAllChoiceTexts()) for part in self._analysisParts \
            if isinstance(part, AnalysisOption) and part.getLabelText()!=''])

    def getFilteredOptionLabelsAsText(self, labelKeys):
        return [part.getLabelText() for part in self._analysisParts if isinstance(part, AnalysisOption)\
                 and part.getLabelText()!='' and part.getLabelKey() in labelKeys]

    def getFilteredOptionsAsText(self, labelKeys):
        return dict([(part.getLabelText(), part.getAllChoiceTexts()) for part in self._analysisParts \
            if isinstance(part, AnalysisOption) and part.getLabelText()!='' and part.getLabelKey() in labelKeys]) 

    def getOptionsAsKeys(self):
        return dict([(part.getLabelKey(), part.getAllChoiceKeys()) for part in self._analysisParts \
            if isinstance(part, AnalysisOption) and part.getLabelText()!=''])
        
    def getFirstOptionKeyAndValues(self):
        '''
            Return the first parameter. Temporary usage for API calls of doAnalysis.
        '''
        for part in self._analysisParts:
            if isinstance(part, AnalysisOption) and part.getLabelText()!='':
                return part.getLabelKey(), part.getAllChoiceKeys()
        return None, None
    
    def getAllOptionsAsKeys(self):
        return dict([(part.getLabelKey(), part.getAllChoiceKeys()) for part in self._analysisParts \
            if isinstance(part, AnalysisOption)])
    
    def getChoices(self, filterByActivation=False):
        return dict([(part.getLabelKey(), part.getChoice()) for part in self._analysisParts \
            if isinstance(part, AnalysisOption) and (not filterByActivation or part.isActivated(self))])

    def getChoicesAsText(self):
        return dict([(part.getLabelText(), part.getChoiceText()) for part in self._analysisParts \
            if isinstance(part, AnalysisOption) and part.getLabelText() != ''])

    def getFilteredChoicesAsText(self, labelKeys):
        return dict([(part.getLabelText(), part.getChoiceText()) for part in self._analysisParts \
            if isinstance(part, AnalysisOption) and part.getLabelText() != '' and part.getLabelKey() in labelKeys])
        

    def getDef(self):
        return ''.join( [( part.getDef() if isinstance(part, AnalysisOption) else str(part) ) \
                         for part in self._analysisParts] ) \
                         + ' -> ' + ','.join([x.__name__ for x in self._statClassList])

    @staticmethod
    def splitAnalysisText(text):
        assert text.count(':') >= 1, text
        splitPos = text.find(':')
        return text[:splitPos], text[splitPos+1:]
 
    #The following methods help interprete data in configs, and thus contains some definitions of semantics
    #def getH0(self):
    #    #print 'My keys: ', self.getOptionsAsKeys()
    #    #if 'H0' in self.getOptionsAsKeys():
    #    #    return self.getChoice('H0')
    #    choices = self.getChoices()
    #    if 'H0' in choices:
    #        return choices['H0']
    #    else:
    #        #print 'My keys: ', self.getOptionsAsKeys()
    #        return None

    #
    #def getH1(self):
    #    #optionKeys = self.getOptionsAsKeys()
    #    #if 'H1' in optionKeys and 'tail' in optionKeys:
    #    choices = self.getChoices()
    #    if 'H1' in choices and 'tail' in choices:
    #        try:
    #            #tailChoice = self.getChoice('tail')                
    #            tailChoice = choices['tail']
    #            self.setChoice('H1', tailChoice)
    #            return self.getChoiceText('H1')
    #        
    #        except (ShouldNotOccurError), e:
    #            logException(e, logging.WARNING,'Could not find H1, probably mismatch between tail and H1 in analysisDef (tail choice: %s)' % self.getChoice('tail') )                
    #        except Exception, e:
    #            logException(e, logging.WARNING,'Could not find H1')                
    #    return 'No H1 found..'
    #
    #    
    #def getNullModel(self):
    #    if 'assumptions' in self.getOptionsAsKeys():
    #        return self.getChoiceText('assumptions')
    #    else:
    #        return None
    
    def _getFormatConverterKeys(self):
        return [self.TF1_KEY, self.TF2_KEY]
    
    def getFormatConverterOptionLabelsAsText(self):
        return self.getFilteredOptionLabelsAsText(self._getFormatConverterKeys())
    
    def getFormatConverterOptionsAsText(self):
        return self.getFilteredOptionsAsText(self._getFormatConverterKeys())
    
    def getFormatConverterChoicesAsText(self):
        return self.getFilteredChoicesAsText(self._getFormatConverterKeys())
    
    def _getInterfaceChoiceKeys(self):
        return [ x for x in self.getChoices().keys() if not x in self._getFormatConverterKeys() ]
    
    def getInterfaceOptionLabelsAsText(self):
        return self.getFilteredOptionLabelsAsText(self._getInterfaceChoiceKeys())
    
    def getInterfaceOptionsAsText(self):
        return self.getFilteredOptionsAsText(self._getInterfaceChoiceKeys())
    
    def getInterfaceChoicesAsText(self):
        return self.getFilteredChoicesAsText(self._getInterfaceChoiceKeys())
    
    def getH0(self):
        H0 = self.getChoice(self.H0_KEY)
#        if H0 is None:
#            logMessage('Could not find H0 in analysisDef: ' + self._analysisLine)
        return H0
         
    def getH1(self):
        #H1 = self.getChoiceText(self.H1_KEY)
        #return H1
        tailChoice = self.getChoice(self.TAIL_KEY)
        if tailChoice is None:
            return None
        
        selectedH1Key = self.H1_KEY + '_' + tailChoice
        H1 = self.getChoice(selectedH1Key)
        if H1 is None:
            logMessage('Could not find H1, probably mismatch between tail-choice and corresponding H1-option in analysisDef '+\
                       '(tail choice: %s, options: %s)' % (self.getChoice('tail'), self.getAllOptionsAsKeys() ) )            
    
        return H1

    #todo:To be phased out..
    def syncH1WithTail(self):
        optionKeys = self.getAllOptionsAsKeys()
        if self.H1_KEY in optionKeys and self.TAIL_KEY in optionKeys:
            try:
                tailChoice = self.getChoice(self.TAIL_KEY)                
                self.setChoice(self.H1_KEY, tailChoice)
            
            except (ShouldNotOccurError), e:
                logException(e, logging.WARNING,'Could not find H1, probably mismatch between tail and H1 in analysisDef (tail choice: %s)' % self.getChoice(self.TAIL_KEY) )                
            except Exception, e:
                logException(e, logging.WARNING,'Could not find H1')
    
    def getNullModel(self):
        nullModel = self.getChoiceText(self.ASSUMP_LABEL_KEY)
        if self._reversed:
            if re.search('[^ ,.]T[12][^ ,.]',nullModel):
                logMessage('found instance of T1/T2 in null-model that may not refer to tracks as assumed in getNullModel')
            assert not 'tempT2' in nullModel
            
            nullModel = nullModel.replace('T1','tempT2')
            nullModel = nullModel.replace('T2','T1')
            nullModel = nullModel.replace('tempT2','T2')
        
        return nullModel
    
    def isTwoSidedTest(self):
        tailChoice = self.getChoice(self.TAIL_KEY)
        if tailChoice is not None and tailChoice == self.TAIL_CHOICE_BOTH:
            return True
        else:
            return False
        
    def getIllustrationFn(self):
        return self.getChoice(self.ILLUSTRATION_FN_KEY)
