# -*- coding: utf-8 -*-
import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin


class TransformCensusFeatures(BaseEstimator, TransformerMixin):

    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        XX = X[['pastures_area_munic', 'pastures_mean_size_munic']]
        XX = pd.concat([XX, X['individual_prod_num']], axis=1)
        XX = pd.concat([XX, X['individual_prod_in_business']], axis=1)
        XX = pd.concat([XX, X['land_rented']], axis=1)

        feats_above_3rd_cycle = ['educ_basic_3rd_cycle',
                                 'educ_secondary_agr',
                                 'educ_secondary_not_agr',
                                 'educ_polyt_or_superior_agr',
                                 'educ_polyt_or_superior_not_agr']
        educ_above_basic = X[feats_above_3rd_cycle].sum(axis=1)
        educ_above_basic.name = 'educ_3rd_cycle_or_higher'
        XX = pd.concat([XX, educ_above_basic], axis=1)

        apf_feats_to_group = ['prof_long', 'prof_short_and_long',
                              'prof_complete']
        apf_grouped = X[apf_feats_to_group].sum(axis=1)
        apf_grouped.name = 'prof_above_some_long'
        XX = pd.concat([XX, apf_grouped], axis=1)

        ext_sit_feats_not_empl = ['ext_sit_self_employed',
                                  'ext_sit_employed_by_others',
                                  'ext_sit_in_family']
        ext_sit_grouped = X[ext_sit_feats_not_empl].sum(axis=1)
        ext_sit_grouped.name = 'ext_sit_not_employer'
        XX = pd.concat([XX, ext_sit_grouped], axis=1)

        # Economic class: keep above 40 and 0-2, 2-4
        feats_econ_above_40 = ['econ_40_100', 'econ_above_100']
        econ_above_40 = X[feats_econ_above_40].sum(axis=1)
        econ_above_40.name = 'econ_above_40'
        XX = pd.concat([XX, econ_above_40, X['econ_0_2'],
                        X['econ_2_4']], axis=1)   

        return XX


class TransformClimateFeatures(BaseEstimator, TransformerMixin):

    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        climate_features = X.columns

        feats_mean_t = [feat for feat in climate_features
                        if 'av_d_mean_t_average' in feat]
        feats_max_t = [feat for feat in climate_features
                       if 'av_d_max_t_average' in feat]
        feats_prec = [feat for feat in climate_features
                      if 'cons_days_no_prec_average' in feat]
        feats_to_keep = feats_mean_t + feats_max_t + feats_prec

        return X[feats_to_keep]


class TransformSoilFeatures(BaseEstimator, TransformerMixin):

    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        soil_features = X.columns

        feats_to_keep = [feat for feat in soil_features
                         if feat != 'pH_mean_munic']

        return X[feats_to_keep]
