from pydantic import BaseModel
from typing import Dict, Any, List

import numpy as np

# Decorator to output result in the specific format
def return_error_codes():
  def decorate(f):
    def applicator(*args, **kwargs):
      try:
         return f(*args,**kwargs)
      except Exception as e:

         return {"code": 400, "output":  {"Error": str(e)}}

    return applicator

  return decorate


def prepare_output(ordered_decision_scores_dict, scoring_matrix,
                   hypothesis, kept_evidences, dropped_evidences,
                   hypothesis_nodes, structure_hypothesis_graph):
    """
    Format output in a suitable format.

    :param ordered_decision_scores_dict: dict, result of decision_making.DecisionDistributionMaker:
        {
            "order_ids": list/array of ints, id of "hypothesis" to the score from "scores".
            "scores": list/array of floats, scores decision per hypothesis.
        }

    :param scoring_matrix: list of lists/array/matrix. Matrix of claim-evidence scores. Claims are rows, evidences are cols.
        This matrix should include only "kept_evidences" and all the claims. The order of rows and cols should be the same as "ordered_hypothesises" and "kept_evidences"
    :param hypothesis: list of str, claims that the decision was made for.
    :param kept_evidences: list of str, ordered list of evidences that were considered in scoring_matrix. Order should be the same as corresponding order of rows in "scoring_matrix"
    :param dropped_evidences: list of str, evidences that were not used during the analysis due to the filtering
    :return: dict, formatted output in the format in AnalyzedOutput
    """
    request_output_dict = {}
    request_output_dict["ordered_hypothesises"] = [hypothesis[i] for i in ordered_decision_scores_dict["order_ids"]]
    request_output_dict["ordered_hypothesises_nodeids"] = [hypothesis_nodes[i] for i in ordered_decision_scores_dict["order_ids"]]
    request_output_dict["ordered_hypothesises_scores"] = [round(x, 3) for x in ordered_decision_scores_dict["scores"]]

    request_output_dict["filtered_scoring_matrix"] = np.array(scoring_matrix).round(3)[ordered_decision_scores_dict["order_ids"],:]
    request_output_dict["filtered_scoring_matrix"] = request_output_dict["filtered_scoring_matrix"].round(3).tolist()

    request_output_dict["kept_evidences"] = kept_evidences
    request_output_dict["dropped_evidences"] = dropped_evidences

    # adding dropped evidences to the matrix
    request_output_dict["full_scoring_matrix"] = request_output_dict["filtered_scoring_matrix"].copy()
    request_output_dict["full_scoring_matrix"] = np.hstack(
        [
            request_output_dict["full_scoring_matrix"],
            np.full(shape=(len(request_output_dict["filtered_scoring_matrix"]), len(request_output_dict["dropped_evidences"])), fill_value=-1000.0)
         ]
    ).round(3).tolist()
    request_output_dict["full_ordered_evidences"] = request_output_dict["kept_evidences"] + request_output_dict["dropped_evidences"]

    request_output_dict["structure_hypothesis_graph"] = structure_hypothesis_graph

    return request_output_dict

class RawTextInput(BaseModel):
    text: str

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "text": "Some experts believe that Climate change is happening. There are plenty of reasons for it, but the most popular opinion is that governments are really slow, when it comes to reaction to the climate change. Other people claim that renewable energy is a scam that should be stopped.",
            }]
        }
    }

class ParsedTextOutput(BaseModel):
    code: int
    output: Dict[str, Any]

    class Config:
        model_config = {
            "json_schema_extra": {
                "examples": [{
                "code": 200,
                "output":  {
                    "hypothesis": [
                        "Climate change is happening",
                        "governments are really slow, when it comes to reaction to the climate change",
                        "renewable energy is a scam"
                    ],
                    "hypothesis_nodes": [
                        {
                            "nodeID": "1",
                            "text": "Climate change is happening",
                            "type": "I",
                            "timestamp": "2020-05-28 19:24:34"
                        },
                        {
                            "nodeID": "2",
                            "text": "governments are really slow, when it comes to reaction to the climate change",
                            "type": "I",
                            "timestamp": "2020-05-28 19:24:31"
                        },
                        {
                            "nodeID": "3",
                            "text": "renewable energy is a scam",
                            "type": "I",
                            "timestamp": "2020-05-28 19:24:35"
                        }
                    ],
                    "structure_hypothesis_graph": [
                        {
                            "fromID": "2",
                            "toID": "1",
                            "relation": "Asserting"
                        },
                        {
                            "fromID": "1",
                            "toID": "3",
                            "relation": "Contradiction"
                        }
                    ]
                }
            }]
        }}



