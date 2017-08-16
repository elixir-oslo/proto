# NB: imported by Galaxy (managers.hdas). Should not import other ProTo modules.
# This module will only be loaded once, during startup of Galaxy, and not dynamically by ProTo
# tools. This means changes in the module will not take effect until Galaxy is restarted.

from proto.config.GalaxyConfigParser import GalaxyConfigParser


def galaxyGetSecurityHelper():
    from galaxy.web.security import SecurityHelper

    config = GalaxyConfigParser()
    id_secret = config.getWithDefault('proto_id_secret',
                                      'USING THE DEFAULT IS ALSO NOT SECURE!',
                                      section='galaxy_proto')
    return SecurityHelper(id_secret=id_secret)


try:
    GALAXY_SECURITY_HELPER_OBJ = galaxyGetSecurityHelper()
except:
    GALAXY_SECURITY_HELPER_OBJ = None


def galaxySecureEncodeId(plainId):
    return GALAXY_SECURITY_HELPER_OBJ.encode_id(plainId)


def galaxySecureDecodeId(encodedId):
    return GALAXY_SECURITY_HELPER_OBJ.decode_id(str(encodedId))
