# -*- coding: utf-8 -*-

import mesa


class Government(mesa.Agent):
    """


    """

    def __init__(self, unique_id, model, sbp_payments):

        super().__init__(unique_id, model)
        self.sbp_payments = sbp_payments

    # def _retrieve_payments(self, payments): CAN BE CHANGED TO RETRIEVE THE YEAR!
    #     """
    #     Called by the Government sub-classes' __init__ method.
    #     Extract the payments for the relative pasture type. If not available,
    #     raise an exception.

    #     Raises
    #     ------
    #     KeyError
    #         Raised if the "payments" dictionary does not have a key
    #         corresponding to the Pasture instance's attribute pasture_type

    #     Returns
    #     ------
    #     dict
    #         Payment relative to the pasture type the Government subclass deals
    #         with

    #     """
    #     try:
    #         return payments[self.pasture_type]
    #     except KeyError:
    #         raise KeyError('Payment for ' + self.pasture_type + ' not provided'
    #                        ', please include them in the "payments" dictionary'
    #                        '.'
    #                        )
