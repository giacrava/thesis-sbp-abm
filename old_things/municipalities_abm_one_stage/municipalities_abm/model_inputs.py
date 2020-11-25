# -*- coding: utf-8 -*-

import pathlib

"""
Inputs needed to instantiate the model.

Data
----------
sbp_payments : str
    Path to the spreadsheed with the total payment in €/hectare provided by the
    Portuguese Carbon Fund for each year.

"""

sbp_payments_path = (pathlib.Path(__file__).parent.parent / 'data'
                     / 'sbp_payments.xlsx')