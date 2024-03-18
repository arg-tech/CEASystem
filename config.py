# ALIGNMENT CONFIG VARIABLES
ALIGNER_MODEL_PATH = "yevhenkost/cutiesRun28-05-2020-roberta-base-evidenceAlignment"
ALIGNER_BATCH_SIZE = 6

# SCORING CONFIG VARIABLES
SCORING_MODEL = "roberta-large-mnli"
SCORING_MODEL_LABEL_DECODER = {"entailment": 2, "contradiction": 0}
SCORER_BATCH_SIZE = 6

# CLAIM WORTHINESS VARIABLES
CLAIM_WORTHINESS_MODEL = "yevhenkost/claimbuster-yesno-binary-bert-base-cased"
CLAIM_WORTHINESS_BATCH_SIZE = 6
CLAIM_WORTHINESS_ID2LABEL = {0: "NO", 1: "YES"}
CLAIM_WORTHINESS_CONFIDENCE_THOLD = 0.8

# API addresses
TURNINATOR_API = "http://amf2.arg.tech/turninator-01"
PROPOSITIONALIZER_API = "http://amf2.arg.tech/propositionUnitizer-01"
SEGMENTER_API = "http://amf2.arg.tech/segmenter-01"

# Legacy 8n8 deployed service
# RELATIONER_API = "http://amf2.arg.tech/bert-te"

# New service - new method. If changing to 8n8, make sure to adjust in parsing_components.py
# the way it loads and processing of inputs and outpus
RELATIONER_API = "http://127.0.0.1:5002/bert-te-from-json"