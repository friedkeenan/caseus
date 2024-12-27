import importlib.metadata

# Dynamically get version.
__version__ = importlib.metadata.version(__name__)

# Remove import from our exported variables
del importlib

from . import types
from . import clients
from . import proxies
from . import secrets
from . import servers
from . import game

from .packets import *

from .clients  import Client
from .proxies  import Proxy
from .secrets import Secrets
from .servers  import MinimalServer
