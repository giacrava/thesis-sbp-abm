# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 15:39:40 2020

@author: giaco
"""
import mesa
import mesa_geo

from municipality import Municipality


class MunicipalitiesNeighbours(mesa.Model):

    def __init__(self, shapefile):
        self.shapefile = shapefile
        
        self.grid = mesa_geo.GeoSpace()

        self._initialize_municipalities()
        
        self.get_neighbours()

    def _initialize_municipalities(self):
        data_is_null = self.shapefile.isnull()
        if data_is_null.values.any():
            munic_with_nan = self.shapefile[
                                data_is_null.any(axis=1)].index.tolist()
            raise ValueError('The municipalities dataset is missing values for'
                             ' the following municipalities: ' +
                             ', '.join(munic_with_nan))

        AC = mesa_geo.AgentCreator(agent_class=Municipality,
                                   agent_kwargs={"model": self})
        municipalities = AC.from_GeoDataFrame(gdf=self.shapefile,
                                              unique_id='CCA_2')
        self.grid.add_agents(municipalities)

    def get_neighbours(self):
        columns = ['neighbours_adj', 'neighbours_10km', 'neighbours_20km',
                   'neighbours_40km', 'neighbours_60km', 'neighbours_80km']
        self.shapefile[columns] = None

        for munic in self.grid.agents:
            munic.neighbours_adj = munic.get_neighbours()
            self.shapefile.at[munic.Municipality, 'neighbours_adj'] = (
                munic.neighbours_adj)

            munic.neighbours_10km = munic.get_neighbours_within_distance(10000)
            self.shapefile.at[munic.Municipality, 'neighbours_10km'] = (
                munic.neighbours_10km)
            munic.neighbours_20km = munic.get_neighbours_within_distance(20000)
            self.shapefile.at[munic.Municipality, 'neighbours_20km'] = (
                munic.neighbours_20km)
            munic.neighbours_40km = munic.get_neighbours_within_distance(40000)
            self.shapefile.at[munic.Municipality, 'neighbours_40km'] = (
                munic.neighbours_40km)
            munic.neighbours_60km = munic.get_neighbours_within_distance(60000)
            self.shapefile.at[munic.Municipality, 'neighbours_60km'] = (
                munic.neighbours_60km)
            munic.neighbours_80km = munic.get_neighbours_within_distance(80000)
            self.shapefile.at[munic.Municipality, 'neighbours_80km'] = (
                munic.neighbours_80km)
            

    def get_neighbours_data(self):
        neighbours_data = self.shapefile.drop(['Municipality', 'geometry'],
                                              axis=1)
        return neighbours_data