

import numpy as np
import shapely
import shapely.wkt
from scipy.sparse import csr_array


class MPPEncoding:

    """
    A Multi-Point Proximity (MPP) encoding for a geometric shape
    """
    
    max_dense_vector_size = 2048

    def __init__(self, model, indices, values):
        self.indices = indices
        self.values = values
        self.full_size = model.n_ref

    def sparse(self):
        """
        Return a sparse array representation of this encoding
        """
        row_indices = np.full(len(self.indices), 0)
        return csr_array((self.values, (row_indices, self.indices)), shape=(1, self.full_size))

    def dense(self, override=False):
        """
        Return a dense vector representing this encoding.
        """
        if self.full_size > self.max_dense_vector_size and override is False:
            raise ValueError('dense vector size would be too large')
        return self.sparse().todense()


class MPPEncoder:

    """
    An object that generates Multi-Point Proximity (MPP) encodings for arbitrary geometries
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
        x_index = np.round((ref_x - self.x0) / self.scale).astype(int)
        y_index = np.round((ref_y - self.y0) / self.scale).astype(int)
        ref_index = y_index * self.nx + x_index
        self.ref_points = [
            shapely.wkt.loads('POINT(%.1f %.1f)' % (zx, zy))
            for zx, zy in list(zip(ref_x, ref_y))
        ]
        self.n_ref = len(self.ref_points)
        self.ref_x = ref_x
        self.ref_y = ref_y
        self.ref_index = ref_index

        # This parameter gives the value below which encoding loadings will be
        # set to zero.
        self.floor = floor

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
        e = MultiPointProximityEncoding(self, self.ref_index[iok], loadings[iok])
        return e
