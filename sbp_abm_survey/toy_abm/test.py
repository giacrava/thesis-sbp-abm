# -*- coding: utf-8 -*-

from sbp_toy_abm import model


modelSBP = model.SBPAdoption()
modelSBP.step()


# for farmer in model.schedule.agents:
#     print('Farm', farmer.code + ':' + farmer.farm.pasture_type.type)
    
#     # maybe better to add farms to a list when initialized, to retrieve 
#     # more easily their type at any moment

adoption_out = modelSBP.datacollector.get_agent_vars_dataframe()
aggr_adoption_out = modelSBP.datacollector.get_model_vars_dataframe()
