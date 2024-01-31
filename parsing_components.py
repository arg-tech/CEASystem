import requests
import tempfile
import json

class AMFComponents:

    @classmethod
    def _run_8n8_post_request(cls, api_address, text):
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
        return cls._run_8n8_post_request(
            api_address=api_address,
            text=text
        )


    @classmethod
    def _run_propositionalizer(cls, api_address, xaif_json):
        return cls._run_8n8_post_request(
            api_address=api_address,
            text=json.dumps(xaif_json)
        )

    @classmethod
    def _run_segmenter(cls, api_address, xaif_json):
        return cls._run_8n8_post_request(
            api_address=api_address,
            text=json.dumps(xaif_json)
        )

    @classmethod
    def _run_relationer(cls, api_address, xaif_json):
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