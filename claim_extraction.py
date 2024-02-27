from typing import Dict, Union, List, Any, Tuple

class RelationClaimExtractor:
    """
    Extract "claims/premises/reasons" from the AIF/xAIF formats.
    The idea is as follows:
        The algorithm will extract all the nodes that are connected with the YA node as its parent.
        (YA -> Node), YA node "text" should be "Asserting", otherwise it will not be kept.
         Only nodes of a type L will be selected.
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
    def get_claim_nodes_xaif(cls,
                             xaif_json: Dict[str, Any],
                             keep_ya_nodes_texts: List[str] = []
                             ) -> List[Dict[str, str]]:
        """Run extraction on xAIF format. Input is a dict with the key "AIF" that has AIF formatted json.
        For output, see get_claim_nodes_aif"""
        return cls.get_claim_nodes_aif(
            aif_json=xaif_json["AIF"],
            keep_ya_nodes_texts=keep_ya_nodes_texts
        )

    @classmethod
    def get_claim_texts_aif(cls,
                            aif_json: Dict[str, Any],
                            keep_ya_nodes_texts: List[str] = []
                            ) -> List[str]:
        """
        Retrieve claims from AIF data sample

        :param aif_json: dict, AIF formatted dict.
        :return: list of str, texts of retrieved claims
        """
        nodes_dicts, structure_claims_graph = cls.get_claim_nodes_aif(
            aif_json=aif_json,
            keep_ya_nodes_texts=keep_ya_nodes_texts
        )
        claim_texts = [x["text"] for x in nodes_dicts]
        return claim_texts

    @classmethod
    def get_claim_texts_xaif(cls,
                             xaif_json: Dict[str, Any],
                             keep_ya_nodes_texts: List[str] = []
                             ) -> List[str]:
        """
        Retrieve claims from xAIF data sample.
        Input: xAIF data sample. Should have key "AIF" with AIF dict attached to it.
        return: see get_claim_texts_aif
        """
        nodes_dicts, structure_claims_graph = cls.get_claim_nodes_xaif(
            xaif_json=xaif_json,
            keep_ya_nodes_texts=keep_ya_nodes_texts
        )
        texts = [x["text"] for x in nodes_dicts]
        return texts

    @classmethod
    def get_claim_nodes_aif(cls, aif_json: Dict[str, Any],
                            keep_ya_nodes_texts: List[str] = []
                            ) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
        """

        :param aif_json:
        :return:
        """
        keep_nodes_ids = []

        node_meta_dict = cls._get_meta_nodes_dict(aif_json)

        # getting all nodes that are children of YA nodes
        for edge in aif_json["edges"]:
            if node_meta_dict[edge["fromID"]]["type"] == "YA":


                if keep_ya_nodes_texts:
                    if node_meta_dict[edge["fromID"]]["text"] in keep_ya_nodes_texts:
                        if edge["toID"] in node_meta_dict:
                            if node_meta_dict[edge["toID"]]["type"] == "I":
                                if edge["toID"] not in keep_nodes_ids:
                                    keep_nodes_ids.append(
                                        edge["toID"]
                                    )
                else:
                    if edge["toID"] in node_meta_dict:
                        if node_meta_dict[edge["toID"]]["type"] == "I":
                            if edge["toID"] not in keep_nodes_ids:
                                keep_nodes_ids.append(
                                    edge["toID"]
                                )

        keep_nodes_meta_dicts = [node_meta_dict[node_id] for node_id in keep_nodes_ids]


        structure_claims_graph = cls.retrieve_edges_from_claim_nodes(
            node_meta_dict=node_meta_dict,
            aif_json=aif_json,
            claim_nodes=keep_nodes_meta_dicts
        )

        # filtering nodes, removing children of CA
        # for node in keep_nodes:
        #     for edge in aif_json["edges"]:
        #         if node_meta_dict[edge["toID"]]["type"] == "CA":
        #             if node in keep_nodes:
        #                 keep_nodes.remove(node)
        #                 break

        return keep_nodes_meta_dicts, structure_claims_graph

    @classmethod
    def get_node_parents_edges(cls,
                               node_id: str,
                               edges: List[Dict[str, Any]]
                               ) -> List[Dict[str, Any]]:
        parents = []
        for edge in edges:
            if edge["toID"] == node_id:
                parents.append(edge)
        return parents

    @classmethod
    def retrieve_edges_from_claim_nodes(cls,
                                            node_meta_dict: Dict[str, Dict[str, Union[str, int, float]]],
                                            aif_json: Dict[str, Any],
                                            claim_nodes: List[Dict[str, Union[str, int, float]]]
                                        ) -> List[Dict[str, Any]]:

        claims_node_ids = [node["nodeID"] for node in claim_nodes]
        kept_relation_edges = []

        # I1 -> YA/CA -> I2 (parse in a way from I2 to I1)
        for edge in aif_json["edges"]:
            if edge["toID"] in claims_node_ids and node_meta_dict[edge["fromID"]]["type"] in ["YA", "CA"]:

                edge_parents = cls.get_node_parents_edges(edge["fromID"], aif_json["edges"])
                edge_parents = [parent_edge for parent_edge in edge_parents if parent_edge["fromID"] in claims_node_ids]

                kept_relation_edges += [
                    {
                        "fromID": parent_edge["fromID"],
                        "toID": edge["toID"],
                        "relation": node_meta_dict[edge["fromID"]]["text"]
                    } for parent_edge in edge_parents
                ]
        return kept_relation_edges

if __name__ == '__main__':
    import json
    data = json.load(
        open("examples/aif_graph.json", "r")
    )


    claim_nodes_dicts, structure_claims_graph = RelationClaimExtractor.get_claim_nodes_aif(
        data
    )
    with open(
        "output.json", "w"
    ) as f:
        json.dump(
            {
                "hypothesis": [x["text"] for x in claim_nodes_dicts],
                "hypothesis_nodes": claim_nodes_dicts,
                "structure_hypothesis_graph": structure_claims_graph
            }, f
        )
