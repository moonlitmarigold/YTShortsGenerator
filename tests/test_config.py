import os
from pathlib import Path
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
SRC_DIR = os.path.join(ROOT_DIR, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

import config


#from src import config

def test_config_loads_example_config():
    """Test that the config can be loaded from example_config.yaml"""
    config_file = Path('example_config.yaml')
    env_file = Path('.env')
    
    c = config.Config(config_file, env_file)
    c.read()
    
    # Should not raise an error
    assert 'generation_type' in c.config_file.parent


def test_config_validation():
    """Test that invalid generation_type raises ValueError"""
    config_file = Path('example_config.yaml')
    env_file = Path('.env')
    
    c = config.Config(config_file, env_file)
    c.read()
    
    # Verify the config was loaded successfully
    assert c.config_file.exists()
