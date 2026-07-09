from yaml import YAMLObject
from .. import providers, generation_types, sessions
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

    @staticmethod
    def _parse_output(output:str):
        split_response = output.split('\n')
        print(split_response)
        if '```json' in split_response:
            index_front = split_response.index('```json') + 1
        else:
            index_front = 0
        split_response.reverse()
        index_back = len(split_response)
        if '```' in split_response:
            index_back -= split_response.index('```') - 1
        split_response.reverse()

        clean_response = json.loads('\n'.join(split_response[index_front:index_back]))
        return generation_types.schemas.GeneratedVideoScript.model_validate(clean_response)


    def run(self, session:sessions.SessionInfo):
        logger.debug('Prompt content: %s', self.config.prompt)
        response = self.provider.prompt()

        script = self._parse_output(response)
        logger.debug('LLM Response: %s', script.model_dump())

        session.inject_prompt_output(script, response)




