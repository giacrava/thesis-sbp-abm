# -*- coding: utf-8 -*-

import pathlib

"""
Inputs needed to instantiate the model

Fixed data
----------
farmers_data : str
    Path to the excel file with the farmers data. Cannot have multiple rows
    referring to the same farmer (i.e. with the same ID)
farmers_data : str
    Path to the excel file with the farms data. There has to be exactly one
    farm per each farmer and the ID columns have to match

Default data (data that can be changed to run simulations)
----------
payments: dict
    Map of each pasture type to the relative payments
pasture_costs : dict
    Map of each pasture to its installation and maintenance yearly costs
weights : tuple
    Weights to calculate the confidence factor, for the features
    in the following order:
    HighestEducationalDegree, PastureSurface, LegalForm, PercentRentedLand

"""
farmers_data = (pathlib.Path(__file__).parent.parent / 'data'
                / 'FarmersData.xlsx')

farms_data = pathlib.Path(__file__).parent.parent / 'data' / 'FarmsData.xlsx'

sbp_payments = [50.72, 50.72, 51.82]
payments = {"Sown Permanent Pasture": sbp_payments}

pastures_costs = {"Sown Permanent Pasture": {
                    "installation": [-722.97],
                    "maintenance": [0.00, -135.96, 0.00, -318.27, 0.00,
                                    -135.96, 0.00, -318.27, 0.00]
                          },
                  'Natural Pasture': {
                      "installation": [0.],
                      "maintenance": [-235.40, -210.18, -210.18, -210.18,
                                      -210.18, -235.40, -210.18, -210.18, 
                                      -210.18]
                      }
                  }

weights = (0.1, 0.1, 0.1, 0.1)