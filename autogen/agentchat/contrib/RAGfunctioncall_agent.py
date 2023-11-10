from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
import chromadb
from chromadb.utils import embedding_functions
from typing import Dict, Optional, Union, List, Tuple, Any
from autogen.agentchat import Agent
from autogen.agentchat.assistant_agent import AssistantAgent
from autogen.agentchat.user_proxy_agent import UserProxyAgent
import autogen

try:
    from termcolor import colored
except ImportError:

    def colored(x, *args, **kwargs):
        return x


# n-results는 max로 검색해볼 chunk의 개수를 의미함. 가장 연관성이 높은 것부터 n_includechunk 만큼 보여주고, 만약 연관없다고 판단될경우 AI 가 update context call을 말하면 그다음 n_includechunk로 넘어가는 구조임.

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


class LocalBasedRAGFunctioncallAgent(AssistantAgent):
    """Made by Pado, if you overide this RAGFunctioncallAgent, that automatically have the function which can communicate Vector DB
    In DBpath, upload file path as you want, now it support pdf, txt, markdown etc.."""

    def __init__(
        self,
        db_path: str,
        collection_name: str,
        n_max: int = 10,
        n_include: int = 3,
        client=chromadb.PersistentClient(path="/tmp/chromadb"),
        embedding_function=None,
        get_or_create=False,  # True면 다무시하고 collection에서 가져옴.
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.db_path = db_path
        self.llm_config.update({"functions": RAG_FUNCTIONS})
        if embedding_function is None:
            self.ef = embedding_functions.OpenAIEmbeddingFunction(config_list[0]["api_key"])
        else:
            self.ef = embedding_function
        self.termination_msg = lambda x: isinstance(x, dict) and "TERMINATE" in str(x.get("content", ""))[-20:].upper()
        self.n_max = n_max
        self.n_include = n_include
        self.ask = None
        self.answer = None
        self.collection_name = collection_name
        self.get_or_create = get_or_create
        self.client = client
        if get_or_create == True:
            self.get_or_create = True
            self.db_path = None
        else:
            self.get_or_create = False
        self.who_sent = None
        self.rag_proxy = UserProxyAgent(
            name="RAG_UserProxy",
            llm_config=False,
            human_input_mode="NEVER",
            is_termination_msg=self.termination_msg,
            code_execution_config=False,
            function_map={"ask_DB": self.ask_DB},
        )
        self.register_reply(Agent, LocalBasedRAGFunctioncallAgent._generate_ragfunctioncall_assistant_reply)

    def _generate_ragfunctioncall_assistant_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional[Any] = None,
    ) -> Tuple[bool, Union[str, Dict, None]]:
        if config is None:
            config = self
        if messages is None:
            messages = self._oai_messages[sender]
        message = messages[-1]
        try:
            if "ask_DB" == message["name"] and "function" == message["role"]:
                print("function answer route")
                self.stop_reply_at_receive(self.rag_proxy)
                content = message["content"]
                content = content.replace("TERMINATE", "")
                self.who_sent.receive(content, self, silent=False)
                return True, {"name": "ask_DB", "role": "function", "content": message["content"]}
            else:
                return False, None
        except:
            print("function pass route")
            return False, None

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
            if "ask_DB" == message.get("function_call", None)["name"]:
                print("function_call route")
                self._prepare_chat(self.rag_proxy, clear_history=True)
                self.who_sent = recipient
                self.rag_proxy.receive(message, self, silent=False)
            else:
                recipient.receive(message, self, request_reply, silent)
        else:
            raise ValueError(
                "Message can't be converted into a valid ChatCompletion message. Either content or function_call must be provided."
            )

    def ask_DB(self, message):
        if self.ask is None or self.answer is None:
            ask = RetrieveUserProxyAgent(
                name="function_DB_ASK",
                system_message="Assistant who has extra content retrieval in database. ",
                is_termination_msg=self.termination_msg,
                human_input_mode="NEVER",
                retrieve_config={
                    "task": "QA",
                    "docs_path": self.db_path,
                    "chunk_token_size": 4048,
                    "model": config_list[0]["model"],
                    "client": self.client,
                    "collection_name": self.collection_name,
                    "embedding_function": self.ef,
                    "get_or_create": True,
                    "n_includechunk": self.n_include,
                },
                code_execution_config=False,  # we don't want to execute code in this case.
            )
            self.ask = ask
            answer = RetrieveAssistantAgent(
                name="function_DB_ANSWER",
                system_message="You are a helpful assistant.",
                is_termination_msg=self.termination_msg,
                llm_config={
                    "request_timeout": 600,
                    "seed": 42,
                    "config_list": config_list,
                },
            )
            self.answer = answer
            ask.initiate_chat(answer, n_results=self.n_max, problem=message)

        else:
            ask = self.ask
            answer = self.answer
            ask.initiate_chat(answer, n_results=self.n_max, problem=message)
        return answer.last_message()["content"]
