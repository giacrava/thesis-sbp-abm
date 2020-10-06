# -*- coding: utf-8 -*-

import pandas as pd
import geopandas as gpd
import pathlib

import mesa
import mesa.time
import mesa.datacollection
import mesa_geo

from . import agents
# from .mapping_class import mappings
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

    Attributes
    ----------
    municipalities_data : pd dataframe


    """

    def __init__(self,
                 initial_year=1996,
                 sbp_payments_path=sbp_payments_path, 
                 seed=None):
        """
        Initalization of the model.

        Parameters
        ----------
        initial_year : int
            Year in the interval 1996 - 2018 in which the simulation has to
            start
        sbp_payments : dict
            Path to the spreadsheed with the total payment in €/hectare 
            provided by the Portuguese Carbon Fund for each year.
        seed : int
            Seed for pseudonumber generation

        """

        super().__init__()

        self._year = initial_year
        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa_geo.GeoSpace()

        self.government = self._initialize_governments(sbp_payments_path)

        self._initialize_municipalities()
        
        self._initialize_climates()

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

    def _initialize_governments(self, sbp_payments_path):
        """
        Called by the __init__ method.

        Instantiate the Government class.

        """
        sbp_payments = pd.read_excel(sbp_payments_path, index_col='Year')
        government = agents.Government(self.next_id(), self, sbp_payments)
        return government

    def _initialize_municipalities(self):
        """
        Called by the __init__ method.

        - Loads the shapefile of the municipalities
        - Check that the file has no missing values
        - Instantiates the municipalities
        - Creates the space grid with the municipalities
        - Adds each municipality to the schedule
        - Calls each municipality's method to retrieve its neighboring ones
        # - Creates the municipalities mapping dictionary, necessary to
        # replace in the farms dataset the strings with the relative objects.

        """

        municipalities_shp_path = (pathlib.Path(__file__).parent.parent
                                   / 'data' / 'municipalities_shp'
                                   / 'concelhos_no_azores_and_madeira.shp')
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
                                   agent_kwargs={"model": self})
        municipalities = AC.from_GeoDataFrame(gdf=municipalities_data,
                                              unique_id='CCA_2')

        self.grid.add_agents(municipalities)
        for munic in municipalities:
            self.schedule.add(munic)
            munic.get_neighbors()
            # mappings.municipalities[munic.Municipality] = munic

    def _initialize_climates(self):
        """
        Called by the __init__ method.
        
        - Loads the climate data
        - Instatiate for each Municipality the relative MunicipalityClimate
          object and set it as an attribute of the Municipality

        Returns
        -------
        None.

        """
        climate_data_path = (pathlib.Path(__file__).parent.parent
                                   / 'data'
                                   / 'municipalities_climate_final.csv')
        climate_data = pd.read_csv(climate_data_path,
                                   index_col=['Municipality', 'Year'])

        for munic in self.schedule.agents:
            munic_name = munic.Municipality
            try:
                climate = agents.MunicipalityClimate(
                    climate_data.loc[munic_name])
            except KeyError:
                print("Climate data for the municipality of", munic_name,
                      "are missing.")
            munic.climate = climate

    # The following methods are not used during the initiation of the model

    def step(self):
        """
        Step method of the model.

        Calls the step methods of the agents added to the schedule.

        """
        self.schedule.step()
        # self.datacollector.collect(self)
