# -*- coding: utf-8 -*-

import abc
import numpy as np


class Pasture:
    """
    Base class for pasture objects.

    Attributes
    ----------
    market : Market object
        Object representing the market, from which to retrieve all the
        economical data required for NPV calculations
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
                         'lacks the implementation of the method to calculate'
                         ' the NPV of keeping it.')


class NaturalPasture(Pasture):
    """
    Natural pasture class.

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
        """
        Calculates the NPV of keeping a natural pasture over 10 years.

        Returns
        -------
        npv : float
            NPV of keeping the actual pasture over 10 years

        """
        cash_flows = self.market.installation + self.market.maintenance
        npv = np.npv(self.market.discount_rate, cash_flows)
        return npv


class AdoptablePasture(Pasture, abc.ABC):
    """
    Abstract class for pastures that can be adopted.

    Enforces the implementation of a method to calculate the NPV of adoption.

    """
    @abc.abstractmethod
    def npv_adoption(self, farmer_education, current_pasture):
        pass


class SownPermanentPasture(AdoptablePasture):
    """
    Sown permanent pasture class.

    Attributes
    ----------
    government : SownPermanentPasturesGovernment object
        Agent responsible to report the payments for sown permanent pastures.
    market : SownPermanentPasturesMarket object
        Agent responsible to report the economic data for sown permanent
        pastures.

    Methods
    ----------
    npv_adoption
        Return the expected NPV to adopt the pasture.

    """

    def __init__(self, model):
        """
        Parameters
        ----------
        //

        """
        super().__init__(model)
        self.type = 'Sown Permanent Pasture'
        self.government = self.model.pasture_governments[self.type]
        self.market = self.model.markets[self.type]
        self._education_confidence = {'Primary': 0.4,
                                      'Secondary': 0.6,
                                      'Undergraduate': 0.8,
                                      'Graduate': 0.8}

    def npv_adoption(self, farmer_education, current_pasture):
        """
        Calculates the NPV of adopting the AdoptablePasture over 10 years.

        Returns
        -------
        npv : float
            NPV of adopting the AdoptablePasture over 10 years

        """

        # Calculate perceived costs
        confidence = self._education_confidence[farmer_education]
        expected_maintenance_sbp = [
            el * confidence for el in self.market.maintenance
            ]
        expected_maintenance_np = [
            el * (1 - confidence) for el in current_pasture.market.maintenance
            ]
        expected_maintenance = [
            c_sbp + c_np for c_sbp, c_np in zip(expected_maintenance_sbp,
                                                expected_maintenance_np)
            ]
        expected_costs = self.market.installation + expected_maintenance

        # Add payments to cash flows
        cash_flows = expected_costs
        for y in range(len(self.government.payments)):
            cash_flows[y] += self.government.payments[y]

        npv = np.npv(self.market.discount_rate, cash_flows)
        return npv