class ClaimsEvidenceInput(BaseModel):
    hypothesis: List[str]
    manual_evidences: List[str]
    hypothesis_nodes: List[Dict[str, str]]
    structure_hypothesis_graph: List[Dict[str, str]]
    min_alignment_limit: int
    max_alignment_limit: int


    model_config = {
        "json_schema_extra": {
            "examples": [{
                "min_alignment_limit": -1,
                "max_alignment_limit": -1,
                "hypothesis": [
                    "Climate change is happening",
                    "governments are really slow, when it comes to reaction to the climate change",
                    "renewable energy is a scam"
                ],
                "manual_evidences": [
                    "renewable energy sector generats plenty of jobs according to me",
                    "the coal industry provides a lot of jobs as well",
                    "there are a lot of money in wind, hydro electricity, solar panels to be made, with the benefits to humanity",
                    "The level is rising for the last 3 decades, studies show",
                    "The ocean level did not rise significantly",
                    "Some countries deploy very strict regulations to the gas companies",
                    "The limits are set for the amount of waste every country could emit",
                    "Some countries are very slow to higher their ecology standards",
                    "The amount of lifestock is getting bigger every year",
                    "The President of the United States uses his plane very oftenly during his term",
                    "The wind stations are on a rise",
                    "The hydro stations do not provide enough electricity even for a small town of 1000 people",
                    "The earth is not flat, but it is shaped as a banana",
                    "Ipod was made from execcive amount of plastic"
                ],
                "hypothesis_nodes": [
                    {
                        "nodeID": "1",
                        "text": "Climate change is happening",
                        "type": "I",
                        "timestamp": "2020-05-28 19:24:34"
                    },
                    {
                        "nodeID": "2",
                        "text": "governments are really slow, when it comes to reaction to the climate change",
                        "type": "I",
                        "timestamp": "2020-05-28 19:24:31"
                    },
                    {
                        "nodeID": "3",
                        "text": "renewable energy is a scam",
                        "type": "I",
                        "timestamp": "2020-05-28 19:24:35"
                    }
                ],
                "structure_hypothesis_graph": [
                    {
                        "fromID": "2",
                        "toID": "1",
                        "relation": "Asserting"
                    },
                    {
                        "fromID": "1",
                        "toID": "3",
                        "relation": "Contradiction"
                    }
                ]
            }]
        }}

class AnalyzedOutput(BaseModel):

    code: int
    output: Dict[str, Any]

    model_config = {
        "json_schema_extra": {
            "examples": [{
                    "code": 200,
                    "output": {
                        'dropped_evidences': [
                            'the coal industry provides a lot of jobs as well',
                            'The level is rising for the last 3 decades, studies show',
                            'The ocean level did not rise significantly',
                            'The limits are set for the amount of waste every country could emit',
                            'The amount of lifestock is getting bigger every year',
                            'The President of the United States uses his plane very oftenly during his term',
                            'The wind stations are on a rise',
                            'The hydro stations do not provide enough electricity even for a small town of 1000 people',
                            'The earth is not flat, but it is shaped as a banana',
                            'Ipod was made from execcive amount of plastic'
                        ],
                        'filtered_scoring_matrix': [
                                [0.0, 0.0, -0.139, 0.341],
                                [-0.834, -0.652, 0.0, 0.0],
                                [0.0, 0.0, 0.0, 0.0]
                            ],
                        'full_ordered_evidences': [
                            'renewable energy sector generates plenty of jobs according to me',
                            'there are a lot of money in wind, hydro electricity, solar panels to be made, with the benefits to humanity',
                            'Some countries deploy very strict regulations to the gas companies',
                            'Some countries are very slow to higher their ecology standards',
                            'the coal industry provides a lot of jobs as well',
                            'The level is rising for the last 3 decades, studies show',
                            'The ocean level did not rise significantly',
                            'The limits are set for the amount of waste every country could emit',
                            'The amount of lifestock is getting bigger every year',
                            'The President of the United States uses his plane very oftenly during his term',
                            'The wind stations are on a rise',
                            'The hydro stations do not provide '
                            'enough electricity even for a small town of 1000 people',
                            'The earth is not flat, but it is shaped as a banana',
                            'Ipod was made from execcive amount of plastic'
                        ],
                        'full_scoring_matrix': [
                                [0.0, 0.0,  -0.139, 0.341, -1000.0, -1000.0, -1000.0, -1000.0, -1000.0, -1000.0, -1000.0, -1000.0,-1000.0, -1000.0],
                                [-0.834, -0.652, 0.0, 0.0, -1000.0, -1000.0, -1000.0, -1000.0, -1000.0, -1000.0, -1000.0, -1000.0, -1000.0, -1000.0],
                                [0.0, 0.0, 0.0, 0.0, -1000.0, -1000.0, -1000.0, -1000.0, -1000.0, -1000.0, -1000.0, -1000.0, -1000.0, -1000.0]
                            ],
                        'kept_evidences': [
                            'renewable energy sector generats plenty of jobs according to me',
                            'there are a lot of money in wind, hydro electricity, solar panels to be made, with the benefits to humanity',
                            'Some countries deploy very strict regulations to the gas companies',
                            'Some countries are very slow to higher their ecology standards'
                        ],
                        'ordered_hypothesises': [
                            'governments are really slow, when it comes to reaction to the climate change',
                            'renewable energy is a scam',
                            'Climate change is happening'
                        ],
                        'ordered_hypothesises_scores': [-1.000, -0.742, 0.112],
                        "ordered_hypothesises_nodeids": [
                            {
                                "nodeID": "2",
                                "text": "governments are really slow, when it comes to reaction to the climate change",
                                "type": "I",
                                "timestamp": "2020-05-28 19:24:31"
                            },
                            {
                                "nodeID": "3",
                                "text": "renewable energy is a scam",
                                "type": "I",
                                "timestamp": "2020-05-28 19:24:35"
                            },
                            {
                                "nodeID": "1",
                                "text": "Climate change is happening",
                                "type": "I",
                                "timestamp": "2020-05-28 19:24:34"
                            }
                        ],
                        "structure_hypothesis_graph": [
                            {
                                "fromID": "2",
                                "toID": "1",
                                "relation": "Asserting"
                            },
                            {
                                "fromID": "1",
                                "toID": "3",
                                "relation": "Contradiction"
                            }
                        ]
                    }
                }]
            }}