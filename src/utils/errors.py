
class ProviderNotKnow(Exception):

    def __init__(self, provider_name, provider):
        super().__init__(f'The provider {provider_name} is not know, the list of know providers is {provider}')


class NoPipelineBuildList(Exception):

    def __init__(self):
        super().__init__('The Pipeline Build List is Empty and so not pipline can be build.')

class ConfigFileNotSet(Exception):

    def __init__(self):
        super().__init__('The config path was not set as a env variable')

class ConfigFileNotFound(Exception):
    def __init__(self, path):
        super().__init__(f'Cannot find config or env file in current path {path}. Either set a path via "--config" or "--env" or create the missing files.')

class RequestReturned429(Exception):

    def __init__(self):
        super().__init__("The Request returned a 429 on the request")

class NoResultsAfterRequestAttempts(Exception):

    def __init__(self, tries):
        super().__init__(f'Gave up after {tries} tries to make the api call')

class NoWikiquotePage(Exception):

    def __init__(self, title):
        super().__init__(f'Wikiquote has no page titled "{title}"')
