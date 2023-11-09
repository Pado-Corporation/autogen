from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
import chromadb
from chromadb.utils import embedding_functions
from typing import Dict, Optional, Union, List, Tuple, Any
from autogen.agentchat import Agent
from autogen.agentchat.assistant_agent import AssistantAgent
from autogen.agentchat.user_proxy_agent import UserProxyAgent
import autogen

RAG_FUNCTIONS = [
    {
        "name": "ask_DB",
        "description": "ask expert that can access to my database",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "question to ask DB. Ensure the question includes enough context, such as the code and the execution result. The expert does not know the conversation between you and the user unless you share the conversation with the expert.",
                },
            },
            "required": ["message"],
        },
    },
]

config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    file_location=".",
)
openai_ef = embedding_functions.OpenAIEmbeddingFunction(config_list[0]["api_key"])
termination_msg = lambda x: isinstance(x, dict) and "TERMINATE(QA)" in str(x.get("content", ""))[-20:].upper()


def ask_DB(message):
    ask = RetrieveUserProxyAgent(
        name="ASK_MAN",
        system_message="Assistant who has extra content retrieval in database. ",
        is_termination_msg=termination_msg,
        human_input_mode="ALWAYS",
        retrieve_config={
            "task": "QA",
            "docs_path": "/Users/parkgyutae/dev/Pado/ASQ_Summarizer/cameco/",
            "chunk_token_size": 4048,
            "model": config_list[0]["model"],
            "client": chromadb.PersistentClient(path="/tmp/chromadb"),
            "collection_name": "comparision",
            "embedding_function": openai_ef,
            "get_or_create": True,
            "n_includechunk": 2,
        },
        code_execution_config=False,  # we don't want to execute code in this case.
    )

    assistant = RetrieveAssistantAgent(
        name="assistant",
        system_message="You are a helpful assistant.",
        is_termination_msg=termination_msg,
        llm_config={
            "request_timeout": 600,
            "seed": 42,
            "config_list": config_list,
        },
    )

    ask.initiate_chat(assistant, n_results=20, problem="Who made cameco?")
    return assistant.last_message()


class RAGFunctioncallAgent(AssistantAgent):
    """Made by Pado, if you overide this RAGFunctioncallAgent, that automatically have the function which can communicate Vector DB
    In DBpath, upload file path as you want, now it support pdf, txt, markdown etc.."""

    def __init__(self, db_path, embedding_function=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_path = db_path
        self.llm_config.update({"functions": RAG_FUNCTIONS})

    def send(
        self,
        message: Union[Dict, str],
        recipient: Agent,
        request_reply: Optional[bool] = None,
        silent: Optional[bool] = False,
    ) -> bool:
        # When the agent composes and sends the message, the role of the message is "assistant"
        # unless it's "function".
        valid = self._append_oai_message(message, "assistant", recipient)
        if valid:
            if "ask_DB" in message:
                user_proxy = UserProxyAgent(
                    name="call ASK DB Function",
                    llm_config=False,
                    human_input_mode="NEVER",
                    is_termination_msg=lambda x: isinstance(x, dict)
                    and "TERMINATE(SUMMARIZE)" in str(x.get("content", ""))[-20:].upper(),
                    code_execution_config=False,
                    function_map={"ask_DB": ask_DB},
                )
                user_proxy.receive(message, self, request_reply, silent)
            else:
                recipient.receive(message, self, request_reply, silent)
        else:
            raise ValueError(
                "Message can't be converted into a valid ChatCompletion message. Either content or function_call must be provided."
            )


# n-results는 max로 검색해볼 chunk의 개수를 의미함. 가장 연관성이 높은 것부터 n_includechunk 만큼 보여주고, 만약 연관없다고 판단될경우 AI 가 update context call을 말하면 그다음 n_includechunk로 넘어가는 구조임.
