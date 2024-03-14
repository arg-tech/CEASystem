import transformers
import torch
import numpy as np

from utils import divide_chunks

from typing import List, Any, Dict, Tuple, Union


class ClaimWorthiness:
    """
    Predictor of alignment of claims and evidences (which evidence is relevant to which claim)
    """
    def __init__(self, model_path_name, label2id, confidence_thold=0.0):
        """
        :param model_path_name: str, path to pretrained huggingface model or link to it in the huggingface hub.
        """
        self.model = transformers.AutoModelForSequenceClassification.from_pretrained(model_path_name)
        self.model.eval()

        self.tokenizer = transformers.AutoTokenizer.from_pretrained(model_path_name)
        self.label2id = label2id
        self.confidence_thold = confidence_thold

    def predict(self,
                claim_nodes_dicts: List[Dict[str, Any]],
                structure_claims_graph: List[Dict[str, Union[str ,int]]],
                batch_size: int = 8) -> Tuple[List[Dict[str, Any]], List[Dict[str, Union[str ,int]]]]:

        nodes_decisions = []

        nodes_idx = list(range(len(claim_nodes_dicts)))
        texts = np.array([node_meta["text"] for node_meta in claim_nodes_dicts])

        for batch_idx in divide_chunks(nodes_idx, batch_size):

            batch_texts = texts[batch_idx].tolist()

            batch_preds = self._predict_worthiness(batch_texts)
            nodes_decisions += batch_preds

        filter_claim_nodes_dicts = [node_dict for node_dict, is_worthy in zip(claim_nodes_dicts, nodes_decisions) if is_worthy == "YES"]

        filtered_structure_claims_graph = self.filter_structure_claims_graph(
            structure_claims_graph=structure_claims_graph,
            keep_nodes=[node["nodeID"] for node in filter_claim_nodes_dicts]
        )


        return filter_claim_nodes_dicts, filtered_structure_claims_graph

    def filter_structure_claims_graph(self,
                                        structure_claims_graph: List[Dict[str, Union[str ,int]]],
                                        keep_nodes: List[Union[str ,int]]
                                        ) -> List[Dict[str, Union[str ,int]]]:
        filtered_structure_claims_graph = [
            structure_dict for structure_dict in structure_claims_graph if
            structure_dict["fromID"] in keep_nodes and structure_dict["toID"] in keep_nodes
        ]
        return filtered_structure_claims_graph


    @torch.no_grad()
    def _predict_worthiness(self, texts: List[str]) -> List[str]:
        """
        Run batch through the model.

        :param predict_pairs: list of list pf str, pairs of (claim, evidence):
            [(claim, evidence), (claim, evidence), (claim, evidence)....]
        :return: list of ints, predicted classes for batch inputs
        """

        tokenized_batch_input = self.tokenizer.batch_encode_plus(
            texts,
            return_tensors="pt",
            padding=True,
            truncation=True
        )

        preds_output = self.model(**tokenized_batch_input)
        preds_logits = torch.softmax(preds_output.logits, dim=-1)

        preds_classes = torch.argmax(preds_logits, dim=1).detach().cpu().numpy().tolist()

        preds_classes_names = [self.label2id[pred_class_id] if max(preds_logits[i]) >= self.confidence_thold else "NO" for i, pred_class_id in enumerate(preds_classes)]

        return preds_classes_names
