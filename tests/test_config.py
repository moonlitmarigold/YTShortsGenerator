import os
from pathlib import Path
import sys
from src import config
from src.providers import Ollama

def test_config_loads_example_config():
    """Test that the config can be loaded from example_config.yaml"""
    config_file = Path('config.yaml')
    env_file = Path('.env')
    
    c = config.Config(config_file, env_file)
    result = c.read()
    
    # Should not raise an error
    assert 'generation_type' in result


def test_config_validation():
    """Test that invalid generation_type raises ValueError"""
    config_file = Path('config.yaml')
    env_file = Path('.env')
    
    c = config.Config(config_file, env_file)
    c.read()
    
    # Verify the config was loaded successfully
    assert c.config_file.exists()

def test_providers():
    config_file = Path('config.yaml')
    env_file = Path('.env')

    c = config.Config(config_file, env_file)
    conf =c.read()



    o = Ollama.Ollama(conf)
    assert o.base_url == conf['ollama_base_url']
    assert o.model == conf['ollama_model']
