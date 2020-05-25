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
    def NPV_adoption(self):
        pass
    
    @abc.abstractmethod
    def NPV_keeping(self): #maybe a better name?
        pass
    

class NaturalPasture(Pasture):
    
    def NPV_adoption(self):
        pass
    
    def NPV_keeping(self):
        pass


class SownPermanentPasture(Pasture):
    """
    Class to create sown permanent pastures.
    
    Attributes
    ----------
    government: SownPermanentPasturesGovernment object
        Agent responsible to report the subsidy for sown permanent pastures.
        
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
        self.government = self.model.pasture_governments[
        'Sown Permanent Pasture']
    
    def NPV_adoption(self):
        pass
    
    def NPV_keeping(self):
        pass
