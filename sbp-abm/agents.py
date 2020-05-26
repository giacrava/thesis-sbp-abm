# -*- coding: utf-8 -*-
"""
Created on Thu May 21 09:45:52 2020

@author: giaco
"""
import mesa


class Government(mesa.Agent): #IS IT ABSTRACT?
    """
    Base class for the agents reporting payments for ecosystem services from 
    pastures.
    Should not be instantiated.
        
    """   
    
    def __init__(self, unique_id, model):
        # super().__init__(unique_id, model)
        pass
        
    def retrieve_subsidy(self, payments):
        """
        Called by the Government sub-classes' __init__ method.
        Extract the payments for the relative pasture type. If not available, 
        raise an exception.

        Raises
        ------
        KeyError
            Raised if the "payments" dictionary does not have a key 
            corresponding to the Pasture instance's attribute pasture_type

        Returns
        -------
        None.

        """
        try:
            self.payment = payments[self.pasture_type]
        except KeyError:
            raise KeyError('Payment for '+ self.pasture_type +' not provided.'
                           'Please include them in the "payments" dictionary.'
                           )
            
    def step(self):
        pass
       
class SownPermanentPasturesGovernment(Government):
    """
    Agent reporting the payments regarding Sown Permanent Pastures
    
    Attributes
    ----------
    payment : dict
        Report the payment for adoption from 2009 to 2014
        
    """       
    def __init__(self, unique_id, model, subsidies):
        """
        Initialize a SownPermanentPasturesGovernment object, retrieving the 
        relative payment for ecosystem services.

        Parameters
        ----------
        subsidies : dict
            Maps each pasture type to the relative payment

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
    
    def step(self):
        pass


class Municipality(mesa.Agent): ## Can define an agents to have unique_id, but NO ADD TO THE
            ## SCHEDULER! 
    """
    Agent representing the market, from where farmers access prices and
    economic values
    
    Attributes
    ----------
    
    
    
    """   
    pass


class Farmer(mesa.Agent):
    """
    Class for the farmer agents.
    
    Farmers:
        - own a farm
        - their step method is directly called by the model's schedule at each
          model step
    
    Attributes
    ----------
    code : str
        ID of the farmer in the farmers excel database    
    
    
    """  
    def __init__(self, unique_id, model, farmer_data):
        super().__init__(unique_id, model)
        self.code = farmer_data.name
        self.farm = None
        
    def step(self):
        pass

class Farm(mesa.Agent): ## Can define an agents to have unique_id, but NO ADD TO THE
            ## SCHEDULER!
    """
    Class for the farm objects.
    
    Farms:
        - are owned by a farmer
        - have one and only one type of pasture
        - are in a municipality
    
    Attributes
    ----------
    code : str
        ID of the farm in the farms excel database
    
    municipality :
        
    pasture_type : 
    
    
    """  
    def __init__(self, unique_id, model, farm_data):
        """
        

        Parameters
        ----------
        farm_data : pandas series
            Series 

        """
        super().__init__(unique_id, model)
        self.code = farm_data.name
        self.municipality = farm_data['Municipality'] ## HERE CAN BE IMPLEMENTED CONTROL MUNICIPALITY IN THE LIST / OR WE CAN HAVE ALREADY THE DATAFRAME POINTING AT THE OBJECTS
        # self.pasture_area = ## DEPEND HOW WE CONSIDER AREAS
        # self.pasture_type = ## SAME FOR PASTURES
        self.owner = None
        
 
        