from typing import Dict, Union, List, Any

class RelationClaimExtractor:
    """
    Extract "claims/premises/reasons" from the AIF/xAIF formats.
    The idea is as follows:
        The algorithm will extract all the nodes that are connected with the YA node as its parent.
        (YA -> Node). Only nodes of a type L will be selected. If there is a relationship as:
            (Node -> CA), the node will be dropped, as it is cponsidered to be an argument rather than a claim.
    """

    @classmethod
    def _get_meta_nodes_dict(cls, aif_json: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        """
        Construct a meta json for the unique nodes for convenience.

        :param aif_json: AIF formatted json, with the key "nodes"
        :return: --dict:
            {
                node_id: {dict from the input file that contains info about the node}
            }

            Example:
            {
             'nodeID': '511074',
             'text': 'Our schools are really unsafe due to gun laws',
             'timestamp': '2020-05-28 19:24:33',
             'type': 'I'
             }
        """

        node_meta_dict = {}
        for node_dict in aif_json["nodes"]:
            node_meta_dict[node_dict["nodeID"]] = node_dict

        return node_meta_dict

    @classmethod
    def get_claim_nodes_xaif(cls, xaif_json: Dict[str, Any]) -> List[Dict[str, str]]:
        """Run extraction on xAIF format. Input is a dict with the key "AIF" that has AIF formatted json.
        For output, see get_claim_nodes_aif"""
        return cls.get_claim_nodes_aif(aif_json=xaif_json["AIF"])

    @classmethod
    def get_claim_texts_aif(cls, aif_json: Dict[str, Any]) -> List[str]:
        """
        Retrieve claims from AIF data sample

        :param aif_json: dict, AIF formatted dict.
        :return: list of str, texts of retrieved claims
        """
        nodes_dicts = cls.get_claim_nodes_aif(aif_json=aif_json)
        claims_texts = [node_dict["text"] for node_dict in nodes_dicts]
        return claims_texts

    @classmethod
    def get_claim_texts_xaif(cls, xaif_json: Dict[str, Any]) -> List[str]:
        """
        Retrieve claims from xAIF data sample.
        Input: xAIF data sample. Should have key "AIF" with AIF dict attached to it.
        return: see get_claim_texts_aif
        """
        nodes_dicts = cls.get_claim_nodes_xaif(xaif_json=xaif_json)
        claims_texts = [node_dict["text"] for node_dict in nodes_dicts]
        return claims_texts

    @classmethod
    def get_claim_nodes_aif(cls, aif_json: Dict[str, Any]) -> List[Dict[str, str]]:
        """

        :param aif_json:
        :return:
        """
        keep_nodes = []

        node_meta_dict = cls._get_meta_nodes_dict(aif_json)

        # getting all nodes that are children of YA nodes
        for edge in aif_json["edges"]:
            if node_meta_dict[edge["fromID"]]["type"] == "YA":
                if edge["toID"] in node_meta_dict:
                    if node_meta_dict[edge["toID"]]["type"] == "I":
                        if edge["toID"] not in keep_nodes:
                            keep_nodes.append(edge["toID"])

        # filtering nodes, removing children of CA
        for node in keep_nodes:
            for edge in aif_json["edges"]:
                if node_meta_dict[edge["toID"]]["type"] == "CA":
                    if node in keep_nodes:
                        keep_nodes.remove(node)
                        break

        return [node_meta_dict[node] for node in keep_nodes]