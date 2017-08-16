from collections import OrderedDict


class TableCoreMixin(object):
    def tableFromDictionary(self, dataDict, columnNames=None, sortable=True,
                            tableId=None, expandable=False, visibleRows=6,
                            presorted=None, **kwargs):
        """Render a table from data in dataDict. Each key in dataDict is a row title,
        each value is a list of values, each corresponding to the column given with columnNames.

        If presorted is set to a number and tableId != None and sortable == True, that column will be presorted (using a hacky solution using jquery.
        """

        from proto import CommonFunctions
        dataDictOfLists = CommonFunctions.convertToDictOfLists(dataDict)

        if presorted is not None and presorted > -1:
            assert isinstance(presorted, int), 'presorted must be int'
            from quick.util import CommonFunctions
            dataDictOfLists = CommonFunctions.smartSortDictOfLists(
                dataDictOfLists, sortColumnIndex=presorted)

        tableClass = 'colored bordered'
        if expandable:
            tableClass += ' expandable'

        self.tableHeader(headerRow=columnNames, sortable=sortable,
                         tableId=tableId,
                         tableClass=tableClass, **kwargs)

        for key, val in dataDictOfLists.iteritems():
            if isinstance(val, list):
                self.tableLine([key] + val, **kwargs)
            else:
                self.tableLine([key] + [val], **kwargs)

        self.tableFooter(expandable=expandable, tableId=tableId,
                         numRows=len(dataDict), visibleRows=visibleRows, **kwargs)

        return self

    def tableFromDictOfDicts(self, dataDict, firstColName='', **kwargs):
        """
        # Note: it is assumed that dataDict is a full matrix, i.e. each element in
        # the dict is a dict of the same size.
        """

        assert isinstance(dataDict, OrderedDict) and \
               all(isinstance(x, OrderedDict) for x in dataDict.values()), \
            'dataDict must be an OrderedDict of OrderedDicts'

        from proto.CommonFunctions import fromDictOfDictsToDictOfListsAndColumnNameList
        convertedDataDict, colNames = \
            fromDictOfDictsToDictOfListsAndColumnNameList(dataDict, firstColName)

        self.tableFromDictionary(convertedDataDict,
                                 columnNames=colNames,
                                 **kwargs)
        return self
