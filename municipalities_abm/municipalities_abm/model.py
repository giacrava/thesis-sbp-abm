# -*- coding: utf-8 -*-


import pandas as pd
import geopandas as gpd
import numpy as np
import pathlib
import csv
import joblib

import mesa
import mesa.time
import mesa.datacollection
import mesa_geo

from . import agents
from .mapping_class import mappings
from .model_inputs import sbp_payments_path


# Functions for datacollector
# def get_percentage_adopted(model):
#     """
#     Method to calculate how many farmers have adopted SBP.
#     Called by the DataCollector.

#     Returns
#     -------
#     percentage_adopted : int
#         Percentage of farmers that have adopted SBP.

#     """
#     farmers_adopted = 0
#     for farmer in model.schedule.agents:
#         if farmer.farm.pasture_type.type == 'Sown Permanent Pasture':
#             farmers_adopted += 1
#     percentage_adopted = farmers_adopted / model._total_farmers * 100
#     return percentage_adopted


class SBPAdoption(mesa.Model):
    """
    Model for SBP adoption.

    Attributes #TO UPDATE
    ----------
    municipalities_data : pd dataframe


    """

    def __init__(self,
                 ml_features_path="./ml_model/rnd_for_TTFTTF2/features.csv",
                 ml_model_path="./ml_model/rnd_for_TTFTTF2/model.pkl",
                 initial_year=1996,
                 sbp_payments_path=sbp_payments_path,
                 seed=None):
        """
        Initalization of the model.

        Parameters
        ----------
        initial_year : int
            Year in the interval 1996 - 2018 in which the simulation has to
            start (the adoptions from this year will be predicted)
        sbp_payments : dict
            Path to the spreadsheed with the total payment in €/hectare 
            provided by the Portuguese Carbon Fund for each year
        ml_model : path str
            Path to the machine learning model already already fit to data, to 
            be used for prediction of SBP adoption
        ml_features : path str
            Path to a List of names of the features on which the ML model was 
            trained,in the same order as they were passed for training
        seed : int
            Seed for pseudonumber generation

        """

        super().__init__()

        self.schedule = mesa.time.SimultaneousActivation(self)
        self.grid = mesa_geo.GeoSpace()

        if (initial_year < 1996):
            raise ValueError("The model cannot be initialized in a year "
                             "previous to 1996")
        else:
            self._year = initial_year
        self._ml_model = joblib.load(ml_model_path)
        self._ml_features = self._retrieve_ml_features(ml_features_path)

        self.government = self._initialize_government(sbp_payments_path)

        self.perm_pastures_ha_port = None
        self.yearly_adoption_ha_port = None
        self.cumul_adoption_10y_ha_port = None
        self.adoption_pr_y_port = None
        self.cumul_adoption_10_y_pr_y_port = None
        self._initialize_municipalities_and_adoption()

        self._initialize_environments()

        # Attribute updated by the municipalities to calculate total adoption
        # in the year in Portugal
        self._adoption_in_year_port_ha = 0

        # self.datacollector = mesa.datacollection.DataCollector(
        #     agent_reporters={
        #         'FARM_ID': lambda a: a.code,
        #         'Pasture': lambda a: a.farm.pasture_type.type},
        #     model_reporters={
        #         'Percentage of adoption': get_percentage_adopted}
        #         )

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, new_val):
        self._year = new_val

    @property
    def adoption_in_year_port_ha(self):
        return self._adoption_in_year_port_ha

    @adoption_in_year_port_ha.setter
    def adoption_in_year_port_ha(self, new_val):
        self._adoption_in_year_port_ha = new_val

    @property
    def ml_model(self):
        return self._ml_model

    @property
    def ml_features(self):
        return self._ml_features

    def _initialize_government(self, sbp_payments_path):
        """
        Called by the __init__ method.

        Instantiate the Government class.

        """
        sbp_payments = pd.read_excel(sbp_payments_path, index_col='Year')
        government = agents.Government(self.next_id(), self, sbp_payments)
        return government

    def _initialize_municipalities_and_adoption(self):
        """
        Called by the __init__ method.

        - Loads the shapefile of the municipalities
        - Check that the file has no missing values
        - Instantiates the municipalities
        - Call method to load data that need to be set as attribute of
        municipalities and set them + to set model's attributes regarding
        pastures and adoption in Portugal
        - Creates the space grid with the municipalities
        - Adds each municipality to the schedule
        - Calls each municipality's method to retrieve its neighboring ones
        - Creates the municipalities mapping dictionary, necessary to
        replace in the farms dataset the strings with the relative objects.

        """

        municipalities_shp_path = (pathlib.Path(__file__).parent.parent
                                   / 'data' / 'municipalities_shp'
                                   / 'shapefile_for_munic_abm.shp')
        municipalities_data = gpd.read_file(municipalities_shp_path)
        municipalities_data.rename(columns={'Municipali': 'Municipality'},
                                   inplace=True)

        data_is_null = municipalities_data.isnull()
        if data_is_null.values.any():
            munic_with_nan = municipalities_data[
                                data_is_null.any(axis=1)].index.tolist()
            raise ValueError('The municipalities dataset is missing values for'
                             ' the following municipalities: ' +
                             ', '.join(munic_with_nan))     

        AC = mesa_geo.AgentCreator(agent_class=agents.Municipality,
                                   agent_kwargs={"model": self,})

        municipalities = AC.from_GeoDataFrame(gdf=municipalities_data,
                                              unique_id='CCA_2')

        self._set_munic_attributes_from_data_and_adoption_in_port(
            municipalities
            )

        self.grid.add_agents(municipalities)
        for munic in municipalities:
            self.schedule.add(munic)
            munic.get_neighbors_and_pastures_area()
            mappings.municipalities[munic.Municipality] = munic

    def _set_munic_attributes_from_data_and_adoption_in_port(
            self,
            municipalities
            ):
        """
        Called by the _initialize_municipalities method.

        Method to load and set the relative attributes of each Municipality 
        for census, adoption and permanent pastures area data.
        Adoption data are also restricted to the years before the intial year
        of the simulation, since the ones after are modelled.
        It also calls the method pf the Municipalities to calculate the
        cumulative adoption in the previous 10 years.
        While iterating over the municipalities it also calculates the 
        permanent pastures area and the yearly adoption in Portugal, setting
        the relative model variables. Then from these it calculates the 
        cumulative adoption in the previosu 10 years and divide these values
        for the permanent pastures area to get the ones used for the model.

        """
        census_data_path = (pathlib.Path(__file__).parent.parent
                            / 'data' / 'census_data_for_abm.csv')
        census_data = pd.read_csv(census_data_path, index_col='Municipality')

        adoption_data_path = (pathlib.Path(__file__).parent.parent
                              / 'data'
                              / '% yearly SBP adoption per municipality.csv')
        adoption_data = pd.read_csv(adoption_data_path,
                                    index_col='Municipality')
        adoption_data.columns = adoption_data.columns.astype(int)
        adoption_cols_to_drop = [col for col in adoption_data.columns
                                 if col >= self._year]
        adoption_data.drop(adoption_cols_to_drop, axis=1, inplace=True)

        pastures_data_path = (pathlib.Path(__file__).parent.parent
                              / 'data'
                              / 'municipalities_permanent_pastures_area.csv')
        pastures_data = pd.read_csv(pastures_data_path,
                                    index_col='Municipality')

        perm_pastures_ha_tot = 0
        yearly_adoption_ha_tot = pd.Series(0.,
                                           index=np.arange(1995, self._year))
        for munic in municipalities:
            munic_name = munic.Municipality
            try:
                munic_census_data = census_data.loc[munic_name]
            except KeyError:
                print("Census data for the municipality of",
                      munic_name, "are missing.")
            try:
                munic_pastures_data = pastures_data.loc[munic_name,
                                                        'pastures_area_munic']
            except KeyError:
                print("Pastures data for the municipality of",
                      munic_name, "are missing.")
            try:
                munic_adoption_data = adoption_data.loc[munic_name]
            except KeyError:
                print("Adoption data for the municipality of",
                      munic_name, "are missing.")

            munic.census_data = munic_census_data
            munic.perm_pastures_ha = munic_pastures_data
            munic.yearly_adoption = munic_adoption_data
            munic.set_cumul_adoption_10y(self._year)

            munic.yearly_adoption_ha = (
                munic.yearly_adoption * munic.perm_pastures_ha
                )
            munic.cumul_adoption_10y_ha = (
                munic.cumul_adoption_10y * munic.perm_pastures_ha
                )
            
            perm_pastures_ha_tot += munic.perm_pastures_ha
            yearly_adoption_ha_munic = (
                munic.yearly_adoption * munic.perm_pastures_ha
                )
            yearly_adoption_ha_tot += yearly_adoption_ha_munic

        self.perm_pastures_ha_port = perm_pastures_ha_tot
        self.yearly_adoption_ha_port = yearly_adoption_ha_tot
        self.cumul_adoption_10y_ha_port = (
            self.yearly_adoption_ha_port.loc[
                (self.year - 10) : self.year
                ].sum()
            )
        self.adoption_pr_y_port = (
            self.yearly_adoption_ha_port.loc[self.year - 1]
            / self.perm_pastures_ha_port
            )
        self.cumul_adoption_10_y_pr_y_port = (
            self.cumul_adoption_10y_ha_port
            / self.perm_pastures_ha_port)

    def _initialize_environments(self):
        """
        Called by the __init__ method.
        
        - Loads climate and soil data
        - Instatiate for each Municipality the relative MunicipalityEnvironment
          object and set it as an attribute of the Municipality

        """
        climate_data_path = (pathlib.Path(__file__).parent.parent
                             / 'data'
                             / 'municipalities_average_climate_final.csv')
        soil_data_path = (pathlib.Path(__file__).parent.parent
                          / 'data'
                          / 'municipalities_soil_final.csv')
        
        average_climate_data = pd.read_csv(climate_data_path,
                                           index_col=['Municipality'])
        soil_data = pd.read_csv(soil_data_path,
                                index_col=['Municipality'])

        for munic in self.schedule.agents:
            munic_name = munic.Municipality
            try:
                munic_average_climate = average_climate_data.loc[munic_name]
            except KeyError:
                print("Average climate data for the municipality of",
                      munic_name, "are missing.")
            try:
                munic_soil = soil_data.loc[munic_name]
            except KeyError:
                print("Soil data for the municipality of", munic_name,
                      "are missing.")

            environment = agents.MunicipalityEnvironment(
                munic_average_climate, munic_soil)
            munic.environment = environment

    def _retrieve_ml_features(self, path):
        with open(path) as inputfile:
            rd = csv.reader(inputfile)
            return list(rd)[0]

    # The following methods are not used during the initiation of the model

    def step(self):
        """
        Step method of the model.

        Calls the step methods of the agents added to the schedule.
        Calls the method to update adoptions attributes regarding Portugal.

        """
        self.schedule.step()
        # self.datacollector.collect(self)
        self._update_adoption_port()
        self.year += 1

    def _update_adoption_port(self):
        """
        Method called by the advance() method to update all the adoption
        attributes regarding Portugal.

        Returns
        -------
        None.

        """
        self.yearly_adoption_ha_port[self.year] = self.adoption_in_year_port_ha
        try:
            adopt_to_remove = self.yearly_adoption_ha_port[self.year - 10]
        except KeyError:
            adopt_to_remove = 0
        self.cumul_adoption_10y_ha_port = (self.cumul_adoption_10y_ha_port
                                           + self.adoption_in_year_port_ha
                                           - adopt_to_remove)
        self.adoption_pr_y_port = (
            self.adoption_in_year_port_ha / self.perm_pastures_ha_port
            )
        self.cumul_adoption_10_y_pr_y_port = (
            self.cumul_adoption_10y_ha_port / self.perm_pastures_ha_port
            )

        self.adoption_in_year_port_ha = 0
