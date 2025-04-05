"""
This package provides positional encodings for spatial objects.
Encoding methods are provided as classes that implement a particular approach.
At this time, this includes:

- `MPPEncoder`: Multi-PointProximity encoding.
- `DIVEncoder`: Discrete Indicator Vector encoding.

This package works with `shapely.Geometry` objects, which includes the "primitive" types 
(`shapely.Point`, `shapely.LineString`, and `shapely.Polygon`) 
as well as "multipart" types 
(`shapely.MultiPoint`, `shapely.MultiLineString`, and `shapely.MultiPolygon`).

"""

__version__ = "1.0.4"
__author__ = "John B Collins"

from .encoders import MPPEncoder
from .encoders import DIVEncoder
from .encoders import GeoEncoding
from .utilities import draw_shape


