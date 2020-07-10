# -*- coding: utf-8 -*-
"""
Created on Sat May 23 16:40:17 2020

@author: giaco
"""
import abc
import random


class Pasture:
    """
    Base class for pasture type.

    Attributes
    ----------
    market : Market object
        Object representing the market, from which to retrieve all the
        economical parameters required for NPV calculations
    """

    def __init__(self, model):
        """
        Parameters
        ----------
        //

        """
        self.model = model
        self.market = model.market
        self.pasture_type = ''

    def npv_keeping(self):
        raise ValueError('"' + self.pasture_type + '"' + ' Pasture subclass '
                         'lacks the implementation of the method to calculate '
                         'the NPV of keeping it.')


class NaturalPasture(Pasture):
    """
    Class to create a natural pasture.

    Attributes
    ----------
    pasture_type : str
        String characterizing the pasture, to associate from database

    Methods
    ----------
    NPV_keeping
        Returns the NPV of keeping the pasture.


    """

    def __init__(self, model):
        """
        Parameters
        ----------
        //

        """
        super().__init__(model)
        self.pasture_type = 'Natural Pasture'

    def npv_keeping(self):
        return random.randint(1, 5)


class AdoptablePasture(Pasture, abc.ABC):
    """
    Abstract class for pastures that can be adopted.

    Enforces the implementation of a method to calculate the NPV of adoption.

    """
    @abc.abstractmethod
    def npv_adoption(self):
        pass


class SownPermanentPasture(AdoptablePasture):
    """
    Class to create a sown permanent pasture.

    Attributes
    ----------
    government: SownPermanentPasturesGovernment object
        Agent responsible to report the payments for sown permanent pastures.

    Methods
    ----------
    NPV_adoption


    """

    def __init__(self, model):
        """


        """
        super().__init__(model)
        self.pasture_type = 'Sown Permanent Pasture'
        self.government = self.model.pasture_governments[self.pasture_type]

    def npv_adoption(self, pasture_area, farmer_education):
        # Calculate initial investment
        # Calculate yearly revenues (not including only PCF support)
        # Calculate yearly costs
        # Retrieve payments for adoption by PCF
        # Calculate NPV as Revenues + PCF_subs - costs
        return random.randint(2, 6)
