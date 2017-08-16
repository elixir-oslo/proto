from collections import OrderedDict
# from quick.application.SignatureDevianceLogging import takes, returns
from numpy import nan


# from gold.application.LogSetup import logMessage
from quick.util import NumpyUtils


class TableData(OrderedDict):
    """
    Contains a table (two-dimensional structure) of values.
    It inherits OrderedDict, and can act like a OrderedDict of OrderedDicts.
    Alternatively, one can set and/or retrieve its values in the form of a 
    numpy matrix with accompanying row- and column-names.
    """
    ORIGINAL_MODE_MATRIX = 'matrix'
    ORIGINAL_MODE_DICT = 'dict'

    def __init__(self, *args, **kwargs):
        OrderedDict.__init__(self)
        self._originalMode = None  # used in update
        self.update(*args, **kwargs)
        # numpy representation
        self._numpyMatrix = None
        self._rowNamesList = None
        self._colNamesList = None
        self._significanceMatrix = None

        self.rowClust = None
        self.colClust = None
        self.rowOrder = None
        self.colOrder = None

    @property
    def rowNames(self):
        return self._rowNamesList

    @property
    def rowNamesAsNumpyArray(self):
        from numpy import array
        if self.rowNames is not None:
            return array(self.rowNames)
        else:
            return array([])

    @property
    def columnNamesAsNumpyArray(self):
        from numpy import array
        if self.columnNames is not None:
            return array(self.columnNames)
        else:
            return array([])

    @property
    def columnNames(self):
        return self._colNamesList

    @property
    def numpyMatrix(self):
        if self._numpyMatrix is None:
            self._constructNumpyMatrixFromDictValues()

        # Translate to signed ints, as unsigned ints is not supported by R
        if self._numpyMatrix.dtype in ['uint32', 'uint64']:
            self._numpyMatrix.dtype = str(self._numpyMatrix.dtype)[1:]

        return self._numpyMatrix

    @property
    def significanceMatrix(self):
        return self._significanceMatrix

    # @takes()
    # @returns
    def setByNumpyData(self, numpyMatrix, rowNamesList, colNamesList, 
                       significanceMatrix=None):
        """Sets the table data of this object based on input in numpy form
        :param numpyMatrix: the numpy matrix object containing all the data
        :param rowNamesList: the row titles
        :param colNamesList: the column titles
        :param significanceMatrix: optional binary matrix showing significance
        """
        assert self._originalMode in [None, self.ORIGINAL_MODE_MATRIX],\
            ("TableData instance is already in %s mode. You are not allowed "
             "to set the numpy matrix directly.")
        assert numpyMatrix.shape[0] == len(rowNamesList),\
            ("The row names list and the shape of the matrix do not correspond"
             " to each other. Matrix columns = %s, Column names list size = %s" 
             % (numpyMatrix.shape[0], len(rowNamesList)))
        assert numpyMatrix.shape[1] == len(colNamesList),\
            ("The column names list and the shape of the matrix do not "
             "correspond to each other. Matrix columns = %s, Column names "
             "list size = %s""" % (numpyMatrix.shape[1], len(colNamesList)))

        if significanceMatrix is not None:
            assert significanceMatrix.shape == numpyMatrix.shape,\
                ("The shape of the significance matrix is not equal to the "
                 "shape of the base matrix. Significance matrix shape = %s"
                 ", base matrix shape = %s"
                 % (significanceMatrix.shape, numpyMatrix.shape))
            assert significanceMatrix.dtype == 'bool',\
                ("The significance matrix should be a binary matrix, with"
                 "dtype == 'bool'. The current dtype is '%s'"
                 % significanceMatrix.dtype)

        self._originalMode = self.ORIGINAL_MODE_MATRIX
        self._numpyMatrix = numpyMatrix
        self._rowNamesList = rowNamesList
        self._colNamesList = colNamesList
        self._significanceMatrix = significanceMatrix

    # # @takes()
    # # @returns
    # def getAsNumpyData(self):
    #     """Gets the table data of this object in numpy form, converting 
    #        between forms if necessary"""
    #     if self._numpyMatrix is None:
    #         self._constructNumpyMatrixFromDictValues()
    #     return self._numpyMatrix

    # def __setitem__(self, key, value):
    #    assert self._originalMode in [None, self.ORIGINAL_MODE_DICT]
    #    self._originalMode = self.ORIGINAL_MODE_DICT
    #    pass

    def __getitem__(self, key):

        # logMessage('TableData:In __getitem__ with key %s' % key)
        if self._originalMode == self.ORIGINAL_MODE_MATRIX \
                and len(self.keys()) == 0:
            # likely corresponds to user getting values from this
            # object for the first time
            self._constructDictStructureFromNumpyValues()

        if key not in self:
            # Creating entries and should thus assert original mode is dict
            assert self._originalMode in [None, self.ORIGINAL_MODE_DICT]
            self._originalMode = self.ORIGINAL_MODE_DICT
            self.__setitem__(key, OrderedDict())
        return OrderedDict.__getitem__(self, key)

    # @returns(None)
    def _constructNumpyMatrixFromDictValues(self):
        # constructs self._numpyMatrix etc from its own dict values
        """Creates a numpy matrix from the current ordered dictionary.
        Should be called only once."""
        # logMessage('Constructing numpy matrix from dict')
        assert self._originalMode in [None, self.ORIGINAL_MODE_DICT]
        assert not self._numpyMatrix, 'Numpy matrix already constructed'
        assert not self._rowNamesList, 'Row names list already created'
        assert not self._colNamesList, 'Column names list already created'

        rowSize = len(self)
        assert rowSize > 0, 'TableData instance is empty'
        colSize = max([len(x) for x in self.values()])
        assert all([len(x) == colSize for x in self.values()]),\
            ("TableData is an OrderedDict that must contain all entries for "
             "the matrix it represents. You must set all missing values to "
             "None or some other default value to be able to create a matrix")

        # self._rowNamesList = self.keys()
        # self._colNamesList = self.values()[0].keys()
        # self._numpyMatrix = empty((rowSize, colSize))
        #
        # for key1 in self:
        #     i = self._rowNamesList.index(key1)
        #     for key2 in self[key1]:
        #         j = self._colNamesList.index(key2)
        #         self._numpyMatrix[i, j] = self[key1][key2] \
        #            if self[key1][key2] else nan

        from pandas import DataFrame
        # pandas.DataFrame will make the first level keys in column, and
        # second level in rows, so we need to transpose
        df = DataFrame(self).transpose()
        dfColSize = df.shape[1]
        assert len(self.values()[0]) == dfColSize,\
            ("TableData is an OrderedDict that must contain all entries for "
             "the matrix it represents. You must set all missing values to "
             "None or some other default value to be able to create a matrix")

        df = df.reindex(index=self.keys(), columns=self.values()[0].keys())

        self._rowNamesList = df.index.tolist()
        self._colNamesList = df.columns.tolist()
        self._numpyMatrix = df.as_matrix()

    # @returns(None)
    def _constructDictStructureFromNumpyValues(self):
        # constructs self._numpyMatrix etc from its own dict values
        assert self._originalMode in [self.ORIGINAL_MODE_MATRIX],\
            "Not in matrix mode."
        for i, rowName in enumerate(self._rowNamesList):
            for j, colName in enumerate(self._colNamesList):
                if rowName not in self:
                    super(TableData, self).__setitem__(rowName, OrderedDict())
                self[rowName][colName] = self._numpyMatrix[i, j]

    def __setitem__(self, key, value, dict_setitem=dict.__setitem__):
        # logMessage('TableData:In __setitem__ key=%s value=%s' % (key, value))
        assert isinstance(value, OrderedDict),\
            ("TableData represents an OrderedDict of OrderedDicts, "
             "%s is not an allowed value for the first level, it " % value +
             "must be an OrderedDict")
        super(TableData, self).__setitem__(key, value,
                                           dict_setitem=dict_setitem)

    def update(self, *args, **kwargs):
        # logMessage('TableData:update' + str(args) + str(kwargs))
        assert self._originalMode in [None, self.ORIGINAL_MODE_DICT],\
            ("TableData is in % mode, changing the state through dictionary "
             "methods is not allowed")
        for k, v in dict(*args, **kwargs).iteritems():
            assert isinstance(v, OrderedDict)
            self[k] = v

    def getReducedTableData(self, removeRows=True, removeColumns=True,
                            removeValues=(0, nan)):
        """
        Remove rows and columns that have only values that are in the
        removeValues list, e.g. row with all zeros can be removed.
        :param removeRows rows will be removed when True
        :param removeColumns columns will be removed when True
        :param removeValues list of removable values
        :return reduced numpy matrix
        """
        if self._numpyMatrix is None:
            self._constructNumpyMatrixFromDictValues()
        reducedTableData = TableData()
        rowSize = len(self._rowNamesList)
        colSize = len(self._colNamesList)
        removeRowIndices = []
        removeColIndices = []
        from numpy import asarray
        if removeRows:
            for i in xrange(rowSize):
                if all([str(float(x)) in
                        [str(float(el)) for el in removeValues] for x in
                         asarray(self._numpyMatrix[i, :]).tolist()]):
                    removeRowIndices.append(i)
        if removeColumns:
            for j in xrange(colSize):
                if all([str(float(x)) in
                        [str(float(el)) for el in removeValues] for x in
                         asarray(self._numpyMatrix[:, j]).tolist()]):
                    removeColIndices.append(j)

        for i in xrange(rowSize):
            for j in xrange(colSize):
                if j not in removeColIndices and i not in removeRowIndices:
                    key1 = self._rowNamesList[i]
                    key2 = self._colNamesList[j]
                    reducedTableData[key1][key2] = self._numpyMatrix[i, j]

        return reducedTableData

    def getMaxElement(self):
        """Get the value and keys for the max element of the table"""
        val, rowInd, colInd = NumpyUtils.getNumpyMatrixMaxElement(self.numpyMatrix)
        return val, self.rowNames[rowInd], self.columnNames[colInd]

    def getMinElement(self):
        """Get the value and keys for the min element of the table"""
        val, rowInd, colInd = NumpyUtils.getNumpyMatrixMinElement(self.numpyMatrix)
        return val, self.rowNames[rowInd], self.columnNames[colInd]

