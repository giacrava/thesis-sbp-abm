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
    payments : dict
        Maps each pasture type to the relative payment
    
    pasture_governments : dict
        Maps subsidized pasture types to the relative agent responsible for 
        reporting the payments for ecosystem services
    
    possible_pastures : list
        Pastures that each farm can have
    
    adoptable_pasture : list
        Pastures that each farmer considers for adoption (if not already 
        adopted in the farm)
    
    """   
    def __init__(self, payments):
        """
        Initalization of the model.

        Parameters
        ----------
        payments : dict
            Maps each pasture type to the realtive payment
            
        """

        super().__init__()
        
        self.schedule = mesa.time.RandomActivation
        
        
        # Create agents

        self.__create_governments(payments)
        self.__create_pastures()        
        self.market = agents.Market(self.next_id(), self)

            # Create farmers and add them to the scheduler
            # Create farms and link them to the farmers and their pasture
            
    def __create_governments(self, payments):
        """
        Called by the __init__ method.
        Creates the attribute psature_governments.

        """     
        self.pasture_governments = {}
        for government_subclass in agents.Government.__subclasses__():
            obj = government_subclass(self.next_id(), self, payments)
            self.pasture_governments[obj.pasture_type] = obj
    
    def __create_pastures(self):
        """
        Called by the __init__ method.
        Creates the attributes possible_pastures and adoptable_pastures.

        """
              
        self.possible_pastures = []
        for pasture_type in pastures.Pasture.__subclasses__():
            self.possible_pastures.append(pasture_type(self))
        
        self.adoptable_pastures = [
            pasture for pasture in self.possible_pastures 
            if not isinstance(pasture, pastures.NaturalPasture)
            ]
        
        

        
        
    # def create_agents():
    #     """
        

    #     Returns
    #     -------
    #     None.

    #     """
    #     pass

        
        
    def step(self):
        """
        

        Returns
        -------
        None.

        """
        self.market.step()
        for government in self.pasture_governments.values():
            government.step()
        print("step!")
        #step of the government
        #schedule step
    
    


