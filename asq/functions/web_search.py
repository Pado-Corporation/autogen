import requests
from asq import config, logger
import logging

_endpoint = config.bing_search_endpoint + "/v7.0/search"
_headers = {"Ocp-Apim-Subscription-Key": config.openai_api_key}


def web_search(query: str, mkt: str = "en-US"):
    params = {"q": query, "mkt": mkt}

    try:
        response = requests.get(_endpoint, headers=_headers, params=params)
        response.raise_for_status()

        logger.log(logging.INFO, "Web search complete.")

        return response.json()
    except requests.HTTPError:
        return {"webPages": {"value": None}}
