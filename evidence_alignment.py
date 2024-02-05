import transformers
import torch
import numpy as np

from utils import divide_chunks

#TODO
# Add device selection; Maybe with accelerate ?
class EvidenceAligner:
    """
    Predictor of alignment of claims and evidences (which evidence is relevant to which claim)
    """
    def __init__(self, model_path_name):
        """
        :param model_path_name: str, path to pretrained huggingface model or link to it in the huggingface hub.
        """
        self.model = transformers.AutoModelForSequenceClassification.from_pretrained(model_path_name)
        self.model.eval()

        self.tokenizer = transformers.AutoTokenizer.from_pretrained(model_path_name)

    def predict(self, hypothesises, evidences, batch_size=8):
        """
        Predicting alignment of hypothesis and evidences.
        Produces a binary matrix of shape (num hypothesis, num claims). 1 means alignment (evidence is relevant hypothesis); 0 - not relevant
        :param hypothesises, evidences: list of str, hypothesis and evidences to align respectively.
        :param batch_size: int, batch size to use for the alignment model.

        :return numpy.array, binary alignment matrix.

        """
        alignment_matrix = np.zeros((
            len(hypothesises), len(evidences)
        ))

        index_pairs = [(i,j) for i in range(len(hypothesises)) for j in range(len(evidences))]

        for batch_indexes in divide_chunks(index_pairs, batch_size):
            batch_pairs_predict = [
                [hypothesises[idx[0]], evidences[idx[1]]] for idx in batch_indexes
            ]
            preds = self._predict_alignment(batch_pairs_predict)

            rows_ids, cols_ids = zip(*batch_indexes)
            alignment_matrix[rows_ids, cols_ids] = preds

        return alignment_matrix

    @torch.no_grad()
    def _predict_alignment(self, predict_pairs):
        """
        Run batch through the model.

        :param predict_pairs: list of list pf str, pairs of (claim, evidence):
            [(claim, evidence), (claim, evidence), (claim, evidence)....]
        :return: list of ints, predicted classes for batch inputs
        """

        tokenized_batch_input = self.tokenizer.batch_encode_plus(
            predict_pairs,
            return_tensors="pt",
            padding=True,
            truncation=True
        )

        preds_output = self.model(**tokenized_batch_input)
        preds_classes = torch.argmax(preds_output.logits, dim=1).detach().cpu().numpy().tolist()

        return preds_classes


if __name__ == '__main__':
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

    preds = aligner.predict(
        hypothesises=test_hypothesis,
        evidences=test_evidences,
        batch_size=4
    )


    print(preds.shape, preds.mean(axis=0).shape)
    print(preds)
