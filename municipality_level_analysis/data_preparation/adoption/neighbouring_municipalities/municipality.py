# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 15:39:41 2020

@author: giaco
"""
from mesa_geo.geoagent import GeoAgent


class Municipality(GeoAgent):

    def __init__(self, unique_id, model, shape):
        super().__init__(unique_id, model, shape)

        # Attributes set by the Agent Creator from the Shapefile during the
        # initialization
        self.Municipality = ""
        self.District = ""

    def get_neighbours(self):
        neighbours = self.model.grid.get_neighbors(self)
        return [neighbour.Municipality for neighbour in neighbours]

    def get_neighbours_within_distance(self, distance):
        neighbours_within_distance = (
            self.model.grid.get_neighbors_within_distance(
                self, distance, center=False)
            )
        return [
            neighbour.Municipality for neighbour in neighbours_within_distance
            ]
