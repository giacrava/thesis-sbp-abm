# -*- coding: utf-8 -*-
"""
Created on Sat May 23 16:30:47 2020

@author: giaco
"""

import model

farmers_data = "data/FarmersData.xlsx"
farms_data = "data/FarmsData.xlsx"

# Give payments in €/hectare # WILL HAVE TO CONSIDER FOR HOW MANY YEARS
sbp_payment = {
    '2009': 50,
    '2010': 75,
    '2011': 75,
    '2012': 75,
    '2013': 75,
    '2014': 75,
    }

payments = {'Sown Permanent Pasture' : sbp_payment}


model = model.SBPAdoption(farmers_data, farms_data, payments)
model.step()

