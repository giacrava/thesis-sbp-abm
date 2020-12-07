# -*- coding: utf-8 -*-


class MunicipalityClimate:
    """
    Class for MunicipalityClimate object, responsible for reporting all the
    climatic specifications of the Municipality.

    Attributes
    ----------
    yearly : pandas DataFrame
        Reports for each year the mean temperature over the municipality in °C
        and the mean precipitation sum in mm / areas of 0.1° side

    """

    def __init__(self, munic_climate_data):
        """
        Parameters
        ----------
        munic_climate_data : pandas DataFrame
            DataFrame reporting for each year the climate variables for the
            municipality.

        """
        self.yearly = munic_climate_data
