# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 15:51:15 2020

@author: giaco
"""
import pathlib
import geopandas as gpd

from municipalities_neighbours import MunicipalitiesNeighbours

municipalities_shp_path = (pathlib.Path(__file__).parent.parent
                           / 'concelhos_no_azores_and_madeira.shp')
municipalities_data = gpd.read_file(municipalities_shp_path)
municipalities_data.rename(columns={'Municipali': 'Municipality'},
                           inplace=True)
municipalities_data.set_index('Municipality', drop=False, inplace=True)

# Remove municipalities in Algarve
in_algarve = municipalities_data.loc[
    municipalities_data['District'] == 'Faro'
    ].index
municipalities_data.drop(in_algarve, inplace=True)


model = MunicipalitiesNeighbours(municipalities_data)

municipalities_with_neighbours = model.get_neighbours_data()

# Remove rows corresponding to Lisboa, Porto and São João da Madeira
# to_drop = ['Porto', 'Lisboa', 'São João da Madeira']
# municipalities_with_neighbours.drop(to_drop, inplace=True)

out_file = "municipalities_neighbours.csv"
municipalities_with_neighbours.to_csv(out_file)
