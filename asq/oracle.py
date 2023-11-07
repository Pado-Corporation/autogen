from typing import Dict, Optional
from autogen import UserProxyAgent
from autogen.agentchat.agent import Agent
import logging
import json

logger = logging.getLogger()


def save_requirements(requirements: Dict):
    if not requirements:
        return
    try:
        with open("requirements.json", "w", encoding="utf-8") as json_file:
            json.dump(requirements, json_file, ensure_ascii=False, indent=4)
        return print(f"\nLet's start executing the tasks for you!\n", flush=True)
    except IOError as e:
        return print(f"An error occurred while writing JSON to the file: {e}")


def parse_requirements(message: str) -> Dict:
    try:
        json_str_start = message.index("{")
        json_str_end = message.rindex("}", 0, message.index("[END]"))

        concluding_message = message[:json_str_start].strip()
        print(f"ASQ: {concluding_message}", flush=True)

        json_str = message[json_str_start : json_str_end + 1]
        json_obj: Dict = json.loads(json_str)
        return json_obj
    except ValueError as e:
        logger.error("Error in extracting or parsing JSON: %s", e)
        return {}


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
            requirements = parse_requirements(message)
            return save_requirements(requirements)
        return super().receive(message, sender, request_reply, silent)
