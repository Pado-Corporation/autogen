import sys
from typing import Callable, Dict, Optional, Union
from autogen import GroupChat, GroupChatManager


class Angel(GroupChatManager):
    def __init__(
        self,
        groupchat: GroupChat,
        name: str | None = "chat_manager",
        max_consecutive_auto_reply: int | None = sys.maxsize,
        human_input_mode: str | None = "NEVER",
        system_message: str | None = "Group chat manager.",
        **kwargs
    ):
        super().__init__(groupchat, name, max_consecutive_auto_reply, human_input_mode, system_message, **kwargs)
