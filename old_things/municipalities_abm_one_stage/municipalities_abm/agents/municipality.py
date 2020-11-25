# -*- coding: utf-8 -*-

import pandas as pd

from mesa_geo.geoagent import GeoAgent

from ..mapping_class import mappings


class Municipality(GeoAgent):
    """
    Class for Municipality object.

    Municipalities:
        .....

    Attributes # TO UPDATE
    ----------    
    Municipality : str
        Name of the municipality
    District : str
        Name of the district which municipality is part of
    neighbors : list
        Names (strings) of the neighboring Municipality objects
    neighbors_perm_pastures_ha : float
        Sum of the permanent pastures area in the neighbouring municipalities
    census_data : pd.Series
        Value for census variables of the municipality
    perm_pastures_ha : float
        Area of permanent pastures in hectare in the municipality
    yearly_adoption : pd.Series
        Adoption of SBP in the municipality per year, divided by the permanent
        pastures area of the municipality
    cumul_adoption_10y : float
        Adoptoin of SBP in the municipality in the last 10 years, divided by
        the permanent pastures area od the municipality
    yearly_adoption_ha : pd.Series
        Adoption of SBP in the municipality per year in hectares
    cumul_adoption_10y_ha : float
        Adoptoin of SBP in the municipality in the last 10 years in hectares   
    environment : MunicipalityEnvironment object
        Entity reporting the environmental conditions of the municipality

    Methods
    ----------
    get_neighbors
        Retrieve the names of the neighboring Municipality objects

    """

    def __init__(self, unique_id, model, shape):
        """
        Initialize a Municipality agent.

        """
        super().__init__(unique_id, model, shape)

        # Attributes set by the Agent Creator from the Shapefile during the
        # initialization
        self.Municipality = ""
        self.District = ""

        # Attributes set during initialization of the municipalities
        self.neighbors = None
        self.neighbors_perm_pastures_ha = None
        self.census_data = None
        self.perm_pastures_ha = None

        self.yearly_adoption = None
        self.cumul_adoption_10y = None
        self.yearly_adoption_ha = None
        self.cumul_adoption_10y_ha = None

        # Attibutes set during initialization of MunicipalityClimate objects
        self.environment = None
        
        # Attributes used to save state before running advance method
        self._adoption_in_year = None

    def get_neighbors_and_pastures_area(self):
        """
        Called by the model during instantiation of Municipalities.

        Get touching neighbors (a list of their names, to avoid errors during
        the serialization in Json format for the visualization).
        Calcualte the total area of permanent pastures in these neighbouring
        municipalities.

        # To get them based on a certain distance, use
        # get_neighbors_within_distance grid's method instead.

        """
        neighbors = self.model.grid.get_neighbors(self)
        self.neighbors = [neighbor.Municipality for neighbor in neighbors]
        perm_pastures_ha_all_neighbors = [
            neigh.perm_pastures_ha for neigh in neighbors
            ]
        self.neighbors_perm_pastures_ha = sum(perm_pastures_ha_all_neighbors)

    def set_cumul_adoption_10y(self, year):
        """
        Called by the model during instantiation of Municipalities.

        Calculate the total adoption over the previou 10 years and
        set the cumul_adoption_10y attribute

        Returns
        -------
        None.

        """
        self.cumul_adoption_10y = self.yearly_adoption.loc[
            (year-10):year].sum()

    def step(self):
        """
        Step method called by the step of the model.

        It retrieves all the data and pass them in the right order to the ML
        model to predict the fraction of permanent pastures area in the
        municipality in which SBP is adopted in the year, storing it in a
        temporary attribute.

        Returns
        -------
        None.

        """
        ml_input_data = self._retrieve_data(self.model.ml_features,
                                            self.model.year)
        self.predict_adoption(self.model.ml_model, ml_input_data)
    
    def _retrieve_data(self, features, year):
        """
        Method to return all the data that need to be passed to the ML model
        to predict the adoption in the year.
        
        Returns
        -------
        attributes : pd DataFrame
            Contains all the attributes required by the machine learning model
            to predict adoption.

        """
        attributes = pd.Series(index=features)
        # ind_vars = []

        # ADOPTION
        # ind_vars.extend([self.yearly_adoption.at[year - 1],
        #                  self.cumul_adoption_10y])
        attributes["adoption_pr_y_munic"] = self.yearly_adoption.at[year - 1]
        attributes["cumul_adoption_10_y_pr_y_munic"] = self.cumul_adoption_10y
        adoption_pr_y_neigh, cumul_adoption_10y_neigh = (
            self._get_neigh_adoption()
            )
        attributes["adoption_pr_y_neighbours_adj"] = adoption_pr_y_neigh
        attributes["cumul_adoption_10_y_pr_y_neighbours_adj"] = (
            cumul_adoption_10y_neigh
            )
        attributes["adoption_pr_y_port"] = self.model.adoption_pr_y_port
        attributes["cumul_adoption_10_y_pr_y_port"] = (
            self.model.cumul_adoption_10_y_pr_y_port
            )  
        # ind_vars.extend([adoption_pr_y_neigh, cumul_adoption_10y_neigh])
        # ind_vars.extend([self.model.adoption_pr_y_port,
        #                  self.model.cumul_adoption_10_y_pr_y_port])

        attributes.update(self.census_data)
        attributes['pastures_area_munic'] = self.perm_pastures_ha
        attributes.update(self.environment.average_climate)
        attributes.update(self.environment.soil)
        attributes['sbp_payment'] = (
            self.model.government.retrieve_payments(year)
            )
        if attributes.isnull().any():
            missing_attr = attributes[attributes.isnull()].index.tolist()
            raise ValueError("The following attributes to input to the machine"
                             "learning model are missing: "
                             + ", ".join(missing_attr))
        
        # CENSUS DATA
        # census_data = self.census_data
        # census_to_exclude = ["individual_prod_autonomous", "agr_time_partial"]
        # census_data.drop(census_to_exclude, inplace=True)
        # census_values = list(census_data.values)
        # census_values.insert(-1, self.perm_pastures_ha)
        # ind_vars.extend(census_values)
        # ENVIRONMENTAL DATA
        # av_climate_data = self.environment.average_climate
        # climate_to_exclude = ["days_max_t_over_30_average_munic"]
        # climate_data.drop(climate_to_exclude, inplace=True)
        # climate_data = list(climate_data.values)
        # soil_data = list(self.environment.soil.values)
        # ind_vars.extend(climate_data + soil_data)
        # print("NEW")
        # print(len(ind_vars), len(attributes))
        # for name, attr in zip(attributes.index, ind_vars):
        #     print(name, attr)
        return attributes.to_frame().T

    def _get_neigh_adoption(self):
        """
        Calculate and return the adoption of the previous year and the
        cumulaive over 10 years in the neighbouring municipalities.

        """
        year = self.model.year
        munic_map = mappings.municipalities
        adoptions_ha = [munic_map[neigh].yearly_adoption_ha.at[year-1]
                        for neigh in self.neighbors]
        adoption_pr_y_ha = sum(adoptions_ha)
        adoption_pr_y = adoption_pr_y_ha / self.neighbors_perm_pastures_ha

        adoptions_10y_ha = [munic_map[neigh].cumul_adoption_10y_ha
                            for neigh in self.neighbors]
        cumul_adoption_10y_ha = sum(adoptions_10y_ha)
        cumul_adoption_10y = (
            cumul_adoption_10y_ha / self.neighbors_perm_pastures_ha
            )
        return adoption_pr_y, cumul_adoption_10y

    def predict_adoption(self, predictor, input_data):
        pred = predictor.predict(input_data)
        if pred < 0:
            raise ValueError("Negative adoption predicted")
        self._adoption_in_year = pred[0]
        
    def advance(self):
        """
        Advance method called by the step of the model after the step() methods
        of all municipalities are all called.

        Updates all the attributes regarding adoption considering the
        prediction for the year.

        Sum the hectares adopted to the total adoption in Portugal in the year.

        Returns
        -------
        None.

        """
        year = self.model.year

        self.yearly_adoption[year] = self._adoption_in_year
        self.yearly_adoption_ha[year] = (
            self._adoption_in_year * self.perm_pastures_ha
            )
        try:
            adopt_to_remove = self.yearly_adoption[year - 10]
        except KeyError:
            adopt_to_remove = 0
        self.cumul_adoption_10y = (self.cumul_adoption_10y
                                   + self._adoption_in_year
                                   - adopt_to_remove)
        self.cumul_adoption_10y_ha = (
            self.cumul_adoption_10y * self.perm_pastures_ha
            )

        self.model.adoption_in_year_port_ha += self.yearly_adoption_ha[year]
