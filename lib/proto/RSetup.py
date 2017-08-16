try:
    from rpy2.robjects import r
    import rpy2.robjects as robjects
    import rpy2.rinterface as ri

    import rpy2.rpy_classic
    rpy2.rpy_classic.set_default_mode(rpy2.rpy_classic.NO_CONVERSION)
    from rpy2.rpy_classic import r as rpy1

    import numpy, collections
    from rpy2.robjects import numpy2ri
    numpy2ri.activate()

    def replaceNone(obj):
        if isinstance(obj, basestring):
            return obj

        if isinstance(obj, collections.Iterable):
            obj = [replaceNone(_) for _ in obj]

        if obj is None:
            return robjects.NA_Real

        return obj

    def iterToVector(obj):
        obj = numpy.array(replaceNone(obj))
        if obj.dtype.kind == 'O':
            return obj

        return numpy2ri.numpy2ri(obj)

    robjects.conversion.py2ri.register(list, iterToVector)
    robjects.conversion.py2ri.register(tuple, iterToVector)
    robjects.conversion.py2ri.register(collections.Iterable, iterToVector)
    robjects.conversion.py2ri.register(type(None), replaceNone)

    @robjects.conversion.py2ri.register(dict)
    def dictToList(obj):
        from rpy2.robjects import ListVector
        return ListVector(obj)

    def asNumpyScalar(obj):
        return numpy.array([obj])[0]

    def asScalar(obj):
        obj = robjects.default_converter.ri2ro(obj)

        if len(obj) == 1:
            obj = asNumpyScalar(obj[0])
        else:
            obj = numpy.asarray(obj)

        return obj

    robjects.conversion.ri2ro.register(ri.IntSexpVector, asScalar)
    robjects.conversion.ri2ro.register(ri.FloatSexpVector, asScalar)
    robjects.conversion.ri2ro.register(ri.BoolSexpVector, asScalar)
    robjects.conversion.ri2ro.register(ri.ComplexSexpVector, asScalar)
    robjects.conversion.ri2ro.register(ri.StrSexpVector, asScalar)

    robjects.conversion.ri2ro.register(ri.NACharacterType, asNumpyScalar)
    robjects.conversion.ri2ro.register(ri.NAComplexType, asNumpyScalar)
    robjects.conversion.ri2ro.register(ri.NAIntegerType, asNumpyScalar)
    robjects.conversion.ri2ro.register(ri.NALogicalType, asNumpyScalar)
    robjects.conversion.ri2ro.register(ri.NARealType, asNumpyScalar)

    robjects.conversion.ri2py.register(int, lambda x: x)
    robjects.conversion.ri2py.register(float, lambda x: x)
    robjects.conversion.ri2py.register(bool, lambda x: x)
    robjects.conversion.ri2py.register(type(None), lambda x: x)
    robjects.conversion.ri2py.register(numpy.ndarray, lambda x: x)
    robjects.conversion.ri2py.register(numpy.generic, lambda x: x)


except Exception, e:
    print "Failed importing rpy2. Error: ", e


def getRVersion():
    verDict = r('version')
    try:
        return '%s.%s' % (verDict.rx2('major')[0], verDict.rx2('minor')[0])
    except:
        return '%s.%s' % (verDict[verDict.names.index('major')], verDict[verDict.names.index('minor')])
