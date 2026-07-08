from yaml import YAMLObject
from .. import providers
import json
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
        print(response)
        #split_response = response.split('\n')
        #clean_response = json.loads('\n'.join(split_response[1:-1]))
        #logger.info('Prompt response: %s', clean_response)

        #output = self.config.generation_output.model_validate(clean_response)
        #print(output)
        return response

