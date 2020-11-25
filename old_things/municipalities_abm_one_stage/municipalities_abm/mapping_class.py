# -*- coding: utf-8 -*-

import pandas as pd

class Mappings:
    """
    Class storing all the identificative string - object mappings.

    Attributes
    ----------
    municipialities : dict
        Links each Municipality object (the values) to a string representing
        their name (the keys)

    Methods
    ----------

    """

    def __init__(self):

        self.municipalities = pd.Series()

    # def from_municipality_get_farms(self, municipality):
    #     """
    #     Method to retrieve the farms located in a certain municipality.

    #     Parameters
    #     ----------
    #     municipality : str
    #         Name of the municipality to retrieve the farms located in

    #     Returns
    #     -------
    #     list
    #         List of Farm objects located in the municipality

    #     """
    #     if municipality not in self.municipalities:
    #         print('No municipality called ' + municipality + ".")
    #     else:
    #         farms_in_munic = self.municipalities[municipality].farms
    #         return [self.farms[str] for str in farms_in_munic]


mappings = Mappings()
