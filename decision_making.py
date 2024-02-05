import numpy as np

class DecisionDistributionMaker:
    """
    Scoring claims based on the obtained claim-evidence scoring matrix
    """
    @classmethod
    def predict_order(cls, scoring_matrix):
        """
        Predicting score and order of hypothesises from the least likely to the most likely
        The algorithm is an average of all non-zero evidences for the claim.

        :param scoring_matrix: numpy.array; scoring matrix of claims and evidences. Claims are rows, evidences are columns
        0 in the matrix is considered to be irrelevant evidence to claim
        :return: dict:
            {
                "order_ids": list of ints, order of claims by the least likely to the most likely to scores in "scores",
                "scores": list of floats, sorted list of scores for claims in range of [-1,1]. -1 is not likely at all, should be rejected; +1 means likely, shou;d be accepted.
            }
        """
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


