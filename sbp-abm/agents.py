# -*- coding: utf-8 -*-
"""
Created on Thu May 21 09:45:52 2020

@author: giaco
"""
import mesa


class Government(mesa.Agent):
    """
    Agent reporting the subsidies available for different pastures
    
    Attributes
    ----------
    possible_pastures: list of instances
        List of the pastures that each farm can have
    
    
    """   
    def __init__(self, unique_id, model):
        """

        Parameters
        ----------

        sbp_subsidy : dictionary
            Subsidies given to farmers for adoption of SBP in €/ha for each 
            year ACTUALLY IF WE ARE NOT CONSIDERING THE YEARS, CAN JUST BE 
            A LIST STARTING FROM YEAR 0 AND EACH YEAR INCREMENTING

        """
        super().__init__(unique_id, model)
        # self.sbp_subsidy = sbp_subsidy   ## INPUT VALUES MANUALLY
        

class Market(mesa.Agent):
    """
    Agent representing the market, from where farmers access prices and
    economic values
    
    Attributes
    ----------
    :
    
    
    """  
    pass


class Farmer(mesa.Agent):
    pass


class Farm(mesa.Agent): ## Can define an agents to have unique_id, but NO ADD TO THE
            ## SCHEDULER! 
    pass