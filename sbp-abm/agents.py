# -*- coding: utf-8 -*-
"""
Created on Thu May 21 09:45:52 2020

@author: giaco
"""
import mesa


class Government(mesa.Agent): #THIS CANNOT BE INSTANTIATED, SO SHOULD BE AN ABASTRACT CLASS
    """
    Base class for the agents reporting the subsidies available for subsidized
    pastures
    
    Methods
    ----------  
    retrieve_subsidy : extract the subsidy for the relative pasture type.
        

    """   
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        
    def retrieve_subsidy(self, subsidies):
        """
        Extract the subsidy for the relative pasture type.
        If not available, raise an exception.

        Raises
        ------
        KeyError
            Raised if the subsidy dictionary does not have a key corresponding 
            to the Pasture instance's attribute pasture_type

        Returns
        -------
        None.

        """
        try:
            self.subsidy = subsidies[self.pasture_type]
        except KeyError:
            raise KeyError('Subsidy for '+ self.pasture_type +' not provided.'
                           'Please include them in the "subsidies" dictionary.'
                           )
        
       
class SownPermanentPasturesGovernment(Government):
    """
    Agent reporting the subsidies regarding Sown Permanent Pastures
    
    Attributes
    ----------
    subsidy : dict
        Report the subsidy for adoption from 2009 to 2014
        
    """       
    def __init__(self, unique_id, model, subsidies):
        """
        Initialize a SownPermanentPasturesGovernment object, retrieving the 
        relative subsidy policy.

        Parameters
        ----------
        subsidies : dict
            Maps each pasture type to the realtive subsidy

        """
        super().__init__(unique_id, model)
        self.pasture_type = 'Sown Permanent Pasture'
        self.retrieve_subsidy(subsidies)
        

class Market(mesa.Agent):
    """
    Agent representing the market, from where farmers access prices and
    economic values
    
    Attributes
    ----------

    
    
    """  
    pass


class Farmer(mesa.Agent):
    pass


class Farm(mesa.Agent): ## Can define an agents to have unique_id, but NO ADD TO THE
            ## SCHEDULER! 
    pass