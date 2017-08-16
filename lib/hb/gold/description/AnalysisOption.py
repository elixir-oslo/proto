import re
from gold.util.CustomExceptions import ShouldNotOccurError

class AnalysisOption(object):
    def __init__(self, optionLine):
        #self._label = AnalysisOption._splitOptionElement(DEFAULT_OPTION_LABEL)
        self._label = None
        self._choice = 0
        self._choiceList = []

        parts = re.findall('''
                           # Whitespace
                             ( [\s=]+ )
                           # Label clause
                           | ( [^=[\]]+ # Does not include '=' or ']'
                               [^\s] # Does not end with whitespace
                               (?=\s*=) ) # Ends with '=' (but not included)
                           # Choice clause
                           | ( [^/[\]]+ )
                           ''', optionLine, re.VERBOSE)
        for part in parts:
            if part[1] != '':
                self._label = AnalysisOption._splitOptionElement(part[1])
            if part[2] != '':
                self._choiceList.append(AnalysisOption._splitOptionElement(part[2]))

        assert self._label != None
        assert len(self._choiceList) > 0, 'Empty list of choices for label: ' + str(self._label)

    def isHidden(self):
        return self._label[1].startswith('_')

    def getLabelKey(self):
        return self._label[0]

    def getLabelText(self):
        labelText = self._label[1][1:] if self.isHidden() else self._label[1]
        #Remove if-clause
        labelText = re.sub('\<[^<>]*\>','',labelText)
        return labelText

    def getAllChoiceTexts(self):
        #return [text if not text.startswith('_') else text[1:] for key,text in self._choiceList]
        return [text for key,text in self._choiceList]

    def getAllChoiceKeys(self):
        for choice in self._choiceList:
            assert len(choice)==2, 'Error in analysis definition: each choice for an option should have two elements - key and text (%s)' % ':'.join(choice)
        return [key for key,text in self._choiceList]

    def setChoice(self, choiceKeyOrText):
        for i in range(len(self._choiceList)):
            if choiceKeyOrText in [self._choiceList[i][x] for x in [0,1]]:
                self._choice = i
                return
        raise ShouldNotOccurError

    def setDefaultChoice(self):
        self._choice = 0

    def reduceChoices(self, choiceKeyList):
        self._choiceList = [x for x in self._choiceList if x[0] in choiceKeyList]

    def changeChoices(self, choiceList):
        self._choiceList = choiceList

    def getChoice(self):
        return self._choiceList[ self._choice ][0]

    def getChoiceText(self):
        return self._choiceList[ self._choice ][1]

    def getDefAfterChoice(self):
        return self._constructDef( [self._choice] )
    #    return '[' + ':'.join(self._label) + '=' + ':'.join(self._choiceList[ self._choice ]) + ']'

    def getDef(self):
        return self._constructDef( range(0, len(self._choiceList)) )

    def _constructDef(self, choiceIndexes):
        return '[' + \
                ':'.join(self._label) + '=' + \
                '/'.join([ ':'.join(self._choiceList[ choiceIndex ]) for choiceIndex in choiceIndexes ]) + \
                ']'

    def __str__(self):
        return self._choiceList[ self._choice ][1]

    @staticmethod
    def _splitOptionElement(el):
        if ':' in el:
            return el.split(':')
        else:
            return [el,el]

    def isActivated(self, defHandler):
        'Checks whether all if-clauses (within <>) are satisfied (if any). Currently only considers label text.'
        checks = re.findall('\<[^<>]*\>', self._label[1])
        for check in checks:
            assert check[0]=='<'
            check = check[1:-1] #remove <>
            var,value = check.split('--')
            if defHandler.getChoice(var) != value:
                #print 'non-matching value in function isActivated: ', defHandler.getChoice(var), value
                return False
        return True

