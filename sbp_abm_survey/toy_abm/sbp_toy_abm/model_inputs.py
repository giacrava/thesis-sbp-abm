# -*- coding: utf-8 -*-

import pathlib

"""
Inputs needed to instantiate the model

Data
----------
farmers_data : str
    Path to the excel file with the farmers data. Cannot have multiple rows 
    referring to the same farmer (i.e. with the same ID)
farmers_data : str
    Path to the excel file with the farms data. There has to be exactly one 
    farm per each farmer and the ID columns have to match

Parameters default values (the ones used when run.py is runned for the
visualization)
----------
payments : dict
    Maps each pasture type to the realtive payment
discount_rate : float
    Discount rate for economic calculations

"""
farmers_data = (pathlib.Path(__file__).parent.parent / 'data'
                / 'FarmersData.xlsx')

farms_data = pathlib.Path(__file__).parent.parent / 'data' / 'FarmsData.xlsx'

sbp_payment = [66.67, 66.67, 66.67]
payments = {'Sown Permanent Pasture': sbp_payment}

discount_rate = 0.05
