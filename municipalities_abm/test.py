# -*- coding: utf-8 -*-
%load_ext autoreload
%autoreload 2

from municipalities_abm import model


modelSBP = model.SBPAdoption()
modelSBP.step()

# adoption_out = modelSBP.datacollector.get_agent_vars_dataframe()
# aggr_adoption_out = modelSBP.datacollector.get_model_vars_dataframe()
