# -*- coding: utf-8 -*-

import abc


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
        self.type = ''

    def npv_keeping(self):
        raise ValueError('"' + self.type + '"' + ' Pasture subclass '
                         'lacks the implementation of the method to calculate '
                         'the NPV of keeping it.')


class NaturalPasture(Pasture):
    """
    Class to create a natural pasture.

    Attributes
    ----------
    type : str
        String characterizing the pasture, to associate from database
    market : NaturalPasture object
        Agent responsible to report the economic data for natural pastures.
    
    Methods
    ----------
    npv_keeping
        Returns the NPV of keeping the pasture.


    """

    def __init__(self, model):
        """
        Parameters
        ----------
        //

        """
        super().__init__(model)
        self.type = 'Natural Pasture'
        self.market = self.model.markets[self.type]

    def npv_keeping(self):
        return self.model.random.randint(1, 5)


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
    market : SownPermanentPasturesMarket object
        Agent responsible to report the economic data for sown permanent
        pastures.

    Methods
    ----------
    npv_adoption


    """

    def __init__(self, model):
        """


        """
        super().__init__(model)
        self.type = 'Sown Permanent Pasture'
        self.government = self.model.pasture_governments[self.type]
        self.market = self.model.markets[self.type]

    def npv_adoption(self, pasture_area, farmer_education):
        # Calculate initial investment
        # Calculate yearly revenues (not including only PCF support)
        # Calculate yearly costs
        # Retrieve payments for adoption by PCF
        # Calculate NPV as Revenues + PCF_subs - costs
        return self.model.random.randint(2, 6)
