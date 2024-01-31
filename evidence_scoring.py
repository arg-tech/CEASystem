from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from utils import divide_chunks

import numpy as np

class AlignmentMatrixFiltering:

    @classmethod
    def filter_binary_evidences(cls, alignment_matrix, min_alignment_limit, max_alignment_limit):

        # process default values
        if min_alignment_limit == -1:
            max_alignment_limit = alignment_matrix.shape[1] + 1
        if max_alignment_limit == -1:
            min_alignment_limit = 0

        avg_alignment_matrix = alignment_matrix.sum(axis=0)
        keep_ids, drop_idx = [], []
        for i, avg_value in enumerate(avg_alignment_matrix):
            if avg_value >= max_alignment_limit or avg_value <= min_alignment_limit:
                drop_idx.append(i)
            else:
                keep_ids.append(i)

        return alignment_matrix[:,keep_ids], drop_idx

class AlignmentMarixFilteringScoring:
    def __init__(self,
                 mnli_model_name_path,
                 model_label_decoder
                 ):


        self.mnli_model = AutoModelForSequenceClassification.from_pretrained(mnli_model_name_path)
        self.mnli_tokenizer = AutoTokenizer.from_pretrained(mnli_model_name_path)
        self.model_label_decoder = model_label_decoder

    @torch.no_grad()
    def _predict_mnli_logits(self, hypothesises, evidences):
        input = self.mnli_tokenizer(hypothesises, evidences, padding=True, truncation=True, return_tensors="pt")
        output = self.mnli_model(input["input_ids"])

        logits = torch.softmax(output.logits, dim=1)
        logits = logits.detach().cpu().numpy()

        # get only entailment and contradiction
        entailment_logits = logits[:, self.model_label_decoder["entailment"]].reshape(-1)
        contradiction_logits = logits[:, self.model_label_decoder["contradiction"]].reshape(-1)

        # select a final score with + or - sign
        final_preds = []
        for entailment_logit, contradiction_logit in zip(entailment_logits, contradiction_logits):
            if entailment_logit > contradiction_logit:
                final_preds.append(entailment_logit)
            else:
                final_preds.append(-contradiction_logit)


        return final_preds


    def score_filter_matrix(self, alignment_matrix,
                            evidence_texts, hypothesis_texts,
                            min_alignment_limit,
                            max_alignment_limit,
                            batch_size=8):

        binary_filtered_alignment_matrix, binary_drop_idx = AlignmentMatrixFiltering.filter_binary_evidences(
            alignment_matrix=alignment_matrix,
            min_alignment_limit=min_alignment_limit,
            max_alignment_limit=max_alignment_limit
        )
        binary_filtered_evidence_texts = [
            evidence for i, evidence in enumerate(evidence_texts) if i not in binary_drop_idx
        ]
        dropped_evidence_texts = [
            evidence for i, evidence in enumerate(evidence_texts) if i in binary_drop_idx
        ]

        # selecting hypothesises and evidence that require scoring
        scoring_matrix = binary_filtered_alignment_matrix.copy()
        rows_ids, cols_ids = np.where(binary_filtered_alignment_matrix == 1)

        for batch_chunk_ids in divide_chunks(list(range(len(rows_ids))), batch_size):
            batch_row_ids = [rows_ids[i] for i in batch_chunk_ids]
            batch_col_ids = [cols_ids[i] for i in batch_chunk_ids]

            batch_hypothesis_texts = [
                hypothesis_texts[i] for i in batch_row_ids
            ]
            batch_evidence_texts = [
                binary_filtered_evidence_texts[i] for i in batch_col_ids
            ]

            signed_scores = self._predict_mnli_logits(
                hypothesises=batch_hypothesis_texts,
                evidences=batch_evidence_texts
            )
            scoring_matrix[batch_row_ids, batch_col_ids] = signed_scores

        return {
            "scoring_matrix": scoring_matrix.tolist(),
            "filtered_evidences": binary_filtered_evidence_texts,
            "hypothesis_texts": hypothesis_texts,
            "dropped_evidences": dropped_evidence_texts,
        }


if __name__ == '__main__':
    from evidence_alignment import EvidenceAligner
    model_path = "roberta-EvidenceAlignment-tuned-model"

    aligner = EvidenceAligner(model_path)

    test_hypothesis = [
        "Climate change is not influenced by human activities",
        "Eating chocolate every day is good for your health"
    ]

    test_evidences = [
        "natural factors can influence climate",
        "the current warming trend is largely attributed to human activities",
        "the burning of fossil fuels and deforestation cause climate change",
        "The financial crisis of 1929 was caused by too much cash in my pocket",
        "A balanced diet with a variety of nutrients is more beneficial for overall health",
        "Excessive consumption of chocolate, especially with added sugars, can contribute to health problems",
        "dogs can bark"
    ]

    alignment_matrix = aligner.predict(
        hypothesises=test_hypothesis,
        evidences=test_evidences,
        batch_size=4
    )

    scorer = AlignmentMarixFilteringScoring(
        mnli_model_name_path="roberta-large-mnli",
        model_label_decoder={"entailment": 2, "contradiction": 0},
        min_alignment_percent=0.1,
        max_alignment_percent=0.8
    )

    scored_dict = scorer.score_filter_matrix(
        alignment_matrix=alignment_matrix,
        evidence_texts=test_evidences,
        hypothesis_texts=test_hypothesis,
        batch_size=4
    )
    print(scored_dict)

