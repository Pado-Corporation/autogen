from autogen import config_list_from_dotenv
from typing import Dict, List
from angel import Angel
from king import King
from servant import Servant
from colosseum import Colosseum
import json
import logging

logger = logging.getLogger()


def read_requirements() -> Dict:
    with open("requirements.json", "r") as file:
        return json.load(file)


def create_servants(requirements: Dict) -> List[Servant]:
    servants: List[Servant] = []
    assistants = requirements["assistants"]
    for assistant in assistants:
        servant = Servant(
            assistant["name"],
            responsibility=assistant["responsibility"],
            goal=requirements["goal"],
            format=requirements["format"],
            bg_knowledge=assistant["bg_knowledge"],
        )
        servants.append(servant)
    return servants


if __name__ == "__main__":
    config_list_from_dotenv(
        ".env",
        model_api_key_map={
            "gpt-4": "OPENAI_API_KEY",
            "gpt-3.5-turbo": "OPENAI_API_KEY",
            "gpt-3.5-turbo-16k": "OPENAI_API_KEY",
        },
    )
    requirements = read_requirements()

    initial_request = f"""This is my goal: {requirements["goal"]}
The desired format for my problem: {requirements["format"]}
Here are some background knowledge about me: {requirements["summary"]}
"""

    king = King()
    servants = create_servants(requirements)
    colosseum = Colosseum(agents=[king, *servants], messages=[], max_round=20)

    angel = Angel(groupchat=colosseum)

    king.initiate_chat(angel, message=initial_request)
