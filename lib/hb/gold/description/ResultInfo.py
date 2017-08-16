#from gold.description.ResultInfo import ResultInfo
import gold.description.ResultInfoList as ResultInfoList
from gold.util.CommonFunctions import insertTrackNames

class ResultInfo:
    def __init__(self, trackName1, trackName2, statClassName):
        self._trackName1 = trackName1
        self._trackName2 = trackName2
        self._statClassName = statClassName

    def _getResultInfoKey(self, key, getGeneralKey=False):
        key = key.replace('-','_').replace(' ','_').replace('(','_').replace(')','_').replace(':','_')
        statClassName = self._statClassName

        if key.startswith('TSMC'):
            assert key.count('_') == 1
            statClassName = key.split('_')[1]
            from gold.application.StatRunner import StatJob
            key = StatJob.GENERAL_RESDICTKEY

        if getGeneralKey:
            return 'COMMON_' + key
        else:
            return statClassName + '_' + key

    def getColumnLabel(self, key):
        for asGeneral in [False,True]:
            try:
                label = vars(ResultInfoList)[ self._getResultInfoKey(key, asGeneral)][0]
                if label != '':
                    columnLabel = insertTrackNames( label, self._trackName1, self._trackName2, shortVersion=True)
                    if 'TSMC' in key:
                        columnLabel = 'Test statistic: ' + columnLabel
                    return columnLabel

            except KeyError:
                pass

        return key

    def getHelpText(self, key):
        for asGeneral in [False,True]:
            try:
                helpText = vars(ResultInfoList)[ self._getResultInfoKey(key, asGeneral) ][1]
                if helpText != '':
                    if helpText.startswith('_'):
                        helpText = helpText[1:]
                    else:
                        helpText = insertTrackNames(helpText, self._trackName1, self._trackName2)

                    if 'TSMC' in key:
                        helpText= 'Test statistic: ' + helpText
                    return helpText

            except KeyError:
                pass

        return ''
