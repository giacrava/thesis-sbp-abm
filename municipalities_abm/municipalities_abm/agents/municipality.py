# -*- coding: utf-8 -*-

from mesa_geo.geoagent import GeoAgent


class Municipality(GeoAgent):
    """
    Class for Municipality object.

    Municipalities:

    Attributes
    ----------
    neighbors : list
        Names (strings) of the neighboring Municipality objects
    Municipality: str
        Name of the municipality
    District : str
        Name of the district of which municipality is part

    Methods
    ----------
    get_neighbors
        Retrieve the names of the neighboring Municipality objects

    """

    def __init__(self, unique_id, model, shape):
        """
        Initialize a Municipality agent.

        """
        super().__init__(unique_id, model, shape)

        self.neighbors = []

        # Attributes set by the Agent Creator from the Shapefile during the
        # initialization
        self.Municipality = ""
        self.District = ""

    def get_neighbors(self):
        """
        Called by the model during instantiation of Municipalities.

        Get touching neighbors (a list of their names, to avoid errors during
        the serialization in Json format for the visualization).

        To get them based on a certain distance, use
        get_neighbors_within_distance grid's method instead.

        """
        neighbors = self.model.grid.get_neighbors(self)
        self.neighbors = [neighbor.Municipality for neighbor in neighbors]

    def step(self):
        pass
