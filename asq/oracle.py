from typing import Dict, Optional
from autogen import UserProxyAgent
from autogen.agentchat.agent import Agent
import logging
import json

logger = logging.getLogger()


def parse_info(message: str) -> Dict | None:
    try:
        json_str_start = message.index("{")
        json_str_end = message.rindex("}", 0, message.index("[END]"))
        message = message[:json_str_start].strip()
        print(f"ASQ: f{message}")

        json_str = message[json_str_start : json_str_end + 1]
        json_obj: Dict = json.loads(json_str)
        return json_obj
    except ValueError as e:
        logger.error("Error in extracting or parsing JSON:", e)
        return None


class Oracle(UserProxyAgent):
    """Receives input from the human user until God understands what the human user wants."""

    def __init__(self, name: Optional[str] = "Oracle"):
        super().__init__(
            name,
            human_input_mode="ALWAYS",
            default_auto_reply="Surprise me.",
        )

    def receive(
        self, message: Dict | str, sender: Agent, request_reply: bool | None = None, silent: bool | None = False
    ):
        if "[END]" in message:
            return parse_info(message)
        return super().receive(message, sender, request_reply, silent)
