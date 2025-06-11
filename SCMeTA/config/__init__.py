from .load import PARAMETERS, SYSTEM
from .mz_filter import INCLUDE_LIST, EXCLUDE_LIST
import logging

# Create a logger
logging.basicConfig(
    format="[%(asctime)s][\033[32m%(levelname)s\033[0m] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

TQDM_FORMAT = "{l_bar}{bar:10}{r_bar}{bar:-10b}"