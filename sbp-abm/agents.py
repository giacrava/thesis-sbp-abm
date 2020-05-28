# -*- coding: utf-8 -*-
"""
Created on Thu May 21 09:45:52 2020

@author: giaco
"""
import mesa

## CH: good norm 1 class for file, even subclasses! Maybe in a folder agents. Then 1 only file to
## put all the imports and then import the file. Even if in Python seen often. Every file should be long as one video

class Government(mesa.Agent): #@ CH: should be abstract, since not intialized --> multiple inheritance
    """
    Base class for the agents reporting payments for ecosystem services from 
    pastures.
    Should not be instantiated.
        
    """   
    
    def __init__(self, unique_id, model):
        # super().__init__(unique_id, model)
        pass
        
    def _retrieve_subsidy(self, payments):
        """
        Called by the Government sub-classes' __init__ method.
        Extract the payments for the relative pasture type. If not available, 
        raise an exception.

        Raises
        ------
        KeyError
            Raised if the "payments" dictionary does not have a key 
            corresponding to the Pasture instance's attribute pasture_type

        Returns
        ------
        dict
            Payment relative to the pasture type the Government subclass deals
            with
        
        """
        try:
            return payments[self.pasture_type]
        except KeyError:
            raise KeyError('Payment for '+ self.pasture_type +' not provided.'
                           'Please include them in the "payments" dictionary.'
                           )
        ## CH: porcata, pasture type non c'è qui andrebbe dichiarata vuota nel __init__   
    def step(self):
        pass
       
class SownPermanentPasturesGovernment(Government):
    """
    Agent reporting the payments regarding Sown Permanent Pastures
    
    Attributes
    ----------
    pasture_type : str
        The pasture type they report the payment for 
    
    payment : dict
        Report the payment for adoption from 2009 to 2014
        
    """       
    def __init__(self, unique_id, model, subsidies):
        """
        Initialize a SownPermanentPasturesGovernment object, retrieving the 
        relative payment for ecosystem services.

        Parameters
        ----------
        subsidies : dict
            Maps each pasture type to the relative payment

        """
        super().__init__(unique_id, model)
        self.pasture_type = 'Sown Permanent Pasture'
        self.payment = self._retrieve_subsidy(subsidies)
        

class Market(mesa.Agent):
    """
    Agent representing the market, from where farmers access prices and
    economic values
    
    Attributes
    ----------
    
    
    """  
    
    def step(self):
        pass


class Municipality(mesa.Agent):
    """
    Agent representing the market, from where farmers access prices and
    economic values
    
    Attributes
    ----------
    
    
    """   
    pass


class Farmer(mesa.Agent):
    """
    Class for the farmer agents.
    
    Farmers:
        - own a farm
        - have a step method that is directly called by the model's schedule at 
          each model step
    
    Attributes
    ----------
    code : str
        ID of the farmer in the farmers excel database    
    farm : Farm object
        Farm that the farmer owns
        
    Methods
    ----------   
    step
    
    """  
    def __init__(self, unique_id, model, farmer_data):
        """
        Parameters
        ----------
        farmer_data : pandas Series
            Contains the data of the farmers, contained in the relative row of
            the farmers excel database.

        Returns
        -------
        None.

        """
        super().__init__(unique_id, model)
        self.code = farmer_data.name
        self.farm = None
        
    def step(self):
        """
        Step method called every model step by the scheduler.

        Calls the step method of the farmers' farm.

        """
        self.farm.step()

class Farm(mesa.Agent):
    """
    Class for the farm objects.
    
    Farms:
        - are owned by a farmer
        - have one and only one type of pasture
        - are in a municipality
    
    Attributes
    ----------
    code : str
        ID of the farm in the farms excel database    
    pasture_type : Pasture object
        The pasture that the farm is adopting
    municipality : Municipality object
        The municipality where the farm is
    farmer : Farmer object
        The farmer that owns the farm
        
    Methods
    ---------- 
    step
    
    """  
    def __init__(self, unique_id, model, farm_data): 
        ## CH: fai attenzione a passare tutto da per tutto (come il modello)
        ## perchè violi  la programmazione ad oggetti principles
        """
        Parameters
        ----------
        farm_data : pandas Series
            Contains the data of the farms, contained in the relative row of
            the farms excel database.

        """
        super().__init__(unique_id, model)
        self.code = farm_data.name
        
        # self.pasture_area = ## DEPEND HOW WE CONSIDER AREAS
        self.pasture_type = farm_data['Pasture']
        # self.municipality = farm_data['Municipality']
        self.farmer = None
        
    def step(self):
        """
        Step method by the step method of the farmer that own the farm.
        
        Check if any different pasture can be adopted.
        In case:
            - Calculate NPV of keeping actual pasture
            - Calculate NPV of adoption of each adoptable pasture
            - Calculate differential NPVs

        """
        ## Check if pasture expired here? Would be called also in case pasture
        ## is natural, but can just be a pass method (maybe even in the parent
        ## class) --> ha senso tenere passato il model quando l'unica cosa che 
        ## che serve sono le adoptable pastures? Potrebbe essere un problema
        ## se vogliamo cambiare le le adoptable pastures nel main. Se passi 
        ## solo l'oggetto lo vedi nel model cosa passi e quindi cosa viene 
        ## influenzato
        
        print("farm", self.code,"step")
        
        adoptable_pastures = [past for past in self.model.adoptable_pastures
                              if past != self.pasture_type]

        if adoptable_pastures: ## MAYBE BETTER TO MOVE TO ANOTHER FUNCTION
                                ## DONE ONLY IF PASTURE NATURAL IN TOY MODEL
            NPV_keeping_actual = self.pasture_type.NPV_keeping()
            NPVs_adoption = []
            NPVs_differential = []
            for pasture in adoptable_pastures:
                NPV_adoption = pasture.NPV_adoption()
                NPVs_adoption.append(NPV_adoption)
                NPV_differential = NPV_adoption - NPV_keeping_actual
                NPVs_differential.append(NPV_differential)
                
            # Calculate geog influence
            # Scores from logistic regression
            # Pick best
            # Prob. of adoption
                
            print(NPVs_adoption, NPVs_differential)
        
 
        