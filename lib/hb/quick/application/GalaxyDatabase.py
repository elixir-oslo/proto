from proto.config.GalaxyConfigParser import GalaxyConfigParser


def getGalaxyConfiguration():
    import galaxy.config
    configParser = GalaxyConfigParser()
    configDict = {}
    for key, value in configParser.items("app:main"):
        configDict[key] = value
    return galaxy.config.Configuration(**configDict)


def getGalaxyDatabaseModel():
    import galaxy.model.mapping
    """
    Returns a SQLAlchemy model and session --
    """
    config = getGalaxyConfiguration()

    model = galaxy.model.mapping.init( config.file_path, config.database_connection, engine_options={}, create_tables=False)
    return model

