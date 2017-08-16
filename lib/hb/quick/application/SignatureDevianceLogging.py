from third_party.typecheck import Checker, getargspec, type_name
from gold.application.LogSetup import SIGNATURE_DEVIANCE_LOGGER, logMessageOnce

NO_CHECK = False
from config.Config import IS_EXPERIMENTAL_INSTALLATION

#def takes_strict():
#    pass

def takes(*args, **kwargs):
    "Method signature checking decorator"

    # convert decorator arguments into a list of checkers

    checkers = []
    for i, arg in enumerate(args):
        checker = Checker.create(arg)
        if checker is None:
            if IS_EXPERIMENTAL_INSTALLATION:
                raise TypeError("@takes decorator got parameter %d of unsupported "
                            "type %s" % (i + 1, type_name(arg)))
            else:
                logMessageOnce("@takes decorator got parameter %d of unsupported " +
                            "type %s" % (i + 1, type_name(arg)), level=5, logger=SIGNATURE_DEVIANCE_LOGGER)
        checkers.append(checker)

    kwcheckers = {}
    for kwname, kwarg in kwargs.iteritems():
        checker = Checker.create(kwarg)
        if checker is None:
            if IS_EXPERIMENTAL_INSTALLATION:
                raise TypeError("@takes decorator got parameter %s of unsupported "
                            "type %s" % (kwname, type_name(kwarg)))
            else:
                logMessageOnce("@takes decorator got parameter %s of unsupported " +
                            "type %s" % (kwname, type_name(kwarg)), level=5, logger=SIGNATURE_DEVIANCE_LOGGER)
        kwcheckers[kwname] = checker

    if NO_CHECK: # no type checking is performed, return decorated method itself

        def takes_proxy(method):
            return method        

    else:

        def takes_proxy(method):
            
            method_args, method_defaults = getargspec(method)[0::3]

            def takes_invocation_proxy(*args, **kwargs):
    
                # append the default parameters

                if method_defaults is not None and len(method_defaults) > 0 \
                and len(method_args) - len(method_defaults) <= len(args) < len(method_args):
                    args += method_defaults[len(args) - len(method_args):]

                # check the types of the actual call parameters

                for i, (arg, checker) in enumerate(zip(args, checkers)):
                    if not checker.check(arg):
                        #raise InputParameterError("%s() got invalid parameter "
                                                  #"%d of type %s" %
                                                  #(method.__name__, i + 1, 
                                                   #type_name(arg)))
                        mainMessage = "%s() got invalid parameter %d of type %s" %\
                                                  (method.__name__, i + 1, 
                                                   type_name(arg))                        
                        logMessageOnce(mainMessage, level=5, logger=SIGNATURE_DEVIANCE_LOGGER)
                        

                for kwname, checker in kwcheckers.iteritems():
                    if not checker.check(kwargs.get(kwname, None)):
                        #raise InputParameterError("%s() got invalid parameter "
                                                  #"%s of type %s" %
                                                  #(method.__name__, kwname, 
                                                   #type_name(kwargs.get(kwname, None))))
                        logMessageOnce("%s() got invalid parameter " 
                                                  "%s of type %s" %
                                                  (method.__name__, kwname, 
                                                   type_name(kwargs.get(kwname, None))), level=5, logger=SIGNATURE_DEVIANCE_LOGGER)

                return method(*args, **kwargs)

            takes_invocation_proxy.__name__ = method.__name__
            return takes_invocation_proxy
    
    return takes_proxy

def returns(sometype):
    "Return type checking decorator"

    # convert decorator argument into a checker

    checker = Checker.create(sometype)
    if checker is None:
        #raise TypeError("@returns decorator got parameter of unsupported "
        #                "type %s" % type_name(sometype))
        logMessageOnce("@returns decorator got parameter of unsupported "
                        "type %s" % type_name(sometype), level=5, logger=SIGNATURE_DEVIANCE_LOGGER)

    if NO_CHECK: # no type checking is performed, return decorated method itself

        def returns_proxy(method):
            return method

    else:

        def returns_proxy(method):
            
            def returns_invocation_proxy(*args, **kwargs):
                
                result = method(*args, **kwargs)
                
                if not checker.check(result):
                    #raise ReturnValueError("%s() has returned an invalid "
                    #                       "value of type %s" % 
                    #                       (method.__name__, type_name(result)))
                    logMessageOnce("%s() has returned an invalid "
                                           "value of type %s" % 
                                           (method.__name__, type_name(result)), level=5, logger=SIGNATURE_DEVIANCE_LOGGER)

                return result
    
            returns_invocation_proxy.__name__ = method.__name__
            return returns_invocation_proxy
        
    return returns_proxy
