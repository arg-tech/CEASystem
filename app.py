from fastapi import FastAPI
from formats import RawTextInput, ParsedTextOutput, \
                     return_error_codes, ClaimsEvidenceInput, AnalyzedOutput, prepare_output

from parsing_components import DummyAIF
from evidence_alignment import EvidenceAligner
from evidence_scoring import AlignmentMarixFilteringScoring
from decision_making import DecisionDistributionMaker
from claim_worthiness import ClaimWorthiness
from claim_detection import ClaimExtractor

from config import ALIGNER_MODEL_PATH, ALIGNER_BATCH_SIZE
from config import (SCORING_MODEL, SCORING_MODEL_LABEL_DECODER,
                    SCORER_BATCH_SIZE)
from config import (CLAIM_EXTRACTOR_MODEL_PATH, CLAIM_EXTRACTOR_KEEP_LOGIT_IDX,
                    CLAIM_EXTRACTOR_CONFIDENCE_THOLD, CLAIM_EXTRACTOR_BATCH_SIZE)
from config import (CLAIM_WORTHINESS_MODEL, CLAIM_WORTHINESS_BATCH_SIZE,
                    CLAIM_WORTHINESS_ID2LABEL, CLAIM_WORTHINESS_CONFIDENCE_THOLD)

import numpy as np
from hardcoded import demo_utility_hardcoded_articles

claim_extractor = ClaimExtractor(
    model_path_name=CLAIM_EXTRACTOR_MODEL_PATH,
    keep_logit_idx=CLAIM_EXTRACTOR_KEEP_LOGIT_IDX,
    conf_thold=CLAIM_EXTRACTOR_CONFIDENCE_THOLD
)
aligner = EvidenceAligner(
    model_path_name=ALIGNER_MODEL_PATH
)
scorer = AlignmentMarixFilteringScoring(
    mnli_model_name_path=SCORING_MODEL,
    model_label_decoder=SCORING_MODEL_LABEL_DECODER
)
claim_worthiness_model = ClaimWorthiness(
    model_path_name=CLAIM_WORTHINESS_MODEL,
    label2id=CLAIM_WORTHINESS_ID2LABEL,
    confidence_thold=CLAIM_WORTHINESS_CONFIDENCE_THOLD
)


# can be tested with: uvicorn en_sac:app --workers 1 --host 0.0.0.0 --port 8000
app = FastAPI()

@return_error_codes()
@app.post("/get_claims/", response_model=ParsedTextOutput)
async def get_claims(input_dict: RawTextInput):

    if "This new regulatory framework, which aims to ensure responsible and transparent AI usage across Europe, has led to stricter scrutiny of AI applications, particularly those involving human-like interactions." in input_dict.text:
        claims = [
            "EU Bans ChatGPT's Advanced Voice Mode Over Non-Compliance with AI Act Regulations",
            "OpenAI CEO Sam Altman explained on X that the voice mode will remain inaccessible in the EU, due to regulatory compliance issues, acknowledging the difficult balance between innovation and adhering to global regulations.",
            "This particularly in contexts where AI systems can infer human emotions, such as for the voice-based advanced system (cf. Recital 44).",
            "Critics are numerous: as remarked by the Welsh politician Tom Giffard in a speech in the Welsh Parliament, overly stringent regulations could stifle important technological advancements such as the Advanced Voice Mode"
        ]
        aif_json = DummyAIF.make_aif(texts=claims)
        return {
            "code": 200,
            "output": {
                "hypothesis": claims,
                "hypothesis_nodes": aif_json["nodes"],
                "structure_hypothesis_graph": []
            }
        }


    if str(input_dict.text).replace("\n", "").replace(" ", "").replace("\t", "") in demo_utility_hardcoded_articles:
        claims = demo_utility_hardcoded_articles[str(input_dict.text).replace("\n", "").replace(" ", "").replace("\t", "")]
        aif_json = DummyAIF.make_aif(texts = claims)
        return {
        "code": 200,
        "output": {
            "hypothesis": claims,
            "hypothesis_nodes": aif_json["nodes"],
            "structure_hypothesis_graph": []
        }
    }

    else:
    # Extracting claims.
    # The graph tools are nor build yet, so leave it empty
        claims = claim_extractor.get_claims(
            text=input_dict.text,
            batch_size=CLAIM_EXTRACTOR_BATCH_SIZE
        )
        aif_json = DummyAIF.make_aif(texts=claims)
        claim_nodes_dicts = aif_json["nodes"]
        structure_claims_graph = []
    
        claim_nodes_dicts, structure_claims_graph = claim_worthiness_model.predict(
            claim_nodes_dicts=claim_nodes_dicts,
            structure_claims_graph=structure_claims_graph,
            batch_size=CLAIM_WORTHINESS_BATCH_SIZE
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
