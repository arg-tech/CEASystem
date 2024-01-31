from parsing_components import AMFComponents
from claim_extraction import RelationClaimExtractor
from evidence_alignment import EvidenceAligner
from evidence_scoring import AlignmentMarixFilteringScoring
from decision_making import DecisionDistributionMaker

from formats import prepare_output

from config import ALIGNER_MODEL_PATH, ALIGNER_BATCH_SIZE
from config import (MNLI_SCORING_MODEL, MNLI_MODEL_LABEL_DECODER,
                    SCORER_BATCH_SIZE)
from config import TURNINATOR_API, PROPOSITIONALIZER_API, SEGMENTER_API, RELATIONER_API

import numpy as np

class CEASservice:
    def __init__(self):
        self.aligner = EvidenceAligner(
            model_path_name=ALIGNER_MODEL_PATH
        )
        self.scorer = AlignmentMarixFilteringScoring(
            mnli_model_name_path=MNLI_SCORING_MODEL,
            model_label_decoder=MNLI_MODEL_LABEL_DECODER
        )

    def get_claims(self, input_dict):
        aif_json = AMFComponents.parse_text_to_xaif(
            turninator_api=TURNINATOR_API,
            propositionalizer_api=PROPOSITIONALIZER_API,
            segmenter_api=SEGMENTER_API,
            relationer_api=RELATIONER_API,
            text=input_dict["text"]
        )
        aif_json = aif_json["AIF"]

        claim_texts = RelationClaimExtractor.get_claim_texts_aif(
            aif_json=aif_json
        )

        return {
            "code": 200,
            "output": {
                "hypothesis": claim_texts
            }
        }
    def analyze(self, input_dict):
        alignment_matrix = self.aligner.predict(
            hypothesises=input_dict["hypothesis"],
            evidences=input_dict["manual_evidences"],
            batch_size=ALIGNER_BATCH_SIZE
        )

        scoring_dict = self.scorer.score_filter_matrix(
            alignment_matrix=alignment_matrix,
            evidence_texts=input_dict["manual_evidences"],
            hypothesis_texts=input_dict["hypothesis"],
            batch_size=SCORER_BATCH_SIZE,
            min_alignment_limit=input_dict["min_alignment_limit"],
            max_alignment_limit=input_dict["max_alignment_limit"]
        )

        ordered_decision_scores_dict = DecisionDistributionMaker.predict_order(
            scoring_matrix=np.array(scoring_dict["scoring_matrix"])
        )

        request_output = prepare_output(
            ordered_decision_scores_dict=ordered_decision_scores_dict,
            scoring_matrix=scoring_dict["scoring_matrix"],
            hypothesis=input_dict["hypothesis"],
            kept_evidences=scoring_dict["filtered_evidences"],
            dropped_evidences=scoring_dict["dropped_evidences"]
        )

        return {"code": 200, "output": request_output}