# -*- coding: utf-8 -*-
"""
Created on Thu May 21 09:45:34 2020

@author: giaco
"""

import pandas as pd

import mesa
import mesa.time

import agents
import pastures


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
        Maps subsidized pasture types to the relative agent responsible for 
        reporting the payments for ecosystem services
    
    possible_pastures : list
        Pastures that each farm can have
    
    adoptable_pasture : list
        Pastures that each farmer considers for adoption (if not already 
        adopted in the farm)
    
    """   
    def __init__(self, farmers_data, farms_data, payments):
        """
        Initalization of the model.

        Parameters
        ----------
        farmers_data : str
            Path to the excel file with the farmers data. Cannot have
            multiple rows referring to the same farmer (i.e. with the same ID).
        
        farmers_data : str
            Path to the excel file with the farms data. There has to be at
            least one farm per each farmer and the ID columns have to match.
        
        payments : dict
            Maps each pasture type to the realtive payment
            
        """

        super().__init__()
        
        self.farmers_data = farmers_data
        self.farms_data = farms_data
        self.market = None     ## DEFINE ALL AND THEN REDIFINE AFTER IN AGENT CREATION?
        self.pasture_governments = {}
        self.possible_pastures = []
        self.adoptable_pastures = [] 
        
        self.schedule = mesa.time.RandomActivation(self)
        
        # Create agents and objects
        self.market = agents.Market(self.next_id(), self)
        self.__create_governments(payments)
        self.__create_pastures()     
        self.__create_farmers_and_farms(self.farmers_data, self.farms_data)
        
        
        
    @property
    def farmers_data(self):
        return self._farmers_data
    
    @farmers_data.setter
    def farmers_data(self, farmers_data):
        """
        Check that the farmers_data excel file doesn't have multiple rows
        referring to the same farmer (i.e. with the same ID).
        In case it has, raises a ValueError exception.
        Also, drops any blank line fro the excel file in case present.

        """
        farmers_dataframe = pd.read_excel(farmers_data, index_col = 0)
        # farmers_dataframe = farmers_dataframe.dropna(how='all') ## TO REINTRODUCE WHEN
        ## FARMERS WILL HAVE AN ATTRIBUTE, OTERWISE CONSIDERS ALL LINES AS EMPTY AND DROPS
        ## EVERYTHING
        farmers_id = farmers_dataframe.index
        
        duplicated_farmers_id = farmers_id[farmers_id.duplicated()].unique()
        if not duplicated_farmers_id.empty:
            
            ## IS VALUE ERROR THE RIGHT ERROR? Also for the farms_data setter
            raise ValueError('The farmers dataset has multiple rows with the ' 
                             'following ID values: ' + 
                             ', '.join(duplicated_farmers_id.values))                                
        else:    
            self._farmers_data = farmers_dataframe

    @property
    def farms_data(self):
        return self._farms_data
    
    @farms_data.setter
    def farms_data(self, farms_data):
        """
        Convert the farms excel database into a pandas dataframe, check that
        it respect the requirements and substitutes the pasture and
        municipalities columns strings with the respective objects.
        
        Checks:
            Ignores, if present, blank lines from the excel file.
            Check that the farms_data excel file:
                - Doesn't have multiple rows referring to the same farmer (i.e. 
                  with the same ID).
                - Has exactly the same indexes (i.e.IDs) as the farmers_data 
                  excel. Otherwise, raises a ValueError exception.
            Check if all the pasture types and the municipalities are correctly
            spelled.
        
        """        
        farms_dataframe = pd.read_excel(farms_data, index_col = 0)
        farms_dataframe = farms_dataframe.dropna(how='all')
        farms_id = farms_dataframe.index
        
        duplicated_farms_id = farms_id[farms_id.duplicated()].unique()
        if not duplicated_farms_id.empty:
            raise ValueError('The farms dataset has multiple rows with the ' 
                             'following ID values: ' + 
                             ', '.join(duplicated_farms_id.values))
        
        farmers_id = self.farmers_data.index
        ID_in_farmers_and_not_in_farms = [ID for ID in farmers_id.values 
                                          if ID not in farms_id.values]
        ID_in_farms_and_not_in_farmers = [ID for ID in farms_id.values
                                          if ID not in farmers_id.values]
        if ID_in_farmers_and_not_in_farms and ID_in_farms_and_not_in_farmers:
            raise ValueError('Rows with the following ID values are in the'
                                 ' farmers dataset but not in the farms one: ' 
                                 + ', '.join(ID_in_farmers_and_not_in_farms) 
                                 + '\n' + 'Rows with the following ID values ' 
                                 'are in the farms dataset but not in the '
                                 'farmers one: ' 
                                 + ', '.join(ID_in_farms_and_not_in_farmers))
        elif ID_in_farmers_and_not_in_farms:
            raise ValueError('Rows with the following ID values are in the'
                             ' farmers dataset but not in the farms one: ' 
                             + ', '.join(ID_in_farmers_and_not_in_farms))
        elif ID_in_farms_and_not_in_farmers:
            raise ValueError('Rows with the following ID values are in the'
                             ' farms dataset but not in the farmers one: ' 
                             + ', '.join(ID_in_farms_and_not_in_farmers))
        else:
            self._farms_data = farms_dataframe
                
    # def switch_strings_with_objects(self, mapping, series):
    #     """
    #     Called by the ...
    #     Replace in the given series the strings with the relative object 
    #     through a dictionary mapping them.

    #     Parameters
    #     ----------
    #     mapping : dict
    #         Maps each string to the object that we want to replace it with
    #     series : pandas series
    #         Series in which the replacement has to take place

    #     Returns
    #     -------
    #     pandas series
    #         A series with the objects instead of the strings

    #     """
    ## I COULD USE THE REPLACE METHOD INSIDE THIS FUNCTION, AND AT THE SAME TIME
    ## CHECK THAT AT THE END THERE NOT ANYMORE STRINGS AND IN CASE PRINT THEM 
    ## RAISING AN EXCEPTION. otherwise, call the replace in the main function 
    ## and just implement a method for checking
    #     series_copy = series[:]
    #     for index in range(len(series_copy)):
    #         series_copy.iloc[index] = mapping[series_copy.iloc[index]]
    #     return series_copy
                                              
            
    def __create_governments(self, payments):
        """
        Called by the __init__ method.
        Creates the attribute psature_governments.

        """     
        for government_subclass in agents.Government.__subclasses__():
            obj = government_subclass(self.next_id(), self, payments)
            self.pasture_governments[obj.pasture_type] = obj
    
    def __create_pastures(self):
        """
        Called by the __init__ method.
        Creates the attributes possible_pastures and adoptable_pastures.

        """              
        for pasture_type in pastures.Pasture.__subclasses__():
            self.possible_pastures.append(pasture_type(self))
        
        self.adoptable_pastures = [
            pasture for pasture in self.possible_pastures 
            if not isinstance(pasture, pastures.NaturalPasture)
            ]
        
    def __create_farmers_and_farms(self, farmers_data, farms_data):
        """
        Called by the __init__ method.           
        Creates farmers and add them to the scheduler.
        Creates farms.
        Links farms and farmers.

        """
        for id_ in farmers_data.index:
            farmer = agents.Farmer(self.next_id(), self, farmers_data.loc[id_])
            self.schedule.add(farmer)
            farm = agents.Farm(self.next_id(), self, farms_data.loc[id_])
            farmer.farm = farm
            farm.owner = farmer
        
    def step(self):
        """
        

        Returns
        -------
        None.

        """
        self.market.step()
        for government in self.pasture_governments.values():
            government.step()
        print("step!")
        #step of the government
        #schedule step
    
    


