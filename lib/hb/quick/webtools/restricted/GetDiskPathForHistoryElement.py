from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.webtools.GeneralGuiTool import GeneralGuiTool


#This is a template prototyping GUI that comes together with a corresponding web page.
#

class GetDiskPathForHistoryElement(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Fetch full disk path for data behind history element"

    @staticmethod
    def getInputBoxNames(prevChoices=None):
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Genome (not required)', 'History element:', 'Read off disk path']

    @staticmethod
    def getOptionsBox1():
        return '__genome__'

    @staticmethod
    def getOptionsBox2(prevChoices):
        "Returns a list of options to be displayed in the first options box"
        #return ('__history__',('bed','category.bed','wig'))
        return ('__history__',)

    @staticmethod
    def getOptionsBox3(prevChoices):
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)
        '''
        if prevChoices[1] is not None:
            galaxyTN = prevChoices[1].split(':')
            fn = ExternalTrackManager.extractFnFromGalaxyTN(galaxyTN)
            return fn, True

    #    return prevChoices[0], 1, True

    #@staticmethod
    #def getOptionsBox3(prevChoices):
    #    return ['']

    #@staticmethod
    #def getOptionsBox4(prevChoices):
    #    return ['']

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history.
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''

        #print 'Executing...'
        genome = choices[0]
        galaxyTN = choices[1].split(':')
        #print 'galaxyTN: ',galaxyTN , type(galaxyTN)
        fn = ExternalTrackManager.extractFnFromGalaxyTN(galaxyTN)
        print 'Disk path for selected history element: <br>%s<br><br>' % fn
        from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
        staticFile = GalaxyRunSpecificFile([],fn)
        print 'HyperBrowser data path (static file path) corresponding to selected history element: <br>%s<br><br>' % staticFile.getDiskPath()

        from config.Config import EXT_PROCESSED_DATA_PATH
        try:
            tn = ExternalTrackManager.getStdTrackNameFromGalaxyTN(galaxyTN)[:-1]
            preProcPath = '/'.join([EXT_PROCESSED_DATA_PATH,'100000','noOverlaps',genome] + tn)
            import os
            lastTnPart = os.listdir(preProcPath)
            assert len(lastTnPart)==1, lastTnPart
            #preProcPath += '/'+lastTnPart[0]
            tn += lastTnPart
            preProcPath = '/'.join([EXT_PROCESSED_DATA_PATH,'100000','noOverlaps',genome] + tn)

            print 'HyperBrowser pre-processed track name (if applicable): <br>%s<br><br>' % tn
            print 'HyperBrowser pre-processed track path (if applicable): <br>%s<br><br>' % preProcPath
        except:
            print '(Not printing track name, as history element does not appear to be a (valid) track.)<br>'
        print 'HyperBrowser URL path (static file URL) corresponding to selected history element: <br>%s<br><br>' % staticFile.getURL()

        # Does not work correctly, as the id needs to be the history id, and not the dataset id,
        # which may be different. Dataset id may perhaps be found from history id in the following manner (untested):
        #
        # data = trans.sa_session.query( trans.app.model.HistoryDatasetAssociation ).get( trans.security.decode_id( history_id ) )
        # dataset_id = extractIdFromGalaxyFn(data.file_name)
        #
        # Not sure how to go the other way.
        #
        #from quick.util.CommonFunctions import extractIdFromGalaxyFn
        #from galaxy.web.security import SecurityHelper
        #from config.Config import GALAXY_ID_SECRET
        #secHelper = SecurityHelper(id_secret=GALAXY_ID_SECRET)
        #id = extractIdFromGalaxyFn(galaxyFn)
        #encodedId = secHelper.encode_id(id[1])
        #print 'Galaxy URL id: <br>%s<br><br>' % encodedId

        import os.path, time
        print "Time of creation for Galaxy history file: %s" % time.ctime(os.path.getctime(fn))
        print "Last modification for Galaxy history file: %s" % time.ctime(os.path.getmtime(fn))


        #from quick.util.CommonFunctions import extractIdFromGalaxyFn,getUniqueWebPath
        #id = extractIdFromGalaxyFn(fn)
        #print 'HyperBrowser obsolete data path (used still for presenters) corresponding to selected history element: <br>%s<br><br>' % getUniqueWebPath(id)
        #print '<br>'
        #print '<br>'.join(galaxyTN)

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        if choices[0] == '':
            return 'Please select a genome.'

        if choices[1] is None:
            return 'Please select a history element.'

        return None

    #@staticmethod
    #def isPublic():
    #    return False
    #
    #@staticmethod
    #def isRedirectTool():
    #    return False
    #
    #@staticmethod
    #def getToolDescription():
    #    return ''
    #
    #@staticmethod
    #def getToolIllustration():
    #    return None
    #
    #@staticmethod
    #def isDebugMode():
    #    return True
    #
    @staticmethod
    def getResetBoxes():
        return [2]
    #
    #@staticmethod
    #def isRedirectTool():
    #    return False
    #
    #@staticmethod
    #def getOutputFormat():
    #    return 'html'
    #
    #@staticmethod
    #def validateAndReturnErrors(choices):
    #    '''
    #    Should validate the selected input parameters. If the parameters are not valid,
    #    an error text explaining the problem should be returned. The GUI then shows this
    #    to the user and greys out the execute button. If all parameters are valid, the method
    #    whould return None, which enables the execute button.
    #    '''
    #    return None
