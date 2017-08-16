from config.Config import DebugModes, DebugConfig
from gold.application.LogSetup import setupDebugModeAndLogging


class DebugMixin(object):
    @classmethod
    def getInputBoxNamesForDebug(cls):
        return [('Debug mode', 'debugMode')]
        
    @classmethod
    def getOptionsBoxDebugMode(cls, prevChoices):
        if cls.isDebugMode():
            return [DebugModes.NO_DEBUG,
                    DebugModes.PROFILING,
                    DebugModes.UNCHANGED_LOGIC_VERBOSE,
                    DebugModes.UNCHANGED_LOGIC_TRACE_CREATE_VERBOSE,
                    DebugModes.UNCHANGED_LOGIC_TRACE_COMPUTE_VERBOSE,
                    DebugModes.UNCHANGED_LOGIC_FULL_TRACE_VERBOSE,
                    DebugModes.RAISE_HIDDEN_EXCEPTIONS_NO_VERBOSE,
                    DebugModes.RAISE_HIDDEN_EXCEPTIONS_WITH_VERBOSE,
                    DebugModes.RAISE_HIDDEN_EXCEPTIONS_FULL_TRACE_VERBOSE,
                    DebugModes.RAISE_HIDDEN_EXCEPTIONS_INCLUDING_NONE_WITH_VERBOSE,
                    DebugModes.RAISE_HIDDEN_EXCEPTIONS_INCLUDING_NONE_FULL_TRACE_WITH_VERBOSE]

    @classmethod
    def getInputBoxGroups(cls, choices=None):
        if hasattr(super(DebugMixin, cls), 'getInputBoxGroups'):
            return super(DebugMixin, cls).getInputBoxGroups(choices)
        return None

    @staticmethod
    def _setDebugModeIfSelected(choices):
        if choices.debugMode:
            if choices.debugMode == DebugModes.NO_DEBUG:
                DebugConfig.changeMode(choices.debugMode)
            else:
                #Sets up std.out and std.err to pipe debug and error log messages, respectively,
                #in addition to setting the debug mode
                setupDebugModeAndLogging(choices.debugMode)
            #print DebugConfig

