# -*- coding: utf-8 -*-

from mesa.visualization.modules import TextElement
from mesa_geo.visualization.MapModule import MapModule
from mesa_geo.visualization.ModularVisualization import ModularServer

from .model import SBPAdoption#, get_percentage_adopted


# class FarmersAdoption(TextElement):
#     """
#     Display a text count of how many farmers have adopted SBP.
#     """

#     def render(self, model):
#         adopted = '{0:.2f}'.format(get_percentage_adopted(model))
#         return "Percentage of farmers that have adopted: {}".format(adopted)


def map_draw(agent):
    """
    Portrayal Method for canvas
    """

    portrayal = dict()
    if agent.cumul_adoption_10y_ha == 0:
        portrayal["color"] = "Grey"
    else:
        portrayal["color"] = "Blue"
    return portrayal
    return portrayal


# adoption_percent = FarmersAdoption()
map_element = MapModule(map_draw, [38.5714, -7.9135], 7, 500, 500)

modular_server = ModularServer(
    SBPAdoption, [map_element], "SBP adoption"
    )
# server.port = 8521
