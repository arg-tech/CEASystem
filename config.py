# ALIGNMENT CONFIG VARIABLES
ALIGNER_MODEL_PATH = "roberta-EvidenceAlignment-tuned-model"
ALIGNER_BATCH_SIZE = 6

# SCORING CONFIG VARIABLES
MNLI_SCORING_MODEL = "roberta-large-mnli"
MNLI_MODEL_LABEL_DECODER = {"entailment": 2, "contradiction": 0}
SCORER_BATCH_SIZE = 6

# API addresses
TURNINATOR_API = "http://amf2.arg.tech/turninator-01"
PROPOSITIONALIZER_API = "http://amf2.arg.tech/propositionUnitizer-01"
SEGMENTER_API = "http://amf2.arg.tech/segmenter-01"
RELATIONER_API = "http://amf2.arg.tech/bert-te"