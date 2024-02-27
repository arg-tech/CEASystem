from fastapi import FastAPI
from formats import RawTextInput, ParsedTextOutput, \
                     return_error_codes, ClaimsEvidenceInput, AnalyzedOutput, prepare_output

from parsing_components import AMFComponents
from claim_extraction import RelationClaimExtractor
from evidence_alignment import EvidenceAligner
from evidence_scoring import AlignmentMarixFilteringScoring
from decision_making import DecisionDistributionMaker


from config import ALIGNER_MODEL_PATH, ALIGNER_BATCH_SIZE
from config import (MNLI_SCORING_MODEL, MNLI_MODEL_LABEL_DECODER,
                    SCORER_BATCH_SIZE)
from config import TURNINATOR_API, PROPOSITIONALIZER_API, SEGMENTER_API, RELATIONER_API

import numpy as np

aligner = EvidenceAligner(
    model_path_name=ALIGNER_MODEL_PATH
)
scorer = AlignmentMarixFilteringScoring(
    mnli_model_name_path=MNLI_SCORING_MODEL,
    model_label_decoder=MNLI_MODEL_LABEL_DECODER
)

# can be tested with: uvicorn en_sac:app --workers 1 --host 0.0.0.0 --port 8000
app = FastAPI()

@return_error_codes()
@app.post("/get_claims/", response_model=ParsedTextOutput)
async def get_claims(input_dict: RawTextInput):
    aif_json = AMFComponents.parse_text_to_xaif(
        turninator_api=TURNINATOR_API,
        propositionalizer_api=PROPOSITIONALIZER_API,
        segmenter_api=SEGMENTER_API,
        relationer_api=RELATIONER_API,
        text=input_dict.text
    )
    aif_json = aif_json["AIF"]

    claim_nodes_dicts, structure_claims_graph = RelationClaimExtractor.get_claim_nodes_aif(
        aif_json=aif_json,
        keep_ya_nodes_texts=input_dict.keep_ya_nodes_texts
    )
    claim_texts = [x["text"] for x in claim_nodes_dicts]

    if not len(claim_texts):
        return {
            "output": {"Error": "No claims detected."},
            "code": 400
        }

    return {
        "code": 200,
        "output": {
            "hypothesis": claim_texts,
            "hypothesis_nodes": claim_nodes_dicts,
            "structure_hypothesis_graph": structure_claims_graph
        }
    }

@return_error_codes()
@app.post("/analyze/", response_model=AnalyzedOutput)
async def analyze(input_dict: ClaimsEvidenceInput):
    alignment_matrix = aligner.predict(
        hypothesises=input_dict.hypothesis,
        evidences=input_dict.manual_evidences,
        batch_size=ALIGNER_BATCH_SIZE
    )

    scoring_dict = scorer.score_filter_matrix(
        alignment_matrix=alignment_matrix,
        evidence_texts=input_dict.manual_evidences,
        hypothesis_texts=input_dict.hypothesis,
        batch_size=SCORER_BATCH_SIZE,
        min_alignment_limit=input_dict.min_alignment_limit,
        max_alignment_limit=input_dict.max_alignment_limit
    )

    ordered_decision_scores_dict = DecisionDistributionMaker.predict_order(
        scoring_matrix=np.array(scoring_dict["scoring_matrix"])
    )

    request_output = prepare_output(
        ordered_decision_scores_dict=ordered_decision_scores_dict,
        scoring_matrix=scoring_dict["scoring_matrix"],
        hypothesis=input_dict.hypothesis,
        kept_evidences=scoring_dict["filtered_evidences"],
        dropped_evidences=scoring_dict["dropped_evidences"],
        structure_hypothesis_graph=input_dict.structure_hypothesis_graph,
        hypothesis_nodes=input_dict.hypothesis_nodes
    )

    return {"code": 200, "output": request_output}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)