# -*- coding: utf-8 -*-
"""
Created on Thu May 28 14:52:56 2020

@author: giaco
"""

import mesa


class Farm:
    """
    Class for farm objects.
       
    Farms:
        - are initialized by the farmer that owns them
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
        
    Methods
    ---------- 
    step
    
    """  
    def __init__(self, unique_id, model_adoptable_pastures, farm_data): 
        """
        Parameters
        ----------
        farm_data : pandas Series
            Contains the data of the farms, contained in the relative row of
            the farms excel database.
            

        """
        self.unique_id = unique_id
        self.code = farm_data.name
        self.model_adoptable_pastures = model_adoptable_pastures
        
        # Data from database
        # self.pasture_area = ## DEPEND HOW WE CONSIDER AREAS
        self.pasture_type = farm_data['Pasture']
        # self.municipality = farm_data['Municipality']
            ## probably also to be added to the municipality here
        
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
        ## class)
        
        print("farm", self.code,"step")
        
        farm_adoptable_pastures = [pasture for pasture
                                   in self.model_adoptable_pastures
                                   if pasture != self.pasture_type]

        if farm_adoptable_pastures: ## MAYBE BETTER TO MOVE TO ANOTHER FUNCTION
                                    ## DONE ONLY IF PASTURE NATURAL IN TOY MODEL
            NPV_keeping_actual = self.pasture_type.NPV_keeping()
            NPVs_adoption = []
            NPVs_differential = []
            for pasture in farm_adoptable_pastures:
                NPV_adoption = pasture.NPV_adoption()
                NPVs_adoption.append(NPV_adoption)
                NPV_differential = NPV_adoption - NPV_keeping_actual
                NPVs_differential.append(NPV_differential)
                
            # Calculate geog influence
            # Scores from logistic regression
            # Pick best
            # Prob. of adoption
                
            print(NPVs_adoption, NPVs_differential)
        
 