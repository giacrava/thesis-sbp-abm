# -*- coding: utf-8 -*-

import abc

import mesa


class Market(mesa.Agent, abc.ABC):
    """
    Base class for the agents reporting economic data for NPV calculation for
    pastures.
    Should not be instantiated.

    """

    @abc.abstractmethod
    def __init__(self, unique_id, model, discount_rate, pastures_costs):

        super().__init__(unique_id, model)
        self.discount_rate = discount_rate
        pasture_costs = pastures_costs[self.pasture_type]
        self.installation = pasture_costs['installation']
        self.maintenance = pasture_costs['maintenance']



class NaturalPasturesMarket(Market):
    """
    Agent reporting the economic data regarding Natural Pastures

    Attributes
    ----------
    pasture_type : str
        The pasture type the data are reported for
    installation : float
        Cash flow for the installation (year 0)
    maintenance : float
        Cash flows for the years 1-9

    """

    def __init__(self, unique_id, model, discount_rate, pastures_costs):
        """
        Parameters
        ----------
        discount_rate : float
            Discount rate for economic calculations
        pastures_costs : dict
            Mapping of each pasture type to its maintenance and instlallation
            yearly costs

        """
        self.pasture_type = 'Natural Pasture'
        super().__init__(unique_id, model, discount_rate, pastures_costs)


class SownPermanentPasturesMarket(Market):
    """
    Agent reporting the economic data regarding Sown Permanent Pastures

    Attributes
    ----------
    pasture_type : str
        The pasture type the data are reported for
    installation : float
        Cash flow for the installation (year 0)
    maintenance : float
        Cash flows for the years 1-9

    """

    def __init__(self, unique_id, model, discount_rate, pastures_costs):
        """
        Parameters
        ----------
        discount_rate : float
            Discount rate for economic calculations
        pastures_costs : dict
            Mapping of each pasture type to its maintenance and instlallation
            yearly costs

        """
        self.pasture_type = 'Sown Permanent Pasture'
        super().__init__(unique_id, model, discount_rate, pastures_costs)
