# NB: imported by Galaxy (managers.hdas). Should not import other ProTo modules.
# This module will only be loaded once, during startup of Galaxy, and not dynamically by ProTo
# tools. This means changes in the module will not take effect until Galaxy is restarted.

import ast
import os
from ConfigParser import SafeConfigParser


GALAXY_BASE_DIR = os.path.abspath(os.path.dirname(__file__) + '/../../../.')


class GalaxyConfigParser(SafeConfigParser):
    def __init__(self):
        SafeConfigParser.__init__(self, {'here': GALAXY_BASE_DIR})

        self._configFn = None

        for configRelFn in [os.environ.get('GALAXY_CONFIG_FILE'),
                            'config/galaxy.ini',
                            'config/galaxy.ini.sample']:
            if configRelFn:
                self._configFn = GALAXY_BASE_DIR + '/' + configRelFn
                if os.path.exists(self._configFn):
                    self.read(self._configFn)
                    break
        else:
            raise Exception('No Galaxy config file found at path: ' + self._configFn)

    def getWithDefault(self, key, default, section='app:main'):
        try:
            val = self.get(section, key)
            if not isinstance(default, basestring):
                val = ast.literal_eval(val)
        except:
            val = default

        if type(val) != type(default):
            raise ValueError('Value for configuration "%s" in section "%s" of file "%s" ' %
                             (key, section, self._configFn) +
                             'is incorrect. The value "%s" is of different type ' % val +
                             'than the default value "%s": %s != %s' %
                             (default, type(val), type(default)))

        return val

