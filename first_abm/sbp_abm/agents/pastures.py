# -*- coding: utf-8 -*-
"""
Created on Sat May 23 16:40:17 2020

@author: giaco
"""
import abc

class Pasture(abc.ABC):
    """
    Base abstract class for pasture types.
    
    """   
    
    def __init__(self, model):
        self.model = model
    
    @abc.abstractmethod
    def npv_adoption(self):
        pass
    
    @abc.abstractmethod
    def npv_keeping(self): #maybe a better name?
        pass
    

class NaturalPasture(Pasture):
    
    def __init__(self, model):
        """
        

        """
        super().__init__(model)
        self.pasture_type = 'Natural Pasture'
    
    def npv_adoption(self): ## ACTUALLY NOT NEEEDED HERE NO?
        pass
    
    def npv_keeping(self):
        return 2

class SownPermanentPasture(Pasture):
    """
    Class to create sown permanent pastures.
    
    Attributes
    ----------
    government: SownPermanentPasturesGovernment object
        Agent responsible to report the payments for sown permanent pastures.
        
    Methods
    ----------  
    NPV_adoption : 
    
    NPV_keeping : passed 
    
    """  
    
    def __init__(self, model):
        """
        

        """
        super().__init__(model)
        #self.age
        self.pasture_type = 'Sown Permanent Pasture'
        self.government = self.model.pasture_governments[self.pasture_type]
    
    def step(self):
        
        # Increment the age of the farm
        # If age = 10, switch to natural
        pass
    
    def npv_adoption(self):
        # Calculate initial investment
        # Calculate yearly revenues (not including only PCF support)
        # Calculate yearly costs
        # Retrieve payments for adoption by PCF
        # Calculate NPV as Revenues + PCF_subs - costs 
        return 10

    def npv_keeping(self):
        pass
