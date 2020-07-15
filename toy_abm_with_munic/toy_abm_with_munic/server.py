# -*- coding: utf-8 -*-
"""
Created on Thu May 21 09:43:17 2020

@author: giaco
"""
from mesa.visualization.modules import TextElement
from mesa_geo.visualization.MapModule import MapModule
from mesa_geo.visualization.ModularVisualization import ModularServer

from .model import SBPAdoption, get_percentage_adopted


class FarmersAdoption(TextElement):
    """
    Display a text count of how many farmers have adopted SBP.
    """

    def render(self, model):
        adopted = '{0:.2f}'.format(get_percentage_adopted(model))
        return "Percentage of farmers that have adopted: {}".format(adopted)

def map_draw(agent):
    """
    Portrayal Method for canvas
    """
    portrayal = dict()
    portrayal["color"] = "Blue"
    # if agent.atype is None:
    #     portrayal["color"] = "Grey"
    # elif agent.atype == 0:
    #     portrayal["color"] = "Red"
    # else:
    #     portrayal["color"] = "Blue"
    return portrayal


adoption_percent = FarmersAdoption()
map_element = MapModule(map_draw, [38.5714, -7.9135], 7, 500, 500)

modular_server = ModularServer(
    SBPAdoption, [adoption_percent, map_element], "SBP adoption"
    )
# server.port = 8521
