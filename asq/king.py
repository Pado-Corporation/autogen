from typing import Any, Callable, Dict, Optional
from autogen import UserProxyAgent


class King(UserProxyAgent):
    """King agent is the envoy from the Human user that talks to Servants"""

    def __init__(
        self,
        name: Optional[str] = "King",
        is_termination_msg: Callable[[Dict], bool] | None = None,
        max_consecutive_auto_reply: int | None = None,
        human_input_mode: str | None = "NEVER",
        function_map: Dict[str, Callable[..., Any]] | None = None,
        code_execution_config: Dict | bool | None = None,
        default_auto_reply: str | Dict | None = None,
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
