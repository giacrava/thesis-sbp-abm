# -*- coding: utf-8 -*-

import pandas as pd
import geopandas as gpd
import pathlib

import mesa
import mesa.time
import mesa.datacollection
import mesa_geo

from . import agents
from .mapping_class import mappings
from .model_inputs import sbp_payments_path, initial_year


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
                 initial_year=initial_year,
                 sbp_payments_path=sbp_payments_path, 
                 seed=None):
        """
        Initalization of the model.

        Parameters
        ----------
        sbp_payments : dict

        seed : int
            Seed for pseudonumber generation

        """

        super().__init__()

        self.year = initial_year
        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa_geo.GeoSpace()

        self.government = self._initialize_governments(sbp_payments_path)

        # Municipalities instantiation
        self._initialize_municipalities()
        # self._farmers_data = []
        # self._load_farmers_data(farmers_data)

        # self.datacollector = mesa.datacollection.DataCollector(
        #     agent_reporters={
        #         'FARM_ID': lambda a: a.code,
        #         'Pasture': lambda a: a.farm.pasture_type.type},
        #     model_reporters={
        #         'Percentage of adoption': get_percentage_adopted}
        #         )

    # @property
    # def farmers_data(self):
    #     return self._farmers_data

    def _load_farmers_data(self, farmers_data):
        """
        Load the farmers excel database into a pandas dataframe and set the
        attribute self._farmers_data

        Check that the farmers_data excel file doesn't have multiple rows
        referring to the same farmer (i.e. with the same ID).
        In case it has, raises a ValueError exception.
        Also, drops any blank line from the excel file in case present.

        """
        farmers_dataframe = pd.read_excel(farmers_data, index_col=0)

        farmers_dataframe = farmers_dataframe.dropna(how='all')
        if farmers_dataframe.isnull().values.any():
            raise ValueError('The farmers excel database has some missing values'
                              '. Please fill in the right values or remove the '
                              'farmer and the relative farm from the database.')

        farmers_id = farmers_dataframe.index

        duplicated_farmers_id = farmers_id[farmers_id.duplicated()].unique()
        if not duplicated_farmers_id.empty:
            raise ValueError('The farmers dataset has multiple rows with the '
                             'following ID values: ' +
                             ', '.join(duplicated_farmers_id.values))
        self._farmers_data = farmers_dataframe

    def _load_farms_data(self, farms_data):
        """
        Convert the farms excel database into a pandas dataframe and check that
        it respect the requirements.

        Checks:
            Ignores, if present, blank lines from the excel file
            Check that the farms_data excel file:
                - Doesn't have multiple rows referring to the same farmer (i.e.
                  with the same ID).
                - Has exactly the same indexes (i.e.IDs) as the farmers_data
                  excel. Otherwise, raises a ValueError exception.

        """
        farms_dataframe = pd.read_excel(farms_data, index_col=0)

        farms_dataframe = farms_dataframe.dropna(how='all')
        if farms_dataframe.isnull().values.any():
            raise ValueError('The farms excel database has some missing values'
                             '. Please fill in the right values or remove the '
                             'farm and the relative farmer from the database.')

        farms_id = farms_dataframe.index
        duplicated_farms_id = farms_id[farms_id.duplicated()].unique()
        if not duplicated_farms_id.empty:
            raise ValueError('The farms dataset has multiple rows with the '
                             'following ID values: ' +
                             ', '.join(duplicated_farms_id.values))

        farmers_id = self._farmers_data.index
        id_in_farmers_and_not_in_farms = [id_ for id_ in farmers_id.values
                                          if id_ not in farms_id.values]
        id_in_farms_and_not_in_farmers = [id_ for id_ in farms_id.values
                                          if id_ not in farmers_id.values]
        if id_in_farmers_and_not_in_farms and id_in_farms_and_not_in_farmers:
            raise ValueError('Rows with the following ID values are in the'
                             ' farmers dataset but not in the farms one: '
                             + ', '.join(id_in_farmers_and_not_in_farms)
                             + '\n' + 'Rows with the following ID values '
                             'are in the farms dataset but not in the '
                             'farmers one: '
                             + ', '.join(id_in_farms_and_not_in_farmers))
        if id_in_farmers_and_not_in_farms:
            raise ValueError('Rows with the following ID values are in the'
                             ' farmers dataset but not in the farms one: '
                             + ', '.join(id_in_farmers_and_not_in_farms))
        if id_in_farms_and_not_in_farmers:
            raise ValueError('Rows with the following ID values are in the'
                             ' farms dataset but not in the farmers one: '
                             + ', '.join(id_in_farms_and_not_in_farmers))
        self._farms_data = farms_dataframe

    @staticmethod
    def _replace_strings_with_objects(dataframe, column, mapping):
        """
        Called by the __init__ method.

        Replace in the specified column of the dataframe each string with the
        relative object, as specified in the mapping dictionary.
        Check that the there are no more strings in the column specified, i.e.
        that all the strings corresponded to an object.

        Parameters
        ----------
        dataframe : pandas dataframe
            Dataframe to which the column belongs
        column : str
            Name of the column we want to replace the strings
        mapping : dict
            Map each string value to the relative object

        Raises
        ------
        ValueError
            Raised when in the column there are strings not linked to any
            object in the mapping dict.

        """
        strings = list(mapping.keys())
        objects = list(mapping.values())
        column_to_modify = dataframe[column]
        column_to_modify.replace(to_replace=strings,
                                 value=objects,
                                 inplace=True)

        wrong_strings = [entry for entry in column_to_modify
                         if isinstance(entry, str)]
        if wrong_strings:
            raise ValueError('The column ' + column + ' in the excel databases'
                             ' contains the following wrong entries: ' +
                             ", ".join(wrong_strings))

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

        Load the shapefile of the municipalities, instantiate the 
        municipalities, create the grid with them, add each to the schedule
        and make each retrieve the neighbouring municipalities.
        Also, creates the municipalities mapping dictionary, necessary to
        replace in the farms dataset the strings with the relative objects.

        """

        municipalities_shp_path = (pathlib.Path(__file__).parent.parent
                                   / 'data' / 'municipalities_shp'
                                   / 'concelhos_no_azores_and_madeira.shp')
        municipalities_data = gpd.read_file(municipalities_shp_path)
        municipalities_data.rename(columns={'Municipali': 'Municipality'},
                                   inplace=True)

        # useful_cols = ['CCA_2', 'NAME_2', 'NAME_1', 'geometry']
        # municipalities_col_sel = municipalities_data[useful_cols]
        # columns_renaming = {'NAME_1': 'District',
        #                     'NAME_2': 'Municipality'}
        # municipalities_col_sel.rename(columns=columns_renaming, inplace=True)

        AC = mesa_geo.AgentCreator(agent_class=agents.Municipality,
                                   agent_kwargs={"model": self})
        municipalities = AC.from_GeoDataFrame(gdf=municipalities_data,
                                              unique_id='CCA_2')

        self.grid.add_agents(municipalities)
        for munic in municipalities:
            self.schedule.add(munic)
            munic.get_neighbors()
            mappings.municipalities[munic.Municipality] = munic

    # The following methods are not used during the initiation of the model

    def step(self):
        """
        Step method of the model.

        Calls the step methods of the agents added to the schedule.

        """
        self.schedule.step()
        # self.datacollector.collect(self)
