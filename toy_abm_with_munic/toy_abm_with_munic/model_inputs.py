# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 09:03:40 2020

@author: giaco
"""
import pathlib

"""
Inputs needed to instantiate the model
----------
farmers_data : str
    Path to the excel file with the farmers data. Cannot have
    multiple rows referring to the same farmer (i.e. with the same ID)
farmers_data : str
    Path to the excel file with the farms data. There has to be at
    least one farm per each farmer and the ID columns have to match
payments : dict
    Maps each pasture type to the realtive payment

"""
farmers_data = (pathlib.Path(__file__).parent.parent / 'data'
                / 'FarmersData.xlsx')

farms_data = pathlib.Path(__file__).parent.parent / 'data' / 'FarmsData.xlsx'

sbp_payment = [50, 50, 50]
payments = {'Sown Permanent Pasture': sbp_payment}
