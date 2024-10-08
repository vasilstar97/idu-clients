"""
Clients for IDU projects APIs.
"""

import importlib

__version__ = importlib.metadata.version("idu_clients")
__author__ = ""
__email__ = ""
__credits__ = []
__license__ = "BSD-3"

from .urban_api import UrbanAPI
from .transport_frames_api import TransportFramesAPI