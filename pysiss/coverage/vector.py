""" file:   vector.py (pysiss.coverage)
    author: Jess Robertson
            CSIRO Minerals Resources Flagship
    date:   Monday 25 August, 2014

    desription: Implementation of classes for vector coverage data
"""

from .utilities import project, id_object


class MappedFeature(id_object):

    """ Class containing vector GIS data.

        Corresponds roughly to gsml:MappedFeatures
    """

    def __init__(self, ident, shape, projection, metadata):
        super(MappedFeature, self).__init__()
        self.ident = ident

        # Store some info on the shape
        self.shape = shape
        self.centroid = self.shape.representative_point()

        # Store metadata
        self.projection = projection
        self.metadata = metadata

    def __repr__(self):
        """ String representation
        """
        info = 'MappedFeature {0} somewhere near {1} contains '
        info_str = info.format(self.name, self.centroid)
        return info_str

    def reproject(self, new_projection):
        """ Reproject the shape to a new projection.

            :param new_projection: The identifier for the new projection
            :type new_projection: int
        """
        self.shape = type(self.shape)(project(self.shape.positions))
