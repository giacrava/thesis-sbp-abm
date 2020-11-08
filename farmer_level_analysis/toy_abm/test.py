# -*- coding: utf-8 -*-

from sbp_toy_abm import model


model = model.FLToyABM()
model.step()

adoption_out = model.datacollector.get_agent_vars_dataframe()
aggr_adoption_out = model.datacollector.get_model_vars_dataframe()
