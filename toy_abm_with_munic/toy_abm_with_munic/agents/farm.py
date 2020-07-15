# -*- coding: utf-8 -*-
"""
Created on Thu May 28 14:52:56 2020

@author: giaco
"""


class Farm:
    """
    Class for farm objects.

    Farms:
        - are initialized by the farmer that owns them
        - have one and only one type of pasture

    Attributes
    ----------
    owner : Farmer object
        Farmer who owns the farm.
    code : str
        ID of the farm in the farms excel database
    pasture_type : Pasture object
        The pasture that the farm is adopting
    municipality : Municipality object
        Municipality where the farm is located

    Methods
    ----------
    pastures_adoption_evaluation
        Evaluate the adoption of all the adoptable pastures and, if at least
        one is considered economically viable, adopt the one with the highest
        differential NPV respect to the actual one.

    """
    def __init__(self, owner, unique_id, model_adoptable_pastures, farm_data):#,
                 #municipality):
        """
        Parameters
        ----------
        farm_data : pandas Series
            Contains the data of the farms, contained in the relative row of
            the farms excel database.

        """
        self.owner = owner
        self.unique_id = unique_id
        self.code = farm_data.name
        self.model_adoptable_pastures = model_adoptable_pastures

        # Data from database
        self.pasture_area = farm_data['PastureSurface']
        self.pasture_type = farm_data['Pasture']
        self.municipality = farm_data['Municipality']

        self.municipality.farms.append(self)
        if self.pasture_type.type == 'Sown Permanent Pasture':
            self.municipality.adoptedSBP += 1

    def pastures_adoption_evaluation(self):
        """
        Method called by the step method of the farmer who owns the farm to
        evaluate the adoption of the available types of pastures.

        Check if any different pasture can be adopted.
        In case:
            - Calculate NPV of keeping actual pasture
            - Calculate NPV of adoption of each adoptable pasture
            - Calculate differential NPV
            - If there are positive ones, choose the more advantageous relative
            pasture and adopt it

        """

        # print("farm", self.code, "step")

        farm_adoptable_pastures = [pasture for pasture
                                   in self.model_adoptable_pastures
                                   if pasture != self.pasture_type]

        if farm_adoptable_pastures:
            npvs_differential = self._get_differential_npvs(farm_adoptable_pastures)

            # print(npvs_differential)

            if any([npv > 0 for npv in npvs_differential]):
                max_diff_npv = max(npvs_differential)
                idx_max_diff_npv = npvs_differential.index(max_diff_npv)
                pasture_to_adopt = farm_adoptable_pastures[idx_max_diff_npv]
                self.pasture_type = pasture_to_adopt
                self.municipality.adoptedSBP += 1

    def _get_differential_npvs(self, farm_adoptable_pastures):
        """
        Calculates the NPV of keeping the actual pasture, the NPVs of adopting
        the adoptable pastures and for each of them the differential NPVs
        between adopting a keeping the actual pasture.

        Parameters
        ----------
        farm_adoptable_pastures : list of AdoptablePasture objects
            AdoptablePasture objects to calculate the differential NPV for.

        Returns
        -------
        npvs_differential : list of int
            Differential NPVs between adopting the adoptable pastures and
            keeping the actual one.

        """
        npv_keeping_actual = self.pasture_type.npv_keeping()
        npvs_adoption = []
        npvs_differential = []
        for pasture in farm_adoptable_pastures:
            npv_adoption = pasture.npv_adoption(self.pasture_area,
                                                self.owner.education)
            npvs_adoption.append(npv_adoption)
            npv_differential = npv_adoption - npv_keeping_actual
            npvs_differential.append(npv_differential)
        return npvs_differential
    