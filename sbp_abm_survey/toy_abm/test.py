# -*- coding: utf-8 -*-

from sbp_toy_abm import model


model = model.FLToyABM()
model.step()


# for farmer in model.schedule.agents:
#     print('Farm', farmer.code + ':' + farmer.farm.pasture_type.type)

#     # maybe better to add farms to a list when initialized, to retrieve
#     # more easily their type at any moment

adoption_out = model.datacollector.get_agent_vars_dataframe()
aggr_adoption_out = model.datacollector.get_model_vars_dataframe()
