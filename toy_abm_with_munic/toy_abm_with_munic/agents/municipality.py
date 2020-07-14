# -*- coding: utf-8 -*-
"""
Created on Mon Jul 13 15:51:44 2020

@author: giaco
"""

from mesa_geo.geoagent import GeoAgent


class Municipality(GeoAgent):
    def __init__(self, unique_id, model, shape):
        """
        

        Returns
        -------
        None.

        """
        super().__init__(unique_id, model, shape)
