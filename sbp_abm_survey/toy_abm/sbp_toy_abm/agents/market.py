# -*- coding: utf-8 -*-
"""
Created on Thu May 28 14:53:15 2020

@author: giaco
"""

import mesa


class Market(mesa.Agent):
    """
    Agent representing the market, from where farmers access prices and
    economic values

    Attributes
    ----------
    ...

    """

    def __init__(self, unique_id, model):
        """
        Parameters
        ----------
        //

        """
        super().__init__(unique_id, model)
        self.discount_rate = 0.05
