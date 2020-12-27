# -*- coding: utf-8 -*-

from mesa.visualization.modules import TextElement, ChartModule
from mesa_geo.visualization.MapModule import MapModule
from mesa_geo.visualization.ModularVisualization import ModularServer
import plotly.colors

from .model import SBPAdoption
from .custom_transformers import (
    TransformCensusFeaturesClsf,
    TransformCensusFeaturesRegr,
    TransformClimateFeatures,
    TransformSoilFeatures
    )
from .colors_interpolation import get_continuous_color

start_year = 1996


class YearPassed(TextElement):
    """
    Display the year for which the simulation was already done.
    """

    def render(self, model):
        year_passed = model.year - 1
        return ("Year passed: " + str(year_passed))


def map_draw(agent):
    """
    Portrayal Method for canvas
    """

    portrayal = dict()

    # Choice of upper limit (over which maximum color):
    # max value in real data: around 15000
    # in 2015 paper, darkest color is 4000-6000
    # 28 municipalities reach 1000 ha in the real data in 2012
    # 43 municipalities reach 500 ha in the real data in 2012
    # 50 municipalities reach 300 in the real data in 2012
    higher_lim_int = 4000
    lower_lim_int = 0

    # Choice of scale of colours
    # For other color scales: https://plotly.com/python/builtin-colorscales/
    scale_chosen = plotly.colors.diverging.Picnic

    ha_adopt = agent.cumul_adoption_tot_ha

    norm_ha_adopt = (
        (ha_adopt - lower_lim_int) / (higher_lim_int - lower_lim_int)
        )

    scale_colors, _ = plotly.colors.convert_colors_to_same_type(scale_chosen)
    colorscale = plotly.colors.make_colorscale(scale_colors)

    portrayal["color"] = get_continuous_color(colorscale, norm_ha_adopt)
    return portrayal

# Not needed, since already in the chart
# class AreaAdopted(TextElement):
#     """
#     Display a text count of how much area was adopted in total last year and
#     over all years.
#     """

#     def render(self, model):
#         year = model.year
#         year_adopted = '{0:.2f}'.format(
#             model.yearly_adoption_ha_port.loc[year]
#             )
#         tot_adopted = '{0:.2f}'.format(get_total_area_adopted(model))
#         out = ("In {} SBP was installed in {} ha.\n".format(year, year_adopted)
#                + "Total area installed from 1996: {} ha".format(tot_adopted))
#         return out

year_text = YearPassed()
map_element = MapModule(map_draw, [38.5714, -7.9135], 7, 600, 600)

model_var_col = {"Total area of SBP sown [ha]": "#000000",
                 "Area sown in the last year [ha/y]": "Blue"}

adoption_chart = ChartModule(
    [{"Label": label, "Color": col} 
     for (label, col) in model_var_col.items()],
    canvas_height=350,
    canvas_width=500
)

model_params = {"initial_year": start_year}

modular_server = ModularServer(
    SBPAdoption,
    [year_text, map_element, adoption_chart],
    "SBP adoption",
    model_params
    )
# server.port = 8521
