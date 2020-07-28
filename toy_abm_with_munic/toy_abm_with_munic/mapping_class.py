# -*- coding: utf-8 -*-

class Mappings:
    """
    Class storing all the identificative string - object mappings.

    Attributes
    ----------
    farms : dict
        Links each farm object (the values) to a string representing their ID
        in the farms database
        (the keys)
    municipialities : dict
        Links each Municipality object (the values) to a string representing
        their name (the keys)
    pastures : dict
        Links each Pasture object (the values) to a string representing their
        type (the keys)

    Methods
    ----------
    from_municipality get_farms
        Given a certain municipality, it returns the list of Farm objects
        located in that municipality.

    """

    def __init__(self):

        # self.farmers = {}
        self.farms = {}
        self.municipalities = {}
        self.pastures = {}

    def from_municipality_get_farms(self, municipality):
        """
        Method to retrieve the farms located in a certain municipality.

        Parameters
        ----------
        municipality : str
            Name of the municipality to retrieve the farms located in

        Returns
        -------
        list
            List of Farm objects located in the municipality

        """
        if municipality not in self.municipalities:
            print('No municipality called ' + municipality + ".")
        else:
            farms_in_munic = self.municipalities[municipality].farms
            return [self.farms[str] for str in farms_in_munic]


mappings = Mappings()
