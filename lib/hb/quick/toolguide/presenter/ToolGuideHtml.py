'''
Created on Feb 16, 2015

@author: diana
'''
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.toolguide.ToolGuideConfig import TOOL_INPUT_TYPE_TO_TOOL_GUIDE_HELP_HEADER_DICT, TOOL_GUIDE_HELP_HEADER_TEXT, TOOL_GUIDE_HELP_HEADER_TEXT_TEXT

class ToolGuideHtml(object):
    '''
    classdocs
    '''
    
    def __init__(self, guideDataDict):
        '''
        Constructor
        '''
        self._guideDataDict = guideDataDict
        self._guideContent = ''
        self._buildContent()
        
    def _buildContent(self):
        #iterate through dictionary and for each key create a section (one of [GSuite, Track...])
        # each value in the dictionary is a list of GiudeData objects that go into the section defined by the key
        htmlCore = HtmlCore()
        htmlCore.divBegin('toolGuideInfo')
        htmlCore.divBegin(divClass='toolGuideInfoText')
        htmlCore.divBegin(divClass='toolGuideInfoTextHeader')
        htmlCore.line(TOOL_GUIDE_HELP_HEADER_TEXT)
        htmlCore.divEnd()
        htmlCore.divBegin(divClass='toolGuideInfoText')
        htmlCore.line(TOOL_GUIDE_HELP_HEADER_TEXT_TEXT)
        htmlCore.divEnd()
        htmlCore.divEnd()
        for guideDataKey, guideDataValues in self._guideDataDict.iteritems():
            htmlCore.divBegin('toolGuide')
            if guideDataKey in TOOL_INPUT_TYPE_TO_TOOL_GUIDE_HELP_HEADER_DICT:
                htmlCore.header(TOOL_INPUT_TYPE_TO_TOOL_GUIDE_HELP_HEADER_DICT[guideDataKey])
            for guideDataValue in guideDataValues:
                htmlCore.divBegin(divClass='toolGuideData')
                htmlCore.divBegin(divClass='toolGuideImgTitle')
                if guideDataValue.imgUrl:
                    htmlCore.image(guideDataValue.imgUrl)
                htmlCore.link(text=guideDataValue.toolDisplayName, url=str(guideDataValue.toolUrl),
                              args=(' onclick="%s"' % guideDataValue.onclick)
                                    if guideDataValue.onclick else '')
                htmlCore.divEnd()
                htmlCore.divBegin(divClass='toolGuideDesc')
                htmlCore.append(guideDataValue.description)
                if guideDataValue.helpPageUrl:
                    htmlCore.link(text='...read more', url=str(guideDataValue.helpPageUrl))
                htmlCore.divEnd()
                htmlCore.divEnd()
            htmlCore.divEnd()
        htmlCore.divEnd()
        #raise Exception(str(htmlCore))#to debug
        self._guideContent = str(htmlCore)
        
    def getContent(self):
        #Mockup code, remove after implementation
        #return "<p><a href=" + CommonFunctions.createToolURL("hb_track_global_search_tool") + ">Tool</a></p>"
        return self._guideContent
    
    #def addGuideData(self, toolGuideData):
        #TODO: generate appropriate html for the ToolGuideData object
        #and concatenate it to self._guideContent
        #pass
