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
        Maps pastures to the relative agent responsible for reporting the 
        payments for ecosystem services (if any)   
    possible_pastures : list
        Pasture objects that each farm can have    
    adoptable_pasture : list
        Pasture objects that each farmer considers for adoption (if not already 
        adopted in the farm)       
    pastures_mapping : dict
        Maps each string in the "Pasture" column of the farms excel 
        database to the relative Pasture object.
    
    """   
    def __init__(self, farmers_data, farms_data, payments):
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
        
        self.farmers_data = farmers_data ## CH: io mi aspetto una stringa,
         ## invece mi arrivano i dati caricati tramite il setter --> porcatissima
        self.farms_data = farms_data
        ## CH come risolvere
        #self.farmers_data = []
        #self.__load_farmers_data(farmers_data)
        # e sotto sostituire @portoperty e @ setter e sostituire il setter con quuesto nome --> setter servono all'esterno in generale non all'interno
        
        self.pasture_governments = self.__create_governments(payments)
        self.market = agents.Market(self.next_id(), self)
        
        # Pastures instantiation
        self.possible_pastures = []
        self.adoptable_pastures = [] 
        self.pastures_mapping = {}
        self.__create_pastures()
        
        ## CH: all these should be private with a getter and setter! 
        ## adoptable pastures are acessible --> getter pubblico e setter non c'è (vedi screenshot in OOP)
        
        ## MUNICIPALITIES
        ## Create municipalities and also list of municipalities string (to give
        ## to the replace_string_with_objects function after merging in a dict)
        
        self.schedule = mesa.time.RandomActivation(self)
    
        # Farmers and farms instantiation
        self.__replace_strings_with_objects(self.farms_data,                                                             
                                           'Pasture',
                                           self.pastures_mapping)
        
        ## Same for municipalities
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
        
        ## TO REINTRODUCE WHEN FARMERS WILL HAVE AN ATTRIBUTE, OTERWISE CONSIDERS ALL
        ## LINES AS EMPTY AND DROPS EVERYTHING
        # farmers_dataframe = farmers_dataframe.dropna(how='all') 
        # if farmers_dataframe.isnull().values.any():
            # raise ValueError('The farmers excel database has some missing values'
            #                  '. Please fill in the right values or remove the '
            #                  'farmer and the relative farm from the database.')
        
        farmers_id = farmers_dataframe.index
        
        duplicated_farmers_id = farmers_id[farmers_id.duplicated()].unique()
        if not duplicated_farmers_id.empty:
            raise ValueError('The farmers dataset has multiple rows with the ' 
                             'following ID values: ' + 
                             ', '.join(duplicated_farmers_id.values))                                
        else:    
            self._farmers_data = farmers_dataframe

    @property
    def farms_data(self):
        return self._farms_data
    
    @farms_data.setter ## CH: normalmente fa poca roba, tipo non legge un excel,
    ## fai una funzione normale da richiamare fuori 
    def farms_data(self, farms_data):
        """
        Convert the farms excel database into a pandas dataframe, check that
        it respect the requirements and substitutes the pasture and
        municipalities columns strings with the respective objects.
        
        Checks:
            Ignores, if present, blank lines from the excel file
            Check that the farms_data excel file:
                - Doesn't have multiple rows referring to the same farmer (i.e. 
                  with the same ID).
                - Has exactly the same indexes (i.e.IDs) as the farmers_data 
                  excel. Otherwise, raises a ValueError exception.
        
        """        
        farms_dataframe = pd.read_excel(farms_data, index_col = 0)
        
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
                
    @staticmethod
    def __replace_strings_with_objects(dataframe, column, mapping):
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
            Raised when in the column there are strings not linked to any
            object in the mapping dict. 

        """

        strings = list(mapping.keys())
        objects = list(mapping.values())
        column_to_modify = dataframe[column]
        column_to_modify.replace(to_replace = strings, 
                                  value = objects, 
                                  inplace = True)
        
        wrong_strings = [entry for entry in column_to_modify 
                         if type(entry) == str]
        if wrong_strings:
            raise ValueError('The column ' + column + ' in the excel databases'
                             ' contains the following wrong entries: ' + 
                             ", ".join(wrong_strings))
        
    def __create_governments(self, payments):
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
    
    def __create_pastures(self):
        """
        Called by the __init__ method.
        
        Creates the attributes possible_pastures and adoptable_pastures.

        """              
        for pasture_class in pastures.Pasture.__subclasses__():
            pasture_object = pasture_class(self)
            self.possible_pastures.append(pasture_object)
            self.pastures_mapping[pasture_object.pasture_type] = pasture_object
        
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
         ##CH: il modello conosce troppe cose. Le classi dovrebbero fare tutto
         ## questo sotto da per sè. Si chiamano farmer data, quindi loro dovrebbero
         ## fare queste cose. Per pasture invece ci sta che il modello
         ## li crei perchè sono solo due oggetti considivisi. Ci sta il fatto che 
         ## comunque la creazione è qui e tutta la logica è dentro. 
         ## Si può passare la creaione delle farm dentro la creazione dei contadini
         
        for id_ in farmers_data.index:
            farmer = agents.Farmer(self.next_id(), self, farmers_data.loc[id_])
            self.schedule.add(farmer)
            farm = agents.Farm(self.next_id(), self, farms_data.loc[id_])
            ## CH: very brutte righe. La farm potrebbe non aver bisogno del farmer
            ## associato.  Poi una dovrebbe essere nascosta da un metodo
            farmer.farm = farm
            farm.farmer = farmer
    
  
    # The following methods are not used for initiation of the model 
    
    def step(self):
        """
        

        Returns
        -------
        None.

        """
        self.market.step()
        for government in self.pasture_governments.values():
            government.step()
            
        print("schedule step")
        
        self.schedule.step()
        
    


