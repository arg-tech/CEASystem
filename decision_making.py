import numpy as np

class DecisionDistributionMaker:
    @classmethod
    def predict_order(cls, scoring_matrix):
        zero2na_scoring_matrix = scoring_matrix.copy()
        zero2na_scoring_matrix[zero2na_scoring_matrix == 0] = np.nan
        means = np.nanmean(zero2na_scoring_matrix, axis=1)

        means[np.isnan(means)] = -1.0

        ordered_means_ids = np.argsort(means).tolist()[::-1]
        ordered_scores = list(sorted(means.tolist(), reverse=True))[::-1]
        return {
            "order_ids": ordered_means_ids,
            "scores": ordered_scores
        }


