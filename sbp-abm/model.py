# -*- coding: utf-8 -*-
"""
Created on Thu May 21 09:45:34 2020

@author: giaco
"""

import inspect

import mesa
import mesa.time

import agents
import pastures


class SBPAdoption(mesa.Model):
    """
    Model for SBP adoption.
    
    Attributes
    ----------
    possible_pastures: list of instances
        List of the pastures that each farm can have
    
    adoptable_pasture: list of instances
        List of the pastures that each farmer consider to adopt (if not
        already adopted in the farm)
    
    """   
    def __init__(self):
        """
        

        Parameters
        ----------
        sbp_subsidy : dictionary
            Subsidies given to farmers for adoption of SBP in €/ha for each 
            year 


        """

        super().__init__()
        
        self.schedule = mesa.time.RandomActivation
        
        
        #Create lists of pastures (possible to have and adoptable)
        self.possible_pastures = []
        for __,obj in inspect.getmembers(pastures):
            if inspect.isclass(obj) and obj != pastures.Pasture:
                self.possible_pastures.append(obj()) 
        
        self.adoptable_pastures = [
            pasture for pasture in self.possible_pastures 
            if not isinstance(pasture, pastures.NaturalPasture)
            ]
        
        
        # Create agents
        self.market = agents.Market(self.next_id(),self)
        self.government = agents.Government(self.next_id(), self)
        
            # Create farmers and add them to the scheduler
            # Create farms and link them to the farmers and their pasture
        
        
        
        def create_agents():
            """
            

            Returns
            -------
            None.

            """
            pass

        
        
    def step(self):
        """
        

        Returns
        -------
        None.

        """
        #step of the market
        #step of the government
        #schedule step
    
    


