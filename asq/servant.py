from typing import Callable, Dict, Optional, Union
from autogen import ConversableAgent


class Servant(ConversableAgent):
    def __init__(
        self,
        name: Optional[str] = "Slave",
        system_message: str | None = "You are a helpful AI Assistant.",
        is_termination_msg: Callable[[Dict], bool] | None = None,
        max_consecutive_auto_reply: int | None = None,
        human_input_mode: str | None = "TERMINATE",
        function_map: Dict[str, Callable[..., Any]] | None = None,
        code_execution_config: Dict | bool | None = None,
        llm_config: Dict | bool | None = None,
        default_auto_reply: str | Dict | None = "",
    ):
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
