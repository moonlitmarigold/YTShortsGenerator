from yaml import YAMLObject
from .. import providers
import logging
logger = logging.getLogger(__name__)

class Prompt:

    def __init__(self, config:YAMLObject):
        self.config = config

    def provider(self):
        _provider = providers.PROVIDER_REGISTER.get(self.config['provider'], None)
        if _provider:
            return _provider

        # If the provider specified in the config is not found in the registry, raise an error
        raise Exception("Unknown provider")

    def run(self):
        logger.info('Starting Prompt')
        logger.info('Prompt content: %s', self.config.get('prompt'))
        provider_class = self.provider()(self.config)
        response = provider_class.prompt()
        logger.info('Prompt response: %s', response)
        return response

