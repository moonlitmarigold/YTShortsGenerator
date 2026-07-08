from yaml import YAMLObject
from .. import providers
import logging
logger = logging.getLogger(__name__)

class Prompt:

    def __init__(self, config:providers.Base.ProviderConfig):
        self.config = config
        self.provider: providers.Base.BaseProvider = self._provider()

    def _provider(self):
        _provider = providers.PROVIDER_REGISTER.get(self.config.name, None)
        return _provider(self.config)

    def run(self):
        logger.info('Starting Prompt')
        logger.info('Prompt content: %s', self.config.prompt)
        response = self.provider.prompt()
        logger.info('Prompt response: %s', response)
        return response

