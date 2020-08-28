# -*- coding: utf-8 -*-

import pathlib

"""
Inputs needed to instantiate the model.

Data
----------
sbp_payments : str
    Path to the spreadsheed with the total payment in €/hectare provided by the
    Portuguese Carbon Fund for each year.

Parameters default values (the ones used when run.py is runned for the
visualization)
----------
initial_year : int
    Year in the interval 1996 - 2018 in which the simulation is about to start

"""

sbp_payments_path = (pathlib.Path(__file__).parent.parent / 'data'
                     / 'sbp_payments.xlsx')

initial_year = 2009
