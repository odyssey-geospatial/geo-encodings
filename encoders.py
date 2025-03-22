

import numpy as np
import shapely
import shapely.wkt
from scipy.sparse import csr_array


class GeoEncoding:

    """
    An encoding for a geometric object.

    Implementation note: The encoding is stored internally essentially as a set of
    indices of non-zero elements, and a set of the values st those indices. That is,
    the components of a sparse vector. These can be returned either as a scipy sparse
    vector or as a numpy dense vector as desired.
    """
    
    def __init__(self, encoder, indices, values):
        self.indices = indices
        self.weights = values
        self.full_size = len(encoder)

    def sparse(self):
        """
        Return a sparse array representation of this encoding
        """
        row_indices = np.full(len(self.indices), 0)
        return csr_array((self.weights, (row_indices, self.indices)), shape=(1, self.full_size))

    def values(self, override=False):
        """
        Return a dense vector representing this encoding.
        """
        row_indices = np.full(len(self.indices), 0)
        s = csr_array((self.weights, (row_indices, self.indices)), shape=(1, self.full_size))
        return s.todense().ravel()


class MPPEncoder:

    """
    A class that generates Multi-Point Proximity (MPP) encodings for arbitrary geometries
    """

    def __init__(self, domain, resolution, scale=None, center=False, floor=0.0):

        """Initializes a MPPEncodier object.

        Creates an object that can be used to create encodings for arbitrary
        spaital objects. It will consist of a regular grid of reference points across
        a rectangular domain.

        Args:
            domain:
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
            	us treat the encoding as a sparse vector.
        """

        # Collect the initialization parameters and do some rudimentary
        # calculations and re-formatting.
        self.x0, self.y0, self.x1, self.y1 = domain
        self.resolution = resolution
        self.scale = self.resolution if scale is None else scale

        # Create the list of ref points for this domain.
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
        self.ref_index = np.arange(self.n_ref)

        # This parameter gives the value below which encoding loadings will be
        # set to zero.
        self.floor = floor

    def __len__(self):
        return len(self.ref_points)

    def encode(self, shape):
        """
        Return a MPP encoding for a shape.
        """

        # Get the loadings for each point.
        loadings = np.array([
            np.exp(-1.0 * shape.distance(ref_point) / self.scale)
            for ref_point in self.ref_points
        ])

        # Create the encoding using only points whose value exceeds the threshold.
        iok = loadings > self.floor
        e = GeoEncoding(self, self.ref_index[iok], loadings[iok])
        return e


class DIVEncoder:

    """
    A class that generates Discrete Indicator Vector (DIV) encodings for arbitrary geometries
    """

    def __init__(self, domain, resolution):

        """Initializes a DIVEncoder object.

        Creates an object that can be used to create encodings for arbitrary
        spaital objects. The encoding is relative to a tiling of a domain into
        discrete square tiles. An encoding for an object consists of an indcator
        vector indicating which tiles intersect the object.

        Args:
            domain:
                [x0, y0, x1, y1]: coordinates of the lower-left and upper-right
                corners of a rectangular area.
            resolution:
            	The size of the (square) tiles dividing the domain.
        """

        # Collect the initialization parameters and do some rudimentary
        # calculations and re-formatting.
        self.x0, self.y0, self.x1, self.y1 = domain
        self.resolution = resolution

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

    def encode(self, geom):
        """
        Return a DIV encoding for a shape.
        """
        indicators = np.array([
            1.0 if shapely.intersects(geom, tile) else 0.0
            for tile in self.tiles
        ])
        iok = indicators > 0.5
        e = GeoEncoding(self, self.tile_index[iok], indicators[iok])
        return e
