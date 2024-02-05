import requests
import tempfile
import json

class AMFComponents:

    """
    API calls to deployed ARG-tech services
    """

    @classmethod
    def _run_8n8_post_request(cls, api_address, text):
        """
        POST request to 8n8 deployed service. The required input is {"file": tempFile}

        :param api_address: str, address of API entry point to use;
        :param text: str, text input. Will be converted to text file
        :return: dict, json request output
        """
        temp = tempfile.TemporaryFile()
        temp.write(bytes(text, "utf-8"))
        temp.seek(0)
        output = requests.post(
            url=api_address,
            files={"file": temp}

        )
        temp.close()
        return output.json()

    @classmethod
    def _run_turninator(cls, api_address, text):
        """
        Run Turninator service. The service takes as an input text and parses it into xAIF format.
        :param api_address: str, address to turninator API point
        :param text: str, input text to convert
        :return: dict, xAIF formatted json
        """
        return cls._run_8n8_post_request(
            api_address=api_address,
            text=text
        )


    @classmethod
    def _run_propositionalizer(cls, api_address, xaif_json):
        """
        Run Propositionalizer. Takes as an input xAIF formatted json
        :param api_address: str, address to Propositionalizer API point
        :param xaif_json: dict, xAIF formatted json to process
        :return: dict, xAIF formatted json
        """
        return cls._run_8n8_post_request(
            api_address=api_address,
            text=json.dumps(xaif_json)
        )

    @classmethod
    def _run_segmenter(cls, api_address, xaif_json):
        """
        Run Segmenter. Takes as an input xAIF formatted json
        :param api_address: str, address to Segmenter API point
        :param xaif_json: dict, xAIF formatted json to process
        :return: dict, xAIF formatted json
        """
        return cls._run_8n8_post_request(
            api_address=api_address,
            text=json.dumps(xaif_json)
        )

    @classmethod
    def _run_relationer(cls, api_address, xaif_json):
        """
        Run Relationer. Takes as an input xAIF formatted json
        :param api_address: str, address to Relationer API point
        :param xaif_json: dict, xAIF formatted json to process
        :return: dict, xAIF formatted json
        """
        return cls._run_8n8_post_request(
            api_address=api_address,
            text=json.dumps(xaif_json)
        )

    @classmethod
    def parse_text_to_xaif(cls,
                           turninator_api,
                           propositionalizer_api,
                           segmenter_api,
                           relationer_api,
                           text
                           ):
        """
        Run API modules in chain on the text to parse text into xAIF formatted json. The output is a parsed argument graph.
        :param turninator_api, propositionalizer_api, segmenter_api, relationer_api:
            str, address to API entry point for the corresponding service

        :param text: str, text to process
        :return: dict, parsed xAIF json
        """

        xaif_json = cls._run_turninator(turninator_api, text)
        prop_xaif_json = cls._run_propositionalizer(propositionalizer_api, xaif_json)
        segm_xaif_json = cls._run_segmenter(segmenter_api, prop_xaif_json)
        relat_xaif_json = cls._run_relationer(relationer_api, segm_xaif_json)
        return relat_xaif_json


if __name__ == '__main__':
    from config import TURNINATOR_API, PROPOSITIONALIZER_API, SEGMENTER_API, RELATIONER_API

    text = "Uruguay welcomes the information provided in the concept paper (S/2016/219, annex), which details the various mechanisms, policies and structures developed in Africa aimed at creating an environment to enable women to play a more significant role in peace and security."
    xaif_json = AMFComponents._run_turninator(TURNINATOR_API, text)
    prop_xaif_json = AMFComponents._run_propositionalizer(PROPOSITIONALIZER_API, xaif_json)
    segm_xaif_json = AMFComponents._run_segmenter(SEGMENTER_API, prop_xaif_json)
    relat_xaif_json = AMFComponents._run_relationer(RELATIONER_API, segm_xaif_json)
    print(relat_xaif_json)