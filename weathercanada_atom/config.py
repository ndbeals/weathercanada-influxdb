from loguru import logger
import sys
logger.remove()
logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <10}</level>| <level>{message}</level>")

import yaml
import pathlib

# with pathlib.Path().open('config.yml','r') as fp:
# fff = pathlib.Path(__file__).parent.parent
_base_path = pathlib.Path(__file__).parent.parent 
config_file = _base_path / 'config.yml'
with config_file.open('r') as fp:
    config = yaml.load(fp, Loader=yaml.FullLoader )