# logging.basicConfig(level=logging.DEBUG)
# od1 = OrderedDict()
# od1['a'] = OrderedDict()
# od1['a']['x'] = 0
# od1['b'] = OrderedDict()
# od1['b']['x'] = 21
# od1['a']['y'] = 0
# od1['b']['y'] = 22
#
# t = TableData(od1)
#
# print 'Table data: ', t
#
# t['c']['x'] = 9
# t['c']['y'] = 99
#
# t=TableData()
#
# if 'a' in t:
#     print "It's here!!!"
#
# t['a']['x'] = 0
# print type(t['a'])
# t['a']['y'] = 0
# t['b']['x'] = 15
# t['b']['y'] = 19
#
#
# print t
# print t['a']
# print t['a']['x']
# print "Values: ", t.values()
#
# print t.numpyMatrix
# print t._rowNamesList
# print t._colNamesList
# tred = t.getReducedTableData()
# print tred.numpyMatrix
# print tred._rowNamesList
# print tred._colNamesList
#
# from numpy import empty
# mat = empty((2,3))
# for i in range(2):
#     for j in range(3):
#         mat[i, j] = (i+1)*j
#
# print mat
# t2 = TableData()
# t2.setByNumpyData(mat, range(2), range(3))
# print t2
# t2[0][0]
# print t2
# print t2.getReducedTableData()
