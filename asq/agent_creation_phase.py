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
    requirements = read_requirements()
    servants = create_servants(requirements)
    for i, servant in enumerate(servants):
        print(f"{i+1}.")
        print(servant)
