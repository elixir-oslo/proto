from config.Config import STATIC_DIR, STATIC_PATH, STATIC_REL_PATH
from proto.StaticFile import StaticFile as ProtoStaticFile
from proto.StaticFile import StaticImage as ProtoStaticImage
from proto.StaticFile import GalaxyRunSpecificFile as ProtoGalaxyRunSpecificFile
from proto.StaticFile import PickleStaticFile as ProtoPickleStaticFile
from proto.StaticFile import RunSpecificPickleFile as ProtoRunSpecificPickleFile


class StaticFile(ProtoStaticFile):
    STATIC_DIR = STATIC_DIR
    STATIC_PATH = STATIC_PATH
    STATIC_REL_PATH = STATIC_REL_PATH


class StaticImage(ProtoStaticImage):
    STATIC_DIR = STATIC_DIR
    STATIC_PATH = STATIC_PATH
    STATIC_REL_PATH = STATIC_REL_PATH


class PickleStaticFile(ProtoPickleStaticFile):
    STATIC_DIR = STATIC_DIR
    STATIC_PATH = STATIC_PATH
    STATIC_REL_PATH = STATIC_REL_PATH


class RunSpecificPickleFile(ProtoRunSpecificPickleFile):
    STATIC_DIR = STATIC_DIR
    STATIC_PATH = STATIC_PATH
    STATIC_REL_PATH = STATIC_REL_PATH


class GalaxyRunSpecificFile(ProtoGalaxyRunSpecificFile):
    STATIC_DIR = STATIC_DIR
    STATIC_PATH = STATIC_PATH
    STATIC_REL_PATH = STATIC_REL_PATH

    def getExternalTrackName(self):
        from quick.application.ExternalTrackManager import ExternalTrackManager
        name = ExternalTrackManager.extractNameFromHistoryTN(self._galaxyFn)
        return ExternalTrackManager.createStdTrackName(self.getId(), name)
