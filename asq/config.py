from dotenv import find_dotenv, load_dotenv
import os


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(metaclass=SingletonMeta):
    def __init__(self):
        if not hasattr(self, "initialized"):
            env_path = find_dotenv()
            load_dotenv(env_path)

            self.log_level: str = os.getenv("LOG_LEVEL")
            self.openai_api_key: str = os.getenv("OPENAI_API_KEY")
            self.bing_search_api_key: str = os.getenv("BING_SEARCH_V7_SUBSCRIPTION_KEY")
            self.bing_search_endpoint: str = os.getenv("BING_SEARCH_V7_ENDPOINT")
            self.initialized = True
