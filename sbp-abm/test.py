# -*- coding: utf-8 -*-
"""
Created on Sat May 23 16:30:47 2020

@author: giaco
"""

import model

# pastures = ['Natural Pasture', 'Sown Permanent Pasture']
farmers_data = "data/FarmersData.xlsx"
farms_data = "data/FarmsData.xlsx"

# Give payments in €/hectare # WULL HAVE TO CONSIDER FOR HOW MANY YEARS
sbp_payment = {
    '2009': 50,
    '2010': 75,
    '2011': 75,
    '2012': 75,
    '2013': 75,
    '2014': 75,
    }

payments = {'Sown Permanent Pasture' : sbp_payment}

# NEED TO PASS TO THE MODEL THE FARMERS AND FARM DATA FILES REFERMENTS, THEN INSIDE THE MODEL READ THEM
#1. Decide type of file to give data (csv, excel) OK
#2. Create files OK
#3. Create function inside model to move files to dataframes OK
    # Do we want to keep the ID as PT01 --> better to further link to AF data
#4. Implement farmers and farms (with a default area) OK
#5. Replace in the dataframe already strings with instances for pastures. 
#6. Analysis on which area/pasture type use from spreadsheet

model = model.SBPAdoption(farmers_data, farms_data, payments)
model.step()


import pandas as pd
map = {'a':1, 'b':2}
series = pd.Series(['a','b','a'])
# model.switch_strings_with_objects(map, series)

