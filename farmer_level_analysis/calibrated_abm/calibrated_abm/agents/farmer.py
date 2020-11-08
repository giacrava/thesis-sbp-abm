# -*- coding: utf-8 -*-

import mesa

from .farm import Farm


class Farmer(mesa.Agent):
    """
    Class for farmer agents.

    Farmers:
        - own a farm
        - have a step method that is directly called by the model's schedule at
          each model step

    Attributes
    ----------
    code : str
        ID of the farmer in the farmers excel database
    education : str
        Education level of the farmer. Used by the farms in NPV calculations
    farm : Farm object
        Farm that the farmer owns
    differential_npvs : list
        Reports the differential npvs calculated after the step (collected by
        the datacollector)

    Methods
    ----------
    step()
        Call the method of the farm owned to evaluate pastures adoption

    """

    def __init__(self, unique_id, model, farmer_data, cf_weights):
        """
        Initialize the farmer and the farms that it owns.
        Calculated the confidence factor of the farmer

        Parameters
        ----------
        farmer_data : pandas Series
            Contains the data of the farmers, contained in the relative row of
            the farmers excel database.

        """
        super().__init__(unique_id, model)
        self.code = farmer_data.name
        self.education = farmer_data['HighestEducationalDegree']
        self.farm = Farm(self,
                         self.model.next_id(),
                         self.model.adoptable_pastures,
                         self.model.farms_data.loc[self.code])
        self.confidence = self.calculate_cf(cf_weights)
        self.differential_npvs = None  # assigned by farms

    def calculate_cf(self, weights):
        scores = []
        scores.append(self.education * weights[0])
        scores.append(self.farm.pasture_surface * weights[1])
        scores.append(self.farm.legal_form * weights[2])
        scores.append(
            self.farm.percent_rented_land * weights[3]
            )
        return sum(scores)

    def step(self):
        """
        Step method called every model step by the scheduler.

        Calls the method of the farmers' farm for evaluation of pastures
        adoption.

        """
        self.farm.pastures_adoption_evaluation()
