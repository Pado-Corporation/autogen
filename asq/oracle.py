from typing import Dict, Optional, Union
from autogen import UserProxyAgent
from autogen.agentchat.agent import Agent


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
            print("Done.")
            return
        return super().receive(message, sender, request_reply, silent)
