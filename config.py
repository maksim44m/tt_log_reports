import logging
from pathlib import Path

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

BASE_DIR = Path(__file__).parent.absolute()
