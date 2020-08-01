# -*- coding: utf-8 -*-
"""
Created on Thu May 28 14:53:03 2020

@author: giaco
"""
import abc

import mesa


class Government(mesa.Agent, abc.ABC):
    """
    Base class for the agents reporting payments for ecosystem services from
    pastures.
    Should not be instantiated.

    """

    @abc.abstractmethod
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.pasture_type = ''

    def _retrieve_payments(self, payments):
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
        ------
        dict
            Payment relative to the pasture type the Government subclass deals
            with

        """
        try:
            return payments[self.pasture_type]
        except KeyError:
            raise KeyError('Payment for ' + self.pasture_type + ' not provided'
                           ', please include them in the "payments" dictionary'
                           '.'
                           )


class SownPermanentPasturesGovernment(Government):
    """
    Agent reporting the payments regarding Sown Permanent Pastures

    Attributes
    ----------
    pasture_type : str
        The pasture type it reports the payment for

    payment : dict
        Report the payment for adoption from 2009 to 2014

    """

    def __init__(self, unique_id, model, payments):
        """
        Initialize a SownPermanentPasturesGovernment object, retrieving the
        relative payment for ecosystem services.

        Parameters
        ----------
        payments : dict
            Maps each pasture type to the relative payment

        """
        super().__init__(unique_id, model)
        self.pasture_type = 'Sown Permanent Pasture'
        self.payments = self._retrieve_payments(payments)
