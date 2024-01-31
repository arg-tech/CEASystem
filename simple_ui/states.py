

class CurrentAnalysisState:
    def __init__(self):
        self.article_text = ""

        self.hypothesis = []
        self.evidences = []
        self.min_alignment_limit = -1
        self.max_alignment_limit = -1

        self.analysis_result = {
            "dropped_evidences": [],
            "ordered_hypothesises_scores": [],
            "filtered_scoring_matrix": [],
            "full_ordered_evidences": [],
            "full_scoring_matrix": [],
            "kept_evidences": [],
            "ordered_hypothesises": [],
            "ordered_hypothesises_scores": []
        }

    def set_article(self, article_text):
        self.article_text = article_text

    def set_min_alignment_limit(self, min_alignment_limit):
        self.min_alignment_limit = int(min_alignment_limit.replace(" ", ""))
    def set_max_alignment_limit(self, max_alignment_limit):
        self.max_alignment_limit = int(max_alignment_limit.replace(" ", ""))

    def set_claims(self, hyp_result):
        self.hypothesis = hyp_result["output"]["hypothesis"]

    def set_evidences(self, separated_evidences):
        self.evidences = separated_evidences.split("\n")
        self.evidences = [x for x in self.evidences if x.strip()]

    def set_analysis_result(self, result):
        self.analysis_result = result["output"]


