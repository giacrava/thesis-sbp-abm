# -*- coding: utf-8 -*-
"""
Created on Thu May 21 09:45:34 2020

@author: giaco
"""



import mesa
import mesa.time

import agents
import pastures


class SBPAdoption(mesa.Model):
    """
    Model for SBP adoption.
    
    Attributes
    ----------
    subsidies : dict
        Maps each pasture type to the realtive subsidy
    
    pasture_governments : dict
        Maps subsidized pasture types to the relative agent responsible for 
        reporting the subsidies
    
    possible_pastures : list
        Pastures that each farm can have
    
    adoptable_pasture : list
        Pastures that each farmer considers for adoption (if not already 
        adopted in the farm)
    
    """   
    def __init__(self, subsidies):
        """
        Initalization of the model.

        Parameters
        ----------
        subsidies : dict
            Maps each pasture type to the realtive subsidy
            
        """

        super().__init__()
        self.subsidies = subsidies
        
        self.schedule = mesa.time.RandomActivation
        
        
        #MAYBE THE FOLLOWING CREATION SHOULD BE MOVED TO METHODS
        
        #Create dictionary of agents resposible for the subsidies
        self.pasture_governments = {}
        for government_subclass in agents.Government.__subclasses__():
            obj = government_subclass(self.next_id(), self, subsidies)
            self.pasture_governments[obj.pasture_type] = obj
        
        #Create lists of pastures (possible to have and adoptable)
        self.possible_pastures = []
        for pasture_type in pastures.Pasture.__subclasses__():
            self.possible_pastures.append(pasture_type(self))
        
        self.adoptable_pastures = [
            pasture for pasture in self.possible_pastures 
            if not isinstance(pasture, pastures.NaturalPasture)
            ]
        
        
        # Create agents
        # self.market = agents.Market(self.next_id(), self)

        
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
    
    


