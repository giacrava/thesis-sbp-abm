# -*- coding: utf-8 -*-

import abc

import mesa


class Market(mesa.Agent, abc.ABC):
    """
    Base class for the agents reporting economic data for NPV calculation for
    pastures.
    Should not be instantiated.

    Attributes
    ----------
    discount_rate : float
        Discount rate for economic calculations

    """

    @abc.abstractmethod
    def __init__(self, unique_id, model, discount_rate):

        super().__init__(unique_id, model)
        self.discount_rate = discount_rate
        self.pasture_type = ''


class NaturalPasturesMarket(Market):
    """
    Agent reporting the economic data regarding Natural Pastures

    Attributes
    ----------
    pasture_type : str
        The pasture type the data are reported for

    """

    def __init__(self, unique_id, model, discount_rate):
        """
        Parameters
        ----------
        discount_rate : float
            Discount rate for economic calculations

        """
        super().__init__(unique_id, model, discount_rate)
        self.pasture_type = 'Natural Pasture'


class SownPermanentPasturesMarket(Market):
    """
    Agent reporting the economic data regarding Sown Permanent Pastures

    Attributes
    ----------
    pasture_type : str
        The pasture type the data are reported for

    """

    def __init__(self, unique_id, model, discount_rate):
        """
        Parameters
        ----------
        discount_rate : float
            Discount rate for economic calculations

        """
        super().__init__(unique_id, model, discount_rate)
        self.pasture_type = 'Sown Permanent Pasture'
