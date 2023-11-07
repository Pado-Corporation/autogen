from typing import Dict, List
from servant import Servant
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
        system_message = f"""You are {assistant["name"]}. Do your duty to help the user reach the goal based on the information:

Your responsibility: {assistant["responsibility"]}
Dependency to other assistants: {assistant["dependency"]}
Background knowledge about the user: {assistant["bg_knowledge"]}

Respond in this format: {assistant["response_format"]}
"""
        servant = Servant(
            assistant["name"],
            system_message=system_message,
        )
        servants.append(servant)
    return servants


if __name__ == "__main__":
    requirements = read_requirements()
    servants = create_servants(requirements)
    for i, servant in enumerate(servants):
        print(f"{i+1}.")
        print(servant)
