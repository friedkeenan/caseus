import importlib.metadata

# Dynamically get version.
__version__ = importlib.metadata.version(__name__)

# Remove import from our exported variables
del importlib

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
