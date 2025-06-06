

import numpy as np
import shapely
import shapely.wkt
from scipy.sparse import csr_array


class GeoEncoding:

    """
    An encoding for a geometric object.

    Implementation note: The encoding is stored internally essentially as a set of
    indices of non-zero elements, and a set of the values of those indices. That is,
    the components of a sparse vector. These can be returned either as a scipy sparse
    vector or as a numpy dense vector as desired.

    If the `floor` parameter of the inpout encoder object is greater than zero, then
    the data will be saved as a sparse vector.

    Args:
        encoder: The encoder object that produced the data
        values: Values of the elements of the encoding
    """

    def __init__(self, encoder, values):
        if encoder.floor > 0.0:
            iok = values > encoder.floor
            self.indices = indices[iok]
            self.elements = values[iok]
        else:
            self.indices = None
            self.elements = values
        self.full_size = len(values)

    def __len__(self):
        return len(self.full_size)

    def sparse(self):
        """
        Return a sparse array representation of this encoding
        """
        if self.indices is None:
            # This isn't saved as a sparse array. But represent it as one anyway.
            row_indices = np.full(self.full_size, 0) # all zeros
            col_indices = np.arange(self.full_size)
        else:
            row_indices = np.full(len(self.indices), 0) # all zeros
            col_indices = self.indices
        return csr_array((self.elements, (row_indices, col_indices)), shape=(1, self.full_size))

    def values(self, override=False):
        """
        Return a dense vector representing this encoding.
        """
        if self.indices is not None:
            row_indices = np.full(len(self.indices), 0) # all zeros
            s = csr_array((self.elements, (row_indices, self.indices)), shape=(1, self.full_size))
            v = s.todense().ravel()
        else:
            v = self.elements
        return v


class MPPEncoder:

    """
    A class that generates Multi-Point Proximity (MPP) encodings for arbitrary geometries.

    This implementation of the MPP concept works with a grid of equally spaced points
    covering a rectangular region.
    
    Args:
        region:
            [x0, y0, x1, y1]: coordinates of the lower-left and upper-right
            corners of a rectangular area.
        resolution:
            The spacing between the reference points.
        scale:
            Factor for the distance weighting function.
            Default: equal to "resolution".
        center:
            If False (the default), then the initial point will be at coordinate (x0, y0).
            If True, then the initial point will be at (x0 + resolution / 2, y0 + resolution / 2),
            i.e. the center of a box of dimension "resolution".
        floor:
            If an encoding is less than this value, it will be set to zero. This lets
            us treat the encoding as a sparse vector. Default is zero.
    
    """

    def __init__(self, region:list[float], resolution:float, scale:float=None, center:bool=False, floor:float=0.0):

        # Collect the initialization parameters and do some rudimentary
        # calculations and re-formatting.
        self.x0, self.y0, self.x1, self.y1 = region
        self.resolution = resolution
        self.scale = self.resolution if scale is None else scale

        # Create the list of reference points for this region.
        offset = resolution / 2.0 if center else 0.0
        eps = self.resolution * 0.1
        xx = np.arange(self.x0 + offset, self.x1 + eps, self.resolution)
        yy = np.arange(self.y0 + offset, self.y1 + eps, self.resolution)
        self.nx = len(xx)
        self.ny = len(yy)
        mm = np.meshgrid(xx, yy)
        ref_x = mm[0].ravel()
        ref_y = mm[1].ravel()
        self.ref_points = [
            shapely.wkt.loads('POINT(%.1f %.1f)' % (zx, zy))
            for zx, zy in list(zip(ref_x, ref_y))
        ]
        self.ref_x = ref_x
        self.ref_y = ref_y
        self.ref_index = np.arange(len(self.ref_points))

        # This parameter gives the value below which encoding elements will be
        # set to zero.
        self.floor = floor

    def __len__(self):
        return len(self.ref_points)

    def encode(self, shape:shapely.Geometry) -> GeoEncoding:
        """
        Return a MPP encoding for a shape.
        
        Args:
            shape: the shape to be encoded
        """

        # Get the encoded values for each point.
        values = np.array([
            np.exp(-1.0 * shape.distance(ref_point) / self.scale)
            for ref_point in self.ref_points
        ])

        # Create the encoding using only elements whose value exceeds the threshold.
        e = GeoEncoding(self, values)

        return e


class DIVEncoder:

    """
    A class that generates Discrete Indicator Vector (DIV) encodings for arbitrary geometries.

    This implementation of the DIV encoding concept works with square tiles that cover
    a rectangular region.

    Args:
        region: [x0, y0, x1, y1]: Coordinates of the lower-left and upper-right corners of a rectangular region.
        resolution: The size of the (square) tiles dividing the region.
        sparse: If True, store as a sparse vector.
    """

    def __init__(self, region:list[float], resolution:float, sparse:bool=False):


        # Collect the initialization parameters and do some rudimentary
        # calculations and re-formatting.
        self.x0, self.y0, self.x1, self.y1 = region
        self.resolution = resolution

        # If this is set to anything above zero, then the encoding will be stored
        # as a sparse vector. That will get taken care of in the "GeoEncoding" class 
        # based on the value of the "floor" parameter. This sets it appropriately. 
        self.floor = 0.5 if sparse else 0.0

        # Create a list of tiles.
        eps = self.resolution * 0.1
        xx = np.arange(self.x0, self.x1 - eps, self.resolution)
        yy = np.arange(self.y0, self.y1 - eps, self.resolution)
        self.nx = len(xx)
        self.ny = len(yy)
        mm = np.meshgrid(xx, yy)
        ref_x = mm[0].ravel()
        ref_y = mm[1].ravel()
        self.tiles = []
        for i in range(len(ref_x)):
            x0, y0 = ref_x[i], ref_y[i]
            x1, y1 = x0 + resolution, y0 + resolution
            wkt = f"POLYGON(({x0} {y0}, {x1} {y0}, {x1} {y1}, {x0} {y1}, {x0} {y0}))"
            self.tiles.append(shapely.from_wkt(wkt))
        self.tile_index = np.arange(len(self))

    def __len__(self):
        return len(self.tiles)

    def encode(self, shape:shapely.Geometry) -> GeoEncoding:
        """
        Return a DIV encoding for a shape.

        Args:
            shape: The shape to be encoded.
        """
        indicators = np.array([
            1.0 if shapely.intersects(shape, tile) else 0.0
            for tile in self.tiles
        ])
        e = GeoEncoding(self, indicators)
        return e
