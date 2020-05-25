# -*- coding: utf-8 -*-
"""
Created on Sat May 23 16:30:47 2020

@author: giaco
"""

import model

# pastures = ['Natural Pasture', 'Sown Permanent Pasture']

# Give subsidies in €/hectare
sbp_subsidy = {
    '2009' : 50,
    '2010' : 75,
    '2011' : 75,
    '2012' : 75,
    '2013' : 75,
    '2014' : 75,
    }

subsidies = {'Sown Permanent Pasture' : sbp_subsidy}

model = model.SBPAdoption(subsidies)

