from typing import Callable, Dict, Optional, Union
from autogen import AssistantAgent


class Employee(AssistantAgent):
    def __init__(
        self,
        name: str,
        system_message: str | None = ...,
        llm_config: Dict | bool | None = None,
        is_termination_msg: Callable[[Dict], bool] | None = None,
        max_consecutive_auto_reply: int | None = None,
        human_input_mode: str | None = "NEVER",
        code_execution_config: Dict | bool | None = False,
        **kwargs
    ):
        super().__init__(
            name,
            system_message,
            llm_config,
            is_termination_msg,
            max_consecutive_auto_reply,
            human_input_mode,
            code_execution_config,
            **kwargs
        )
