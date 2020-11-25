# -*- coding: utf-8 -*-

from municipalities_abm import model
from municipalities_abm.custom_transformers import (
    TransformAdoptionFeatures,
    TransformCensusFeaturesClsf,
    TransformCensusFeaturesRegr,
    TransformClimateFeatures,
    TransformSoilFeatures,
    TransformEconomicFeatures
    )

start_year = 1996

modelSBP = model.SBPAdoption(initial_year=start_year)
modelSBP.step()

# for i in range(start_year, start_year + 1):
#     modelSBP.step()
#     print("Step", str(i))

# adoption_out = modelSBP.datacollector.get_agent_vars_dataframe()
aggr_adoption_out = modelSBP.datacollector.get_model_vars_dataframe()
