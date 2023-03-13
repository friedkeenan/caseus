try:
    import importlib.metadata as importlib_metadata

except ImportError:
    # TODO: Remove this when Python 3.7 support is dropped.
    import importlib_metadata

# Dynamically get version.
__version__ = importlib_metadata.version(__name__)

# Remove import from our exported variables
del importlib_metadata

from . import types
from . import clients
from . import proxies
from . import servers
from . import sniffers
from . import game

from .secrets import *
from .packets import *

from .clients  import Client
from .proxies  import Proxy
from .servers  import MinimalServer
from .sniffers import Sniffer
