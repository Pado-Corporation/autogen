from typing import Callable, Dict, Optional, Any
from autogen import ConversableAgent
import re


def to_snake_case(s):
    # Turn CamelCase into snake_case
    s = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", s)
    # Do the same for capital letters in the middle of a word
    s = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s)
    # Replace spaces and convert to lowercase
    return s.replace(" ", "_").lower()


class Servant(ConversableAgent):
    def __init__(
        self,
        name: Optional[str] = "Servant",
        is_termination_msg: Callable[[Dict], bool] | None = None,
        max_consecutive_auto_reply: int | None = None,
        human_input_mode: str | None = "TERMINATE",
        function_map: Dict[str, Callable[..., Any]] | None = None,
        code_execution_config: Dict | bool | None = None,
        llm_config: Dict
        | bool
        | None = {
            "temperature": 0,
            "request_timeout": 600,
        },
        default_auto_reply: str | Dict | None = "",
        responsibility: str = "",
        bg_knowledge: str = "",
        goal: str = "",
        format: str = "",
    ):
        self.responsibility = responsibility
        self.bg_knowledge = bg_knowledge
        self.goal = goal
        self.format = format
        system_message = f"""You are {name}.
You are responsible for: {responsibility}
About the user: {bg_knowledge}
"""
        name = to_snake_case(name)

        super().__init__(
            name,
            system_message,
            is_termination_msg,
            max_consecutive_auto_reply,
            human_input_mode,
            function_map,
            code_execution_config,
            llm_config,
            default_auto_reply,
        )

    def __repr__(self) -> str:
        return f"[{self.name}]\n{self.system_message}"
