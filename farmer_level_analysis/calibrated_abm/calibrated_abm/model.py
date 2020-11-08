# -*- coding: utf-8 -*-

import pandas as pd

import mesa
import mesa.time
import mesa.datacollection

from . import agents
from .model_inputs import (farmers_data, farms_data, payments, pastures_costs,
                           weights)



def get_percentage_adopted(model):
    """
    Method to calculate the percentage of farmers that adopted SBP.
    Called by the data collector.

    Returns
    -------
    percentage_adopted : int
        Percentage of farmers that have adopted SBP.

    """
    farmers_adopted = 0
    for farmer in model.schedule.agents:
        if farmer.farm.pasture_type.type == 'Sown Permanent Pasture':
            farmers_adopted += 1
    percentage_adopted = farmers_adopted / model.total_farmers * 100
    return percentage_adopted


class FLCalibratedABM(mesa.Model):
    """
    Model for SBP adoption using Animal Farm survey data and differential
    perceived NPV considering only education as proxy for uncertainty.

    Attributes
    ----------
    weights : tuple
        Weights to calculate the confidence factor, for the features
        in the following order:
        HighestEducationalDegree, PastureSurface, LegalForm, PercentRentedLand
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
                 cf_weights=weights,
                 payments=payments,
                 pastures_costs=pastures_costs,
                 discount_rate=0.05):
        """
        Initalization of the model.

        Parameters
        ----------
        weights : tuple
            Weights to calculate the confidence factor, for the features
            in the following order:
            HighestEducationalDegree, PastureSurface, LegalForm, PercentRentedLand
        payments : dict
            Maps each pasture type to the relative payment
        pastures_costs : dict
            Maps each pasture to its installation and maintenance yearly costs
        discount_rate : float
            Discount rate for economic calculations
        seed : int
            Seed for pseudonumber generation

        """

        super().__init__()

        self.schedule = mesa.time.RandomActivation(self)

        self._cf_weights = cf_weights

        self.pasture_governments = self._initialize_governments(payments)
        self.markets = self._initialize_markets(discount_rate, pastures_costs)

        # Pastures instantiation
        self._possible_pastures = []
        self._adoptable_pastures = []
        self._pastures_mapping = {}
        self._initialize_pastures()

        # Farmers and farms instantiation
        self._farmers_data = []
        self._load_and_transform_farmers_data(farmers_data)

        self._farms_data = []
        self._load_and_transform_farms_data(farms_data)

        self._replace_strings_with_objects(self._farms_data,
                                           'Pasture',
                                           self._pastures_mapping)
        self._total_farmers = 0
        self._initialize_farmers_and_farms(self._farmers_data, self.cf_weights)

        self.datacollector = mesa.datacollection.DataCollector(
            agent_reporters={
                'FARM_ID': lambda a: a.code,
                'Pasture': lambda a: a.farm.pasture_type.type,
                'Confidence factor': lambda a: a.confidence,
                'Differential ENPV SBP': lambda a: a.differential_npvs[0]},
            model_reporters={
                'Percentage of adoption': get_percentage_adopted}
                )

    @property
    def cf_weights(self):
        return self._cf_weights

    @property
    def farmers_data(self):
        return self._farmers_data

    @property
    def farms_data(self):
        return self._farms_data

    @property
    def adoptable_pastures(self):
        return self._adoptable_pastures

    @property
    def total_farmers(self):
        return self._total_farmers

    @total_farmers.setter
    def total_farmers(self, value):
        self._total_farmers = value

    @staticmethod
    def normalize_data(column):
        """
        Method to normalize a column of data.

        Parameters
        ----------
        column : pd Series
            The column of data to be normalized

        Returns
        -------
        norm_column : pd.Series
            The normalized column

        """
        data = column
        max_value = data.max()
        min_value = data.min()
        norm_column = (data - min_value) / (max_value - min_value)
        return norm_column

    def _load_and_transform_farmers_data(self, farmers_data):
        """
        Load the farmers excel database into a pandas dataframe, transform the
        features as needed for the calculation of the confidence factor and
        set the attribute self._farmers_data

        Check that the farmers_data excel file doesn't have multiple rows
        referring to the same farmer (i.e. with the same ID).
        In case it has, raises a ValueError exception.
        Also, drops any blank line from the excel file, in case present.

        Feature HighestEducationalDegree: encodes it ordially and then
        normalises it.

        """
        farmers_dataframe = pd.read_excel(farmers_data, index_col=0)

        farmers_dataframe = farmers_dataframe.dropna(how='all')
        if farmers_dataframe.isnull().values.any():
            raise ValueError('The farmers excel database has some missing '
                             'values. Please fill in the right values or '
                             'remove the farmer and the relative farm from the'
                             ' database.')

        farmers_id = farmers_dataframe.index

        duplicated_farmers_id = farmers_id[farmers_id.duplicated()].unique()
        if not duplicated_farmers_id.empty:
            raise ValueError('The farmers dataset has multiple rows with the '
                             'following ID values: ' +
                             ', '.join(duplicated_farmers_id.values))

        education_encoding = {'Primary': 1,
                              'Secondary': 2,
                              'Undergraduate': 3,
                              'Graduate': 4}
        farmers_dataframe['HighestEducationalDegree'].replace(
            education_encoding, inplace=True
            )
        farmers_dataframe['HighestEducationalDegree'] = self.normalize_data(
            farmers_dataframe['HighestEducationalDegree']
            )

        self._farmers_data = farmers_dataframe

    def _load_and_transform_farms_data(self, farms_data):
        """
        Load the farms excel database into a pandas dataframe, transform the
        features as needed for the calculation of the confidence factor and
        set the attribute self._farms_data

        Checks:
            Ignores, if present, blank lines from the excel file
            Check that the farms_data excel file:
                - Doesn't have multiple rows referring to the same farmer (i.e.
                  with the same ID).
                - Has exactly the same indexes (i.e.IDs) as the farmers_data
                  excel. Otherwise, raises a ValueError exception.

        Feature PastureSurface: normalizes it
        Feature LegalForm: encodes it as 1 if "Individual" or 0 if "Associated"
        Feature PercentRentedLand: not modified since already normalized
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

        farms_dataframe['PastureSurface'] = self.normalize_data(
            farms_dataframe['PastureSurface']
            )
        legal_form_encoding = {'Individual': 1, 'Associated': 0}
        farms_dataframe['LegalForm'].replace(legal_form_encoding, inplace=True)

        self._farms_data = farms_dataframe

    @staticmethod
    def _replace_strings_with_objects(dataframe, column, mapping):
        """
        Called by the __init__ method.

        Replace in the specified column of the dataframe each string with the
        relative object, as specified in the mapping dictionary.
        Check that the there are no more strings in the column specified.

        Parameters
        ----------
        dataframe : pandas dataframe
            Dataframe to which the column belongs.
        column : str
            Name of the column we want to replace the strings.
        mapping : dict
            Map each string value to the relative object.

        Raises
        ------
        ValueError
            Risen when in the column there are strings not linked to any
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

        Instantiate the Government subclasses and returns the dictionary
        pasture_governments.

        """
        pasture_governments = {}
        for government_subclass in agents.Government.__subclasses__():
            obj = government_subclass(self.next_id(), self, payments)
            pasture_governments[obj.pasture_type] = obj
        return pasture_governments

    def _initialize_markets(self, discount_rate, pastures_costs):
        """
        Called by the __init__ method.

        Instantiate the Market subclasses and returns the dictionary markets.

        """
        markets = {}
        for market_subclass in agents.Market.__subclasses__():
            obj = market_subclass(self.next_id(), self, discount_rate,
                                  pastures_costs)
            markets[obj.pasture_type] = obj
        return markets

    def _initialize_pastures(self):
        """
        Called by the __init__ method.

        Creates the attributes:
            - possible_pastures, containing all the pastures that a farm can
            have
            - adoptable_pastures, containing all the pastures that a farmers
            can consider for adoption
            - pastures_mapping, used to replace in the excel data the pastures
            with the corresponging pasture object.

        """
        pastures_not_adoptable = [
            pasture for pasture in agents.Pasture.__subclasses__()
            if pasture != agents.pastures.AdoptablePasture
            ]
        pastures_adoptable = agents.AdoptablePasture.__subclasses__()
        possible_pastures = pastures_not_adoptable + pastures_adoptable

        for pasture_class in possible_pastures:
            pasture_object = pasture_class(self)
            self._possible_pastures.append(pasture_object)
            self._pastures_mapping[pasture_object.type] = pasture_object

        self._adoptable_pastures = [
            pasture for pasture in self._possible_pastures
            if isinstance(pasture, agents.AdoptablePasture)
            ]

    def _initialize_farmers_and_farms(self, farmers_data, cf_weights):
        """
        Called by the __init__ method.

        Initialize farmer objects from the database and add them to the
        scheduler.
        During its initialization, ach farmer initializes its farm.

        """
        for id_ in farmers_data.index:
            farmer = agents.Farmer(self.next_id(), self,
                                   farmers_data.loc[id_], cf_weights)
            self.schedule.add(farmer)
            self.total_farmers += 1

    # Methods not used during the instatiation of the model

    def step(self):
        """
        Model's step method.

        Calls the step methods of the agents added to the schedule.

        """
        self.schedule.step()
        self.datacollector.collect(self)
