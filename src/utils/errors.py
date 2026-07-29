

class NoPipelineBuildList(Exception):

    def __init__(self):
        super().__init__('The Pipeline Build List is Empty and so not pipline can be build.')

class ConfigFileNotSet(Exception):

    def __init__(self):
        super().__init__('The config path was not set as a env variable')
