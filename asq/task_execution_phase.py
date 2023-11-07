from autogen import config_list_from_dotenv
from typing import Dict, List
from angel import Angel
from king import King
from servant import Servant
from colosseum import Colosseum
import json
import logging

logger = logging.getLogger()

KING_MESSAGE = """You are King.
Push other assistants to meet the standards.
Criticize other assistants to make them reflect on their previous works. 
Guide them to better achieve the user's request by reminding them.
When talking to other assistants, explicitly state your name and the assistant that you're giving feedbacks to.
Do not make any small talks (e.g., encouragement) with other assistants.
"""

ANGEL_MESSAGE = """You are Angel.
Always keep in mind the relationship between assistants based on their dependencies.
"""


def read_requirements() -> Dict:
    with open("requirements.json", "r") as file:
        return json.load(file)


def create_servants(requirements: Dict) -> List[Servant]:
    servants: List[Servant] = []
    assistants = requirements["assistants"]
    for assistant in assistants:
        system_message = f"""You are {assistant["name"]}. Do your duty to help the user reach the goal based on the information. When receiving feedbacks from the King assistant, reflect on the feedbacks and generate a new response.

Your responsibility: {assistant["responsibility"]}
Dependent to these assistants: {assistant["dependency"]}
Background knowledge about the user: {assistant["bg_knowledge"]}

Always respond in this format: {assistant["response_format"]}
"""
        servant = Servant(
            assistant["name"],
            system_message=system_message,
        )
        servant.reset()
        servants.append(servant)
    return servants


if __name__ == "__main__":
    config_list_from_dotenv(
        ".env",
        model_api_key_map={"gpt-4": "OPENAI_API_KEY"},
    )
    requirements = read_requirements()
    servants = create_servants(requirements)

    initial_request = f"""This is my goal: {requirements["goal"]}
The desired format for my problem: {requirements["solution_format"]}
Here are some background knowledge about me: {requirements["summary"]}
"""

    king = King(
        default_auto_reply="Keep on improving the result to be sufficient for the user to be satisfied.",
        system_message=KING_MESSAGE,
    )

    colosseum = Colosseum(agents=[king, *servants], messages=[], max_round=20)
    angel = Angel(
        groupchat=colosseum,
        system_message=ANGEL_MESSAGE,
    )

    angel.reset()
    king.reset()
    colosseum.reset()

    king.initiate_chat(angel, message=initial_request)
