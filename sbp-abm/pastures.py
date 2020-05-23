# -*- coding: utf-8 -*-
"""
Created on Sat May 23 16:40:17 2020

@author: giaco
"""
import abc

class Pasture(abc.ABC):
    """
    Abstract class for general type of pasture
    
    Attributes
    ----------
    
    
    """   
    
    def __init__(self): #to implement in the next ones?
        pass
    
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
    

    def NPV_adoption(self):
        pass
    
    def NPV_keeping(self):
        pass
