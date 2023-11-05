from typing import Callable, Dict, Optional, Any
from autogen import ConversableAgent


class Servant(ConversableAgent):
    def __init__(
        self,
        name: Optional[str] = "Servant",
        is_termination_msg: Callable[[Dict], bool] | None = None,
        max_consecutive_auto_reply: int | None = None,
        human_input_mode: str | None = "TERMINATE",
        function_map: Dict[str, Callable[..., Any]] | None = None,
        code_execution_config: Dict | bool | None = None,
        llm_config: Dict | bool | None = None,
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
        system_message = f"""You are a {name}.
        You are responsible for this task: {responsibility}
        You are serving the user to help achieve a goal: {goal}
        The best format to solve the problem is: {format}
        You know some background knowledge about the user: {bg_knowledge}
"""
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
        return f"[{self.name}]\nresponsibility: {self.responsibility}\nbg_knowledge: {self.bg_knowledge}"
