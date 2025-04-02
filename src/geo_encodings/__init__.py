"""
This package provides positional encodings for spatial objects.
Encoding methods are provided as classes that implement a particular approach.
At this time, this includes:

- `MPPEncoder`: Multi-PointProximity encoding.
- `DIVEncoder`: DIscrete Indicator Vector encoding.

"""


__version__ = "1.0.0"
__author__ = "John B Collins"

from .encoders import MPPEncoder
from .encoders import DIVEncoder
from .encoders import GeoEncoding
from .vis import px_draw
