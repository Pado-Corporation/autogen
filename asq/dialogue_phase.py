from autogen import config_list_from_dotenv
from oracle import Oracle
from god import God

if __name__ == "__main__":
    config_list_from_dotenv(
        ".env",
        model_api_key_map={
            "gpt-4": "OPENAI_API_KEY",
            "gpt-3.5-turbo": "OPENAI_API_KEY",
            "gpt-3.5-turbo-16k": "OPENAI_API_KEY",
        },
    )

    oracle = Oracle()
    god = God()

    # Let's welcome the human user to ASQ!
    print(open("welcome.txt", "r").read())
    # Let's wait for the human user's request!
    user_request = input(">> ")
    user_request = "What's up?" if user_request == "" else user_request

    oracle.initiate_chat(god, message=user_request)
