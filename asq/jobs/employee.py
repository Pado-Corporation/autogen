from typing import Callable, Dict, Optional, Union, List
from asq.functions import web_search
from autogen import AssistantAgent
from asq import config

try:
    from termcolor import colored
except ImportError:

    def colored(x, *args, **kwargs):
        return x


DEFAULT_DESCRIPTION = """You are a helpful AI employee that uses various tools to get things done.
"""
DEFAULT_ABILITY: Dict[str, Callable] = {"web_search": web_search}
DEFAULT_FUNCTIONS: List[Dict] = [
    {
        "name": "web_search",
        "description": "Sends a search query to Bing and gets back search results that include links to webpages, images, and more.",
        "parameters": {
            "type": "object",
            "properties": {
                "search_term": {
                    "type": "string",
                    "description": "The search query term. The term may not be empty.",
                },
                "mkt": {
                    "type": "string",
                    "description": "The market where the results come from. Typically, mkt is the country where the user is making the request from. However, it could be a different country if the user is not located in a country where Bing delivers results. The market must be in the form <language>-<country/region>. For example, en-US. The string is case insensitive.",
                },
            },
            "required": ["query"],
        },
    },
]

DEFAULT_CONFIG = {"model": config.fast_model, "config_list": config.models_list}


class Employee(AssistantAgent):
    def __init__(
        self,
        job_title: str,
        responsibility: str,
        dependency: str,
        bg_knowledge: str,
        response_format: str,
        job_description: str | None = DEFAULT_DESCRIPTION,
        is_termination_msg: Callable[[Dict], bool] | None = None,
        max_consecutive_auto_reply: int | None = None,
        human_input_mode: str | None = "NEVER",
        function_map: Optional[Dict[str, Callable]] = DEFAULT_ABILITY,
        llm_config: Dict | bool | None = DEFAULT_CONFIG,
        **kwargs,
    ):
        """The Employee agent is designed to autonomously execute tasks based on its role. Then, respond in a fixed format.

        Args:
            name (str): Job title
            system_message (str | None, optional): Job description. Defaults to DEFAULT_DESCRIPTION.
            is_termination_msg (Callable[[Dict], bool] | None, optional): _description_. Defaults to None.
            max_consecutive_auto_reply (int | None, optional): _description_. Defaults to None.
            human_input_mode (str | None, optional): _description_. Defaults to "NEVER".
            function_map (Optional[Dict[str, Callable]], optional): Ability. Defaults to DEFAULT_ABILITY.
            llm_config (Dict | bool | None, optional): _description_. Defaults to DEFAULT_CONFIG.
        """
        job_description = f"""You are a {job_title}.  Do your duty to help the user reach the goal based on the information. When receiving feedbacks from the King assistant, reflect on the feedbacks and generate a new response.

Your responsibility: {responsibility}
Dependent to these assistants: {dependency}
Background knowledge about the user: {bg_knowledge}

Always respond in this format: {response_format}
"""
        super().__init__(
            job_title,
            llm_config,
            is_termination_msg,
            max_consecutive_auto_reply,
            human_input_mode,
            function_map,
            system_message=job_description,
            **kwargs,
        )
