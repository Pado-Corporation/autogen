from autogen import config_list_from_dotenv
from angel import Angel
from king import King
from servant import Servant

if __name__ == "__main__":
    config_list_from_dotenv(
        ".env",
        model_api_key_map={
            "gpt-4": "OPENAI_API_KEY",
            "gpt-3.5-turbo": "OPENAI_API_KEY",
            "gpt-3.5-turbo-16k": "OPENAI_API_KEY",
        },
    )

    angel = Angel()
    king = King()

    """
    TODO)
    The final result from this phase needs to be the solution to the user's problem.
    """
