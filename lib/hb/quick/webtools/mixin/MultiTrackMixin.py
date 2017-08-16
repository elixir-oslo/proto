from quick.application.ProcTrackOptions import ProcTrackOptions
# This is a template prototyping GUI that comes together with a corresponding
# web page.


class MultiTrackMixin(object):
    
    @staticmethod
    def getMultiTrackInputBoxNames():
        '''
        Specifies a list of headers for the input boxes, and implicitly also the
        number of input boxes to display on the page. The returned list can have
        two syntaxes:
        
            1) A list of strings denoting the headers for the input boxes in
               numerical order.
            2) A list of tuples of strings, where each tuple has
               two items: a header and a key.
        
        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is either a number in the range of 1 to the
        number of boxes (case 1), or the specified key (case 2).
        '''
        return [('Select genome','Genome'),('Select source of track 1', 'Track1Source'), ('Select track 1','Track1'), ('Select source of track 2', 'Track2Source'), ('Select track 2', 'Track2'),\
        ('Select source of track 3', 'Track3Source'), ('Select track 3', 'Track3'),('Select source of track 4', 'Track4Source'), ('Select track 4', 'Track4'),\
        ('Select source of track 5', 'Track5Source'), ('Select track 5', 'Track5'),('Select source of track 6', 'Track6Source'), ('Select track 6', 'Track6')]

    @classmethod
    def getInputBoxGroups(cls, choices=None):
        if hasattr(super(GSuiteResultsTableMixin, cls), 'getInputBoxGroups'):
            return super(GSuiteResultsTableMixin, cls).getInputBoxGroups(choices)
        return None

    @staticmethod    
    def getOptionsBoxGenome(): # Alternatively: getOptionsBoxKey()
        '''
        Defines the type and contents of the input box. User selections are
        returned to the tools in the prevChoices and choices attributes to other
        methods. These are lists of results, one for each input box (in the
        order specified by getInputBoxOrder()).
        
        The input box is defined according to the following syntax:
        
        Selection box:          ['choice1','choice2']
        - Returns: string
        
        Text area:              'textbox' | ('textbox',1) | ('textbox',1,False)
        - Tuple syntax: (contents, height (#lines) = 1, read only flag = False)
        - Returns: string
        
        Password field:         '__password__'
        - Returns: string
        
        Genome selection box:   '__genome__'
        - Returns: string
        
        Track selection box:    '__track__'
        - Requires genome selection box.
        - Returns: colon-separated string denoting track name
        
        History selection box:  ('__history__',) | ('__history__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: colon-separated string denoting galaxy track name, as
                   specified in ExternalTrackManager.py.
        
        History check box list: ('__multihistory__', ) | ('__multihistory__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: OrderedDict with galaxy track name as key and selection
                   status (bool) as value.
        
        Hidden field:           ('__hidden__', 'Hidden value')
        - Returns: string
        
        Table:                  [['header1','header2'], ['cell1_1','cell1_2'], ['cell2_1','cell2_2']]
        - Returns: None
        
        Check box list:         OrderedDict([('key1', True), ('key2', False), ('key3', False)])
        - Returns: OrderedDict from key to selection status (bool).
        '''
        return '__genome__'
    
    @staticmethod    
    def getOptionsBoxTrack1Source(prevChoices): 
        '''
        See getOptionsBox1().
        
        '''
        return ['--- select ---','Track','History']
    
    @staticmethod    
    def getOptionsBoxTrack1(prevChoices): 
        '''
        See getOptionsBox1().
        
        '''
        Flag = False
        if prevChoices[-2] in ['Track','History']:
            return '__track__' if prevChoices[-2] == 'Track' else '__history__', 
        
    
    @staticmethod    
    def getOptionsBoxTrack2Source(prevChoices):
        '''
        See getOptionsBox1().
        '''
        
        if prevChoices[-1] in ['Track','History'] or (prevChoices[-3] == 'Track' and ProcTrackOptions.isValidTrack(prevChoices[0], prevChoices[-2].split(':'), fullAccess=True)) or (prevChoices[-3] == 'History' and prevChoices[-2] != ''):
            return ['--- select ---','Track','History']
    
    
    @staticmethod    
    def getOptionsBoxTrack2(prevChoices): 
        '''
        See getOptionsBox1().
        '''
        if prevChoices[-2] in ['Track','History']:
            return '__track__' if prevChoices[-2] == 'Track' else '__history__', 
    
    
    @staticmethod    
    def getOptionsBoxTrack3Source(prevChoices): 
        '''
        See getOptionsBox1().
        '''
        if prevChoices[-1] in ['Track','History'] or (prevChoices[-3] == 'Track'and ProcTrackOptions.isValidTrack(prevChoices[0], prevChoices[-2].split(':'), fullAccess=True)) or (prevChoices[-3] == 'History' and prevChoices[-2] != ''): 
            return ['--- select ---','Track','History']
    
    @staticmethod    
    def getOptionsBoxTrack3(prevChoices): 
        '''
        See getOptionsBox1().
        '''
        if prevChoices[-2] in ['Track','History']:
            return '__track__' if prevChoices[-2] == 'Track' else '__history__',
    
    @staticmethod    
    def getOptionsBoxTrack4Source(prevChoices): 
        '''
        See getOptionsBox1().
        '''
        if prevChoices[-1] in ['Track','History'] or (prevChoices[-3] == 'Track'and ProcTrackOptions.isValidTrack(prevChoices[0], prevChoices[-2].split(':'), fullAccess=True)) or (prevChoices[-3] == 'History' and prevChoices[-2] != ''):
            return ['--- select ---','Track','History']
    
    @staticmethod    
    def getOptionsBoxTrack4(prevChoices): 
        '''
        See getOptionsBox1().
        '''
        if prevChoices[-2] in ['Track','History']:
            return '__track__' if prevChoices[-2] == 'Track' else '__history__', 
        
    @staticmethod    
    def getOptionsBoxTrack5Source(prevChoices): 
        '''
        See getOptionsBox1().
        '''
        if prevChoices[-1] in ['Track','History'] or (prevChoices[-3] == 'Track'and ProcTrackOptions.isValidTrack(prevChoices[0], prevChoices[-2].split(':'), fullAccess=True)) or (prevChoices[-3] == 'History' and prevChoices[-2] != ''):
            return ['--- select ---','Track','History']
    
    @staticmethod    
    def getOptionsBoxTrack5(prevChoices): 
        '''
        See getOptionsBox1().
        '''
        if prevChoices[-2] in ['Track','History']:
            return '__track__' if prevChoices[-2] == 'Track' else '__history__', 
        
    @staticmethod    
    def getOptionsBoxTrack6Source(prevChoices): 
        '''
        See getOptionsBox1().
        '''
        if prevChoices[-1] in ['Track','History'] or (prevChoices[-3] == 'Track'and ProcTrackOptions.isValidTrack(prevChoices[0], prevChoices[-2].split(':'), fullAccess=True)) or (prevChoices[-3] == 'History' and prevChoices[-2] != ''):
            return ['--- select ---','Track','History']
    
    @staticmethod    
    def getOptionsBoxTrack6(prevChoices): 
        '''
        See getOptionsBox1().
        '''
        if prevChoices[-2] in ['Track','History']:
            return '__track__' if prevChoices[-2] == 'Track' else '__history__', 
        
    
    @staticmethod    
    def getAllChosenTracks(choices): 
        '''
        See getOptionsBox1().
        '''
        allTracks = []
        trackParamNames = [('Track1Source', 'Track1'), ('Track2Source', 'Track2'),('Track3Source','Track3'),\
                            ('Track4Source', 'Track4'),('Track5Source', 'Track5'),('Track6Source','Track6')]  
        
        #print 'TEMP: ', choices, trackParamNames
        for source, trackName in [(getattr(choices, s), getattr(choices,t).split(':')) for s,t in trackParamNames if getattr(choices,t) not in [None,''] ]:
            if source == 'History':
                allTracks.append(trackName)
            elif source == 'Track' and ProcTrackOptions.isValidTrack(choices.Genome, trackName, fullAccess=True):
                allTracks.append(trackName)
        return allTracks
    @staticmethod
    def validateTracks(choices):
        '''
        See getOptionsBox1().
        '''
        allTracks = []
        trackParamNames = [('Track1Source', 'Track1'), ('Track2Source', 'Track2'),('Track3Source','Track3'),\
                            ('Track4Source', 'Track4'),('Track5Source', 'Track5'),('Track6Source','Track6')]  
        count = 0
        for trackNumber, source, trackName in \
                [(t, getattr(choices, s),
                 getattr(choices, t).split(':')) for s,t in trackParamNames
                 if isinstance(getattr(choices, t), basestring)]:
            count += 1
            if source == 'Tracks':
                if not ProcTrackOptions.isValidTrack(choices.Genome, trackName):
                    return 'Invalid track: the path for %s is not correctly specified' % trackNumber
        if count == 0:
            return 'No valid tracks chosen'
    
