# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 15:51:44 2020

@author: giaco
"""

from mesa_geo.geoagent import GeoAgent


class Municipality(GeoAgent):
    """
    Class for Municipality object.

    Municipalities:
        - are the geographical layer of the simulation
        - contain the farms

    Attributes
    ----------
    neighbors : list
        Neighboring Municipality objects

    Methods
    ----------
    get_neighbors
        Retrieve the neighboring Municipality objects 

    """
    def __init__(self, unique_id, model, shape):
        """


        Returns
        -------
        None.

        """
        super().__init__(unique_id, model, shape)
        self.neighbors = []
        self.farms = []
        self.adoptedSBP = 0

    def get_neighbors(self):
        """
        Called by the model during instantiation of Municiapalities.
        
        Get touching neighbors.
        To get them based on a certain distance, use
        get_neighbors_within_distance grid's method instead.


        """
        self.neighbors = self.model.grid.get_neighbors(self)
