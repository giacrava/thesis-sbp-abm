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
from .model_inputs import farmers_data, farms_data, payments, discount_rate


# Functions for datacollector
def get_percentage_adopted(model):
    """
    Method to calculate how many farmers have adopted SBP.
    Called by the DataCollector.

    Returns
    -------
    percentage_adopted : int
        Percentage of farmers that have adopted SBP.

    """
    farmers_adopted = 0
    for farmer in model.schedule.agents:
        if farmer.farm.pasture_type.type == 'Sown Permanent Pasture':
            farmers_adopted += 1
    percentage_adopted = farmers_adopted / model._total_farmers * 100
    return percentage_adopted


class SBPAdoption(mesa.Model):
    """
    Model for SBP adoption.

    Attributes
    ----------
    farmers_data : pd dataframe
        Farmers data retrieved from excel file
    farmers_data : pd dataframe
        Farms data retrieved from excel file
    market : Market object
        Agent keeping the economic variables
    pasture_governments : dict
        Maps pastures to the relative agent responsible for reporting the
        payments for ecosystem services (if any)
    adoptable_pasture : list
        Pasture objects that each farmer considers for adoption (if not already
        adopted in the farm)
    total_farmers : int
        Number of farmers present in the model

    """

    def __init__(self, 
                 payments=payments, 
                 discount_rate=discount_rate, 
                 seed=None):
        """
        Initalization of the model.

        Parameters
        ----------
        farmers_data : str
            Path to the excel file with the farmers data. Cannot have
            multiple rows referring to the same farmer (i.e. with the same ID)
        farmers_data : str
            Path to the excel file with the farms data. There has to be at
            least one farm per each farmer and the ID columns have to match
        payments : dict
            Maps each pasture type to the realtive payment

        """

        super().__init__()

        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa_geo.GeoSpace()

        self._farmers_data = []
        self._load_farmers_data(farmers_data)

        self._farms_data = []
        self._load_farms_data(farms_data)

        self.pasture_governments = self._initialize_governments(payments)
        self.markets = self._initialize_markets(discount_rate)

        # Municipalities instantiation
        self._initialize_municipalities()

        # Pastures instantiation
        self._possible_pastures = []
        self._adoptable_pastures = []
        self._initialize_pastures()

        # Farmers and farms instantiation
        self._replace_strings_with_objects(self._farms_data,
                                           'Municipality',
                                           mappings.municipalities)
        self._replace_strings_with_objects(self._farms_data,
                                           'Pasture',
                                           mappings.pastures)
        self._total_farmers = 0
        self._initialize_farmers_and_farms(self._farmers_data)

        self.datacollector = mesa.datacollection.DataCollector(
            agent_reporters={
                'FARM_ID': lambda a: a.code,
                'Pasture': lambda a: a.farm.pasture_type.type},
            model_reporters={
                'Percentage of adoption': get_percentage_adopted}
                )

    @property
    def farmers_data(self):
        return self._farmers_data

    @property
    def farms_data(self):
        return self._farms_data

    @property
    def adoptable_pastures(self):
        return self._adoptable_pastures

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

    def _initialize_governments(self, payments):
        """
        Called by the __init__ method.

        Instantiate the Government subclasses and create the dictionary
        pasture_governments.

        """
        pasture_governments = {}
        for government_subclass in agents.Government.__subclasses__():
            obj = government_subclass(self.next_id(), self, payments)
            pasture_governments[obj.pasture_type] = obj
        return pasture_governments

    def _initialize_markets(self, discount_rate):
        """
        Called by the __init__ method.

        Instantiate the Market subclasses and returns the dictionary markets.

        """
        markets = {}
        for market_subclass in agents.Market.__subclasses__():
            obj = market_subclass(self.next_id(), self, discount_rate)
            markets[obj.pasture_type] = obj
        return markets

    def _initialize_municipalities(self):
        """
        Called by the __init__ method.

        Load the shapefile of the municipalities, select the data relative to
        the districts of interest, instantiate the municipalities, create the
        grid with them and make each retrieve the neighbors municipalities.
        Also, creates the municipalities mapping dictionary, necessary to
        replace in the farms dataset the strings with the relative objects.

        """

        municipalities_shp = (pathlib.Path(__file__).parent.parent / 'data'
                              / 'counties_shp' / 'concelhos.shp')
        municipalities_data = gpd.read_file(municipalities_shp)

        useful_cols = ['CCA_2', 'NAME_2', 'NAME_1', 'geometry']
        municipalities_col_sel = municipalities_data[useful_cols]
        columns_renaming = {'NAME_1': 'District',
                            'NAME_2': 'Municipality'}
        municipalities_col_sel.rename(columns=columns_renaming, inplace=True)

        districts_to_consider = ['Portalegre', 'Setúbal', 'Santarém', 'Évora',
                                 'Beja']
        municipalities_selected = municipalities_col_sel[
            municipalities_col_sel['District'].isin(districts_to_consider)
            ]

        AC = mesa_geo.AgentCreator(agent_class=agents.Municipality,
                                   agent_kwargs={"model": self})
        municipalities = AC.from_GeoDataFrame(gdf=municipalities_selected,
                                              unique_id='CCA_2')

        self.grid.add_agents(municipalities)
        for munic in municipalities:
            munic.get_neighbors()

        for munic in municipalities:
            mappings.municipalities[munic.Municipality] = munic

    def _initialize_pastures(self):
        """
        Called by the __init__ method.

        Creates the attributes:
            - possible_pastures, containing all the pastures that a farm can
            have
            - adoptable_pastures, containing all the pastures that a farmers
            can consider for adoption
            - mapping.pastures, used to replace in the excel data the pastures
            with the corresponging pasture object.

        """
        pastures_not_adoptable = [
            pasture for pasture in agents.Pasture.__subclasses__()
            if pasture != agents.AdoptablePasture
            ]
        pastures_adoptable = agents.AdoptablePasture.__subclasses__()
        possible_pastures = pastures_not_adoptable + pastures_adoptable

        for pasture_class in possible_pastures:
            pasture_object = pasture_class(self)
            self._possible_pastures.append(pasture_object)
            mappings.pastures[pasture_object.type] = pasture_object

        self._adoptable_pastures = [
            pasture for pasture in self._possible_pastures
            if isinstance(pasture, agents.AdoptablePasture)
            ]

    def _initialize_farmers_and_farms(self, farmers_data):
        """
        Called by the __init__ method.

        Initialize farmer objects from the database and add them to the
        scheduler.
        During its initialization, ach farmer initializes its farm.

        """
        for id_ in farmers_data.index:
            farmer = agents.Farmer(self.next_id(), self, farmers_data.loc[id_])
            self.schedule.add(farmer)
            self._total_farmers += 1

    # The following methods are not used during the initiation of the model

    def step(self):
        """
        Step method of the model.

        Calls the step methods of the agents added to the schedule.

        """
        self.schedule.step()
        self.datacollector.collect(self)



# farmers_data = "../data/FarmersData.xlsx"
# farms_data = "../data/FarmsData.xlsx"

# # Give payments in €/hectare, one entry for each year 
# ## WILL HAVE TO CONSIDER FOR HOW MANY YEARS
# sbp_payment = [50, 50, 50]

# payments = {'Sown Permanent Pasture': sbp_payment}


# model = SBPAdoption(farmers_data, farms_data, payments, seed=0)
# model.step()
# adoption_out = model.datacollector.get_agent_vars_dataframe()
# aggr_adoption_out = model.datacollector.get_model_vars_dataframe()
