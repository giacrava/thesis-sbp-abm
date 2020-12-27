# -*- coding: utf-8 -*-
import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin


# class TransformAdoptionFeatures(BaseEstimator, TransformerMixin):

#     def __init__(self, add_square_cumul_adoption=False):
#         self.add_square_cumul_adoption = add_square_cumul_adoption

#     def fit(self, X, y=None):
#         return self

#     def transform(self, X):
#         adoption_features = X.columns
#         # All features referring to tot_cumul excluded (highly corr with 10_y,
#         # that are slighlty more correlated with adoption)

#         # Excluded everything for neighbouring not adjacent, since adoption in
#         # prev_year and cumul_10_y too correlated

#         # Definition of the ones to keep: municipality, adjacent and portugal
#         # not tot_cumul
#         feats_munic = [feat for feat in adoption_features if '_munic' in feat]
#         feats_adj_neigh = [feat for feat in adoption_features
#                            if '_adj' in feat]
#         feats_port = [feat for feat in adoption_features if '_port' in feat]

#         feats_to_keep_all = feats_munic + feats_adj_neigh + feats_port
#         feats_to_keep = [feat for feat in feats_to_keep_all
#                          if 'tot_cumul' not in feat]
#         if self.add_square_cumul_adoption:
#             col_to_add = (X['cumul_adoption_10_y_pr_y_munic']
#                           * X['cumul_adoption_10_y_pr_y_munic'])
#             col_to_add.name = 'cumul_adoption_10_y_pr_y_munic_squared'
#             return pd.concat([X[feats_to_keep], col_to_add], axis=1)
#         else:
#             return X[feats_to_keep]


class TransformCensusFeaturesRegr(BaseEstimator, TransformerMixin):


    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        XX = X[['pastures_area_munic', 'pastures_mean_size_munic']]
        XX = pd.concat([XX, X['individual_prod_num']], axis=1)
        XX = pd.concat([XX, X['individual_prod_in_business']], axis=1)
        XX = pd.concat([XX, X['land_rented']], axis=1)

        feats_above_3rd_cycle = [
                                 'educ_secondary_agr',
                                 'educ_secondary_not_agr',
                                 'educ_polyt_or_superior_agr',
                                 'educ_polyt_or_superior_not_agr']
        educ_above_basic = X[feats_above_3rd_cycle].sum(axis=1)
        educ_above_basic.name = 'educ_above_basic'
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

class TransformCensusFeaturesClsf(BaseEstimator, TransformerMixin):


    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        XX = X[['pastures_area_munic', 'pastures_mean_size_munic']]
        XX = pd.concat([XX, X['individual_prod_num']], axis=1)
        XX = pd.concat([XX, X['individual_prod_in_business']], axis=1)
        XX = pd.concat([XX, X['land_rented']], axis=1)

        feats_above_3rd_cycle = [
                                 'educ_secondary_agr',
                                 'educ_secondary_not_agr',
                                 'educ_polyt_or_superior_agr',
                                 'educ_polyt_or_superior_not_agr']
        educ_above_basic = X[feats_above_3rd_cycle].sum(axis=1)
        educ_above_basic.name = 'educ_above_basic'
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
        
        # All previous years ones excluded since the averages are more correlated!
        
        # Min temp: excluded all since high correlation with av_d_mean_t and
        # low with the target variable
        # Max temp: can keep only one of the two since perfectly correlated,
        # so exluded both days_max_t_over_30
        # Mean temp: excluded days_mean_t_over_20/25 since only one of these
        # kept and av_d_mean_t less correlated with max_t 
        # Prec: exclude both av_prec_sum_pr_y (too correlated with max_t) and
        # days_no
        
        # Definition of the ones to keep.
        feats_mean_t = [feat for feat in climate_features
                        if 'av_d_mean_t_average' in feat]
        feats_max_t = [feat for feat in climate_features
                        if 'av_d_max_t_average' in feat]
        # Precipitation features: keep only cons_days_no_prec
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

        # 'pH_mean_munic' excluded since high correlation with NC and CaCO3
        # (also with av_d_mean_t_average_munic)
        
        # Definition of the ones to keep. 
        feats_to_keep = [feat for feat in soil_features 
                         if feat != 'pH_mean_munic']

        return X[feats_to_keep]
    

# class TransformEconomicFeatures(BaseEstimator, TransformerMixin):

#     def __init__(self):
#         pass

#     def fit(self, X, y=None):
#         return self

#     def transform(self, X):

#         # Nothing to do, it's just sbp_payments and we pass it
#         return X
