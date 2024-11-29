import transformers
import torch
import numpy as np

from nltk import sent_tokenize

from utils import divide_chunks

from typing import List

#TODO
# Add device selection; Maybe with accelerate ?
class ClaimExtractor:
    """
     Extract sentence claims from text
    """
    def __init__(self, model_path_name: str, keep_logit_idx: int = 1, conf_thold:float = 0.5):
        """
        :param model_path_name: str, path to pretrained huggingface model or link to it in the huggingface hub.
        :param keep_logit_idx: int, index in the predicted logits by model of the class to keep the sentence as a claim
        """
        self.model = transformers.AutoModelForSequenceClassification.from_pretrained(model_path_name)
        self.model.eval()

        self.tokenizer = transformers.AutoTokenizer.from_pretrained(model_path_name)
        self.keep_logit_idx = keep_logit_idx
        self.conf_thold = conf_thold

    def get_claims(self, text: str, batch_size=8) -> List[str]:
        """
        Extract claims from the input text. The text will be splitted into sentences,
        and for each sentence the prediction if it should be kept will be performed.

        :param text: str, input text tp retrieve claims from
        :param batch_size: int, batch size to use for the alignment model.

        :return:  list of str, extracted claims

        """

        sentences = sent_tokenize(text=text)

        keep_sentences = []

        for batch_sents in divide_chunks(sentences, batch_size):

            batch_preds = self._run_model(batch_sents)
            keep_sentences += [sent for i, sent in enumerate(batch_sents) if batch_preds[i] >= self.conf_thold]

        return keep_sentences

    @torch.no_grad()
    def _run_model(self, batch_sents: List[str]) -> List[float]:
        """
        Run batch through the model.

        :param predict_pairs: list of str, texts to predict
        :return: list of ints, predicted classes for batch inputs
        """

        tokenized_batch_input = self.tokenizer(
            batch_sents,
            return_tensors="pt",
            padding=True,
            max_length=512,
            truncation=True
        )

        preds_output = self.model(**tokenized_batch_input)
        preds_output = torch.softmax(preds_output.logits, dim=1)
        preds_output = preds_output[:,self.keep_logit_idx].detach().cpu().reshape(-1)
        preds_output = preds_output.numpy().tolist()

        # preds_classes = torch.argmax(preds_output.logits, dim=1).detach().cpu().numpy().tolist()

        return preds_output
