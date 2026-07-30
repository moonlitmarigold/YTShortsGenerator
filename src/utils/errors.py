

class NoPipelineBuildList(Exception):

    def __init__(self):
        super().__init__('The Pipeline Build List is Empty and so not pipline can be build.')

class ConfigFileNotSet(Exception):

    def __init__(self):
        super().__init__('The config path was not set as a env variable')

class ConfigFileNotFound(Exception):
    def __init__(self, path):
        super().__init__(f'Cannot find config or env file in current path {path}. Either set a path via "--config" or "--env" or create the missing files.')
