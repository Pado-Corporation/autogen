import logging
import sys

from chromadb.utils import embedding_functions

import better_exceptions
import autogen

better_exceptions.MAX_LENGTH = None

logger = logging.getLogger(__name__)

logging.basicConfig(
    format="%(asctime)s | %(filename)s:%(lineno)d | %(levelname)s : %(message)s", level=logging.INFO, stream=sys.stdout
)

config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    file_location=".",
)
llm_config = (
    {
        "request_timeout": 600,
        "seed": 42,
        "config_list": config_list,
    },
)
termination_msg = lambda x: isinstance(x, dict) and "TERMINATE" in str(x.get("content", ""))[-20:].upper()
print("LLM models: ", [config_list[i]["model"] for i in range(len(config_list))])

print(autogen.__file__)
openai_ef = embedding_functions.OpenAIEmbeddingFunction(config_list[0]["api_key"])

from autogen.agentchat.contrib.RAGfunctioncall_agent import LocalBasedRAGFunctioncallAgent
from autogen.agentchat.user_proxy_agent import UserProxyAgent

rag_assistant = LocalBasedRAGFunctioncallAgent(
    name="RagAssistant",
    db_path="/Users/parkgyutae/dev/Pado/ASQ_Summarizer/cameco/",
    collection_name="test",
    embedding_function=openai_ef,
    llm_config=llm_config,
)
user_agent = UserProxyAgent(name="user", code_execution_config=False)

user_agent.initiate_chat(rag_assistant, silent=False, message="I want to Find who is CEO of cameco from DB")
