from yaml import YAMLObject
from .. import constants

class Prompt:

    def __init__(self, config:YAMLObject):
        self.config = config

    def provider(self):
        _provider = constants.PROVIDER_REGISTER.get(self.config['provider', None], None)
        if _provider:
            return _provider

        # If the provider specified in the config is not found in the registry, raise an error
        raise Exception("Unknown provider")

    def run(self):
        ...
