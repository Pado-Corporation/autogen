from autogen import config_list_from_dotenv
from dotenv import find_dotenv, load_dotenv
import os


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(metaclass=SingletonMeta):
    fast_model = "gpt-3.5-turbo-1106"
    smart_model = "gpt-4"

    def __init__(self):
        if not hasattr(self, "initialized"):
            env_path = find_dotenv()
            load_dotenv(env_path)

            self.log_level: str = os.getenv("LOG_LEVEL")
            self.openai_api_key: str = os.getenv("OPENAI_API_KEY")
            self.bing_search_api_key: str = os.getenv("BING_SEARCH_V7_SUBSCRIPTION_KEY")
            self.bing_search_endpoint: str = os.getenv("BING_SEARCH_V7_ENDPOINT")
            self.models_list = config_list_from_dotenv(
                env_path,
                model_api_key_map={
                    "gpt-3.5-turbo-1106": self.openai_api_key,
                    "gpt-3.5-turbo": self.openai_api_key,
                    "gpt-3.5-turbo-16k": self.openai_api_key,
                    "gpt-4-1106-preview": self.openai_api_key,
                    "gpt-4-vision-preview": self.openai_api_key,
                    "gpt-4": self.openai_api_key,
                    "gpt-4-32k": self.openai_api_key,
                },
            )

            self.initialized = True
