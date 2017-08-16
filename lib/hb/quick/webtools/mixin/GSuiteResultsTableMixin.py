'''
Created on Feb 10, 2016

@author: boris
'''

from collections import OrderedDict

from gold.gsuite import GSuiteConstants
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN


class GSuiteResultsTableMixin(object):
    GSUITE_FILE_OPTIONS_BOX_KEY = 'gsuite'

    @classmethod
    def getInputBoxNamesForAttributesSelection(cls):
        return [('', 'resultsExplanation'),
                ('Select track attributes to display with the results page', 'additionalAttributes'),
                ('Select the leading attribute (by default "title")', 'leadAttribute')]

    @classmethod
    def getInputBoxGroups(cls, choices=None):
        if hasattr(super(GSuiteResultsTableMixin, cls), 'getInputBoxGroups'):
            return super(GSuiteResultsTableMixin, cls).getInputBoxGroups(choices)
        return None

    @classmethod
    def getOptionsBoxResultsExplanation(cls, prevChoices):
        core = HtmlCore()
        core.divBegin(divClass='resultsExplanation')

        core.paragraph('''
            The results page from this analysis will display the results in a table with one row per track.
            For your convenience you can include attribute (meta-data columns) from the selected GSuite to be displayed in the same table.
            Additionally you can select the leading column, which is by default the track title, but can also be any of the additional attributes you select here.
        ''')
        core.divEnd()

        return '__rawstr__', str(core)

    @classmethod
    def getOptionsBoxAdditionalAttributes(cls, prevChoices):
        galaxyGSName = getattr(prevChoices, cls.GSUITE_FILE_OPTIONS_BOX_KEY)
        if galaxyGSName:
            gsuite = getGSuiteFromGalaxyTN(galaxyGSName)
            if gsuite.attributes:
                return OrderedDict(zip(gsuite.attributes, [False] * len(gsuite.attributes)))

    @classmethod
    def getOptionsBoxLeadAttribute(cls, prevChoices):
        galaxyGSName = getattr(prevChoices, cls.GSUITE_FILE_OPTIONS_BOX_KEY)
        if galaxyGSName:
            if prevChoices.additionalAttributes and any(prevChoices.additionalAttributes.values()):
                return [GSuiteConstants.TITLE_COL] + [key for key, val in prevChoices.additionalAttributes.iteritems()
                                                      if val]

    @classmethod
    def getSelectedAttributesForEachTrackDict(cls, selectionDict, gsuite):
        additionalResultsDict = OrderedDict()
        if selectionDict and any(selectionDict.values()):
            attributes = [key for key, val in selectionDict.iteritems() if val]
            for attrName in attributes:
                for gsTrack in gsuite.allTracks():
                    if gsTrack.title not in additionalResultsDict:
                        additionalResultsDict[gsTrack.title] = OrderedDict()
                    additionalResultsDict[gsTrack.title][attrName] = gsTrack.getAttribute(
                        attrName) if gsTrack.getAttribute(attrName) else '.'
        return additionalResultsDict
