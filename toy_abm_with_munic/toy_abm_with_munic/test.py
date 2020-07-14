# -*- coding: utf-8 -*-
"""
Created on Sat May 23 16:30:47 2020

@author: giaco
"""

import model

farmers_data = "../data/FarmersData.xlsx"
farms_data = "../data/FarmsData.xlsx"

# Give payments in €/hectare, one entry for each year 
## WILL HAVE TO CONSIDER FOR HOW MANY YEARS
sbp_payment = [50, 50, 50]

payments = {'Sown Permanent Pasture': sbp_payment}


modelSBP = model.SBPAdoption(farmers_data, farms_data, payments, seed=0)
modelSBP.step()


# for farmer in model.schedule.agents:
#     print('Farm', farmer.code + ':' + farmer.farm.pasture_type.type)
    
#     # maybe better to add farms to a list when initialized, to retrieve 
#     # more easily their type at any moment

adoption_out = modelSBP.datacollector.get_agent_vars_dataframe()
aggr_adoption_out = modelSBP.datacollector.get_model_vars_dataframe()
