import numpy as np

class GraphMatrix:
    """
    This class holds a matrix representation of a graph (GraphView). It consists of a 2 dimensional numpy array and
    a dict that maps IDs (strings) to row/column numbers. The row and column numbers are identical.

    This class supports indexing by subscripting IDs, like this: matrix['chr1*10', 'chr1*14']
    """
    def __init__(self, weights=None, ids={}):
        """
        'weights' must be a 2 dimensional array with weights
        """
        if weights == None:
            self.weights = np.array([])
        else:
            self.weights = np.array(weights) #a 2 dimensional numpy array holding the weights of a graph
        self.ids = ids #a mapping form IDs to row/column numbers in self.matrix


    def __str__(self):
        return "IDs:\n" + str(self.ids) + "\nWeights:\n" + str(self.weights)

    def __repr__(self):
        return "GraphMatrix @ " + str(id(self))+":\n"+ str(self) +"\n"

    def __len__(self):
        return len(self.weights)

    def _translate(self, array_of_ids):
        """
        Translates the IDs in array_of_ids to positions given in self.ids. This also works for nested lists.
        """
        translate = (lambda e: [translate(el) for el in e] if type(e) == list else self.ids[e])
        translated_items = [translate(i) for i in array_of_ids]
        return translated_items

    def __getitem__(self, item):
        """
        Supports tuples and list for coordinates in self.weights such
        as ('a', 'b') and ['a', 'b', 'c'] in addition to single values.
        """
        #if 'item' is a list of identities:
        if isinstance(item, list):
            #translate the IDs in 'item' to indexes by using
            #self.ids for mapping
            return self.weights[self._translate(item)]
        #if 'item' is a tuple
        elif len(item) == 2:
            item1 = item[0]
            item2 = item[1]
            return self.weights[self.ids[item1], self.ids[item2]]
        #if 'item' is anything else
        else:
            return self.weights[self.ids[item]]

    def __eq__(self, other):
        """
        Two GraphMatrix instances are considered equal by the '==' operator
        if all the values in the matrix are equal (but not necessarily at the same position).
        self.ids gives the index in the matrix for a given id, so this must be used.
        ids = {'a': 0, 'b': 1}
        weights = [[9, 3]
                   [5, 2]]
        is equal to:
        ids = {'a': 1, 'b': 0}
        weights = [[2, 5]
                   [3, 9]]
        """
        #we need this special case for empty arrays, because numpy
        #has some idiosyncrasies when comparing empty arrays.
        if self.weights.size == 0 or other.weights.size == 0:
            return self.weights.size == 0 and other.weights.size == 0
        #if their IDs are different, they can not be equal
        elif set(self.ids.iterkeys()) != set(other.ids.iterkeys()):
                return False
        #compare each element in self and other
        else:
            for idx in self.ids.iterkeys():
                for idy in self.ids.iterkeys():
                    if other[(idx, idy)] != \
                    self[(idx, idy)]:
                        return False
            #if this point is reached, all values in the matrix are equal
            return True

    def __ne__(self, other):
        """
        Two GraphMatrix instances 'a' and 'b' are considered not equal by the '!=' operator
        if 'a == b' is False. In other words it is defined as the complement of '=='.
        """
        return not self.__eq__(other)