from typing import Callable, Dict, Optional
from autogen import UserProxyAgent


class King(UserProxyAgent):
    """King manages the Slaves for the human user"""

    def __init__(
        self,
        name: Optional[str] = "Prometheus",
        is_termination_msg: Callable[[Dict], bool] | None = None,
        max_consecutive_auto_reply: int | None = None,
        human_input_mode: str | None = "ALWAYS",
        function_map: Dict[str, Callable[..., Any]] | None = None,
        code_execution_config: Dict | bool | None = None,
        default_auto_reply: str | Dict | None = "",
        llm_config: Dict | bool | None = False,
        system_message: str | None = "",
    ):
        super().__init__(
            name,
            is_termination_msg,
            max_consecutive_auto_reply,
            human_input_mode,
            function_map,
            code_execution_config,
            default_auto_reply,
            llm_config,
            system_message,
        )
