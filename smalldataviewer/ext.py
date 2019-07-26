import sys
import logging
import traceback
import warnings
from importlib import import_module

logger = logging.getLogger(__name__)


EXTRAS = ["h5py", "z5py", "pyn5", "PIL", "imageio"]

__all__ = ["NoSuchModule"] + EXTRAS


class NoSuchModule(object):
    def __init__(self, name):
        # logger.warning('Module {} is not accessible, some features may be unavailable'.format(name))
        self.__name = name
        self.__traceback_str = traceback.format_tb(sys.exc_info()[2])
        errtype, value = sys.exc_info()[:2]
        self.__exception = errtype(value)

    def __getattr__(self, item):
        print(self.__traceback_str, file=sys.stderr)
        raise self.__exception

    def __bool__(self):
        return False


def import_if_available(name, namespace):
    try:
        with warnings.catch_warnings(record=True):
            warnings.filterwarnings("ignore", ".*issubdtype")
            module = import_module(name)
    except ImportError as e:
        module = NoSuchModule(name)

    namespace[name] = module
    return module


for extra in EXTRAS:
    import_if_available(extra, locals())
