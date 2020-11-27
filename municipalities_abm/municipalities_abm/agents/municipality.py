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
    census_data : dict
        Value for census variables of the municipality
    perm_pastures_ha : float
        Area of permanent pastures in hectare in the municipality
    yearly_adoption : dict
        Adoption of SBP in the municipality per year, divided by the permanent
        pastures area of the municipality
    cumul_adoption_10y : float
        Adoptoin of SBP in the municipality in the last 10 years, divided by
        the permanent pastures area od the municipality
    yearly_adoption_ha : dict
        Adoption of SBP in the municipality per year in hectares
    cumul_adoption_10y_ha : float
        Adoptoin of SBP in the municipality in the last 10 years in hectares  
    # environment : MunicipalityEnvironment object
    #     Entity reporting the environmental conditions of the municipality

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
        self.census_data_clsf = None
        self.census_data_regr = None
        self.perm_pastures_ha = None

        self.yearly_adoption = None
        self.cumul_adoption_10y = None
        self.yearly_adoption_ha = None
        self.cumul_adoption_10y_ha = None

        self.cumul_adoption_tot = None
        self.cumul_adoption_tot_ha = None  # # For visualization

        # Attibutes set during initialization of MunicipalityClimate objects
        # self.environment = None

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
        yearly_adoption_10y = [v for k, v in self.yearly_adoption.items()
                               if k >= (year - 10)]
        self.cumul_adoption_10y = sum(yearly_adoption_10y)

    def set_tot_cumul_adoption(self):
        """
        Called by the model during instantiation of Municipalities.

        Calculate the total adoption over all the previous years and
        set the cumul_adoption_tot attribute

        Returns
        -------
        None.

        """
        self.cumul_adoption_tot = sum(self.yearly_adoption.values())

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
        ml_clsf_input_data = self._retrieve_data(self.model.ml_clsf_feats,
                                                 self.model.year,
                                                 'clsf')
        ml_regr_input_data = self._retrieve_data(self.model.ml_regr_feats,
                                                 self.model.year,
                                                 'regr')
        self.predict_adoption(self.model.ml_clsf, ml_clsf_input_data,
                              self.model.ml_regr, ml_regr_input_data)

    def _retrieve_data(self, features, year, estimator):
        """
        Method to return all the data that need to be passed to the ML model
        to predict the adoption in the year.
        Estimator has to be "clsf" or "regr" and is required to retrieve the
        correct census features.

        Returns
        -------
        attributes : pd DataFrame
            Contains all the attributes required by the machine learning model
            to predict adoption.

        """
        attributes = pd.Series(index=features)

        # ADOPTION
        attributes["adoption_pr_y_munic"] = self.yearly_adoption[year - 1]
        attributes["adoption_pr_y_port"] = self.model.adoption_pr_y_port

        if "cumul_adoption_10_y_pr_y_munic" in features:
            attributes["cumul_adoption_10_y_pr_y_munic"] = (
                self.cumul_adoption_10y
                )
            adoption_pr_y_neigh, cumul_adoption_neigh = (
                self._get_neigh_adoption('10y')
                )
            attributes["adoption_pr_y_neighbours_adj"] = adoption_pr_y_neigh
            attributes["cumul_adoption_10_y_pr_y_neighbours_adj"] = (
                cumul_adoption_neigh
                )
            attributes["cumul_adoption_10_y_pr_y_port"] = (
                self.model.cumul_adoption_10y_port
                )
            if 'cumul_adoption_10_y_pr_y_munic_squared' in features:
                attributes['cumul_adoption_10_y_pr_y_munic_squared'] = (
                    self.cumul_adoption_10y
                    * self.cumul_adoption_10y
                    )
        elif "tot_cumul_adoption_pr_y_munic" in features:
            attributes["tot_cumul_adoption_pr_y_munic"] = (
                self.cumul_adoption_tot
                )
            adoption_pr_y_neigh, cumul_adoption_neigh = (
                self._get_neigh_adoption('tot')
                )
            attributes["adoption_pr_y_neighbours_adj"] = adoption_pr_y_neigh
            attributes["tot_cumul_adoption_pr_y_neighbours_adj"] = (
                cumul_adoption_neigh
                )
            attributes["tot_cumul_adoption_pr_y_port"] = (
                self.model.cumul_adoption_tot_port
                )
            if 'tot_cumul_adoption_pr_y_munic_squared' in features:
                attributes['tot_cumul_adoption_pr_y_munic_squared'] = (
                    self.cumul_adoption_tot
                    * self.cumul_adoption_tot
                    )

        if estimator == 'clsf':
            attributes.update(self.census_data_clsf)
        if estimator == 'regr':
            attributes.update(self.census_data_regr)
            attributes['sbp_payment'] = (
                self.model.government.retrieve_payments(year)
                )
        attributes['pastures_area_munic'] = self.perm_pastures_ha
        environment = mappings.environments[self.Municipality]
        attributes.update(environment.average_climate)
        # attributes.update(environment.yearly_climate.loc[year-1])
        attributes.update(environment.soil)

        if attributes.isnull().any():
            missing_attr = attributes[attributes.isnull()].index.tolist()
            raise ValueError("The following attributes to input to the machine"
                             " learning model are missing: "
                             + ", ".join(missing_attr))

        return attributes.to_frame().T

    def _get_neigh_adoption(self, tot_or_10y):
        """
        Calculate and return the adoption of the previous year and the
        cumulaive over 10 years in the neighbouring municipalities.

        """
        year = self.model.year
        munic_map = mappings.municipalities
        adoptions_ha = [munic_map[neigh].yearly_adoption_ha[year-1]
                        for neigh in self.neighbors]
        adoption_pr_y_ha = sum(adoptions_ha)
        adoption_pr_y = adoption_pr_y_ha / self.neighbors_perm_pastures_ha

        if tot_or_10y == '10y':
            adoptions_10y_ha = [munic_map[neigh].cumul_adoption_10y_ha
                                for neigh in self.neighbors]
            cumul_adoption_10y_ha = sum(adoptions_10y_ha)
            cumul_adoption = (
                cumul_adoption_10y_ha / self.neighbors_perm_pastures_ha
                )
        if tot_or_10y == 'tot':
            adoptions_tot_ha = [munic_map[neigh].cumul_adoption_tot_ha
                                for neigh in self.neighbors]
            cumul_adoption_tot_ha = sum(adoptions_tot_ha)
            cumul_adoption = (
                cumul_adoption_tot_ha / self.neighbors_perm_pastures_ha
                )
        return adoption_pr_y, cumul_adoption

    def predict_adoption(self, classifier, input_clsf, regressor, input_regr):
        prob_adopt = classifier.predict_proba(input_clsf)[0][1]
        if self.model.random.uniform(0, 1) < prob_adopt:
            adoption = regressor.predict(input_regr)
            if adoption < 0:
                print("Negative adoption predicted of:", str(adoption))
                self._adoption_in_year = 0
            else:
                self._adoption_in_year = adoption[0]
        else:
            self._adoption_in_year = 0

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
        self.cumul_adoption_tot += self._adoption_in_year
        self.cumul_adoption_10y_ha = (
            self.cumul_adoption_10y * self.perm_pastures_ha
            )
        self.cumul_adoption_tot_ha += self.yearly_adoption_ha[year]

        self.model.adoption_in_year_port_ha += self.yearly_adoption_ha[year]
