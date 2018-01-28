import logging

logger = logging.getLogger(__name__)
logger.propagate = False
_handler = logging.StreamHandler()
_formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s'
)
_handler.setFormatter(_formatter)
logger.addHandler(_handler)
logger.setLevel(logging.DEBUG)
