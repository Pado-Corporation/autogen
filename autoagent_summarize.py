import logging
import sys

logger = logging.getLogger(__name__)
import autogen

config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    file_location=".",
)

print("LLM models: ", [config_list[i]["model"] for i in range(len(config_list))])

print(autogen.__file__)

user_goal = "Making a Microsoft investment report for investor"
user_context = "Target user is not expert."
toc_part = "Company background in the Introduction"

supervisor_prompt_template = """
You'll be responsible for a specific part of the report.
The report is designed to help users achieve their goal in the context
goal : {goal}
context : {context} 
Your main role is to ask the questions you need to build that report, Then user will reply it.
always try to use function.
ask question one by one. If you think you asked enough question, then call summarize function.
after If you finish ask, end answer with "TERMINATE(ASK)" after that just answer me only with "TERMINATE(ASK)".
use function as much as possible.

The part you will be responsible for is the "{toc_part}" of the report.
always try to use function.
"""

dialog_summarizer_prompt_template = """
You'll be responsebile for a specifc part of the report
The report is designed to help users achieve their {goal} in the context of the user's {goal}. 
Your main role is read dialog between user(question) and assistant(answer), and summarize them and make them into a few paragraphs.
The part you will be responsible for is the {toc_part} of the report. If you finish summarize, end answer with "TERMINATE(SUMMARIZE)" after that just answer me only with "TERMINATE(SUMMARIZE)"
"""

from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen import AssistantAgent, UserProxyAgent
import chromadb
from chromadb.utils import embedding_functions

logging.basicConfig(
    format="%(asctime)s | %(filename)s:%(lineno)d | %(levelname)s : %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=config_list[0]["api_key"], model_name="text-embedding-ada-002"
)
llm_config = {
    "request_timeout": 100,
    "seed": 42,
    "config_list": config_list,
    "temperature": 0,
}

llm_config_function = llm_config.copy()
llm_config_function["functions"] = [
    {
        "name": "ask_DB",
        "description": "ask expert that can access to my database",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "question to ask expert. Ensure the question includes enough context, such as the code and the execution result. The expert does not know the conversation between you and the user unless you share the conversation with the expert.",
                },
                "is_sufficient": {
                    "type": "string",
                    "enum": ["yes", "no", "init"],
                    "description": "Indicate if the previous answer was sufficient. Use 'yes' if the previous answer was sufficient, 'no' if it was not, and 'init' for the first question.",
                },
            },
            "required": ["message"],
        },
    },
    {
        "name": "ask_Summary",
        "description": "ask expert to summarize all of communication you did in report form.",
        "parameters": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "your name"}},
            "required": ["name"],
        },
    },
]

supervisor_prompt = supervisor_prompt_template.format(
    goal=user_goal, context=user_context, toc_part=toc_part
)
dialog_summarize_prompt = dialog_summarizer_prompt_template.format(
    goal=user_goal, context=user_context, toc_part=toc_part
)
autogen.ChatCompletion.start_logging()
termination_msg = (
    lambda x: isinstance(x, dict) and "TERMINATE" in str(x.get("content", ""))[-9:].upper()
)

toc_QA = RetrieveUserProxyAgent(
    name="toc_QA",
    system_message="Assistant who has extra content retrieval in database. ",
    human_input_mode="NEVER",
    retrieve_config={
        "task": "QA",
        "docs_path": "/Users/parkgyutae/dev/Pado/ASQ_Summarizer/test_files/",
        "chunk_token_size": 1024,
        "model": config_list[0]["model"],
        "client": chromadb.PersistentClient(path="/tmp/chromadb"),
        "collection_name": "groupchat",
        "embedding_function": openai_ef,
        "get_or_create": True,
    },
    code_execution_config=False,  # we don't want to execute code in this case.
)


def ask_DB(message, is_sufficient: str):
    logger.info(f"message {message} was {is_sufficient}")
    assistant = RetrieveAssistantAgent(
        name="assistant",
        system_message="You are a helpful assistant.",
        is_termination_msg=lambda x: isinstance(x, dict)
        and "TERMINATE(QA)" in str(x.get("content", ""))[-20:].upper(),
        llm_config={
            "request_timeout": 600,
            "seed": 42,
            "config_list": config_list,
        },
    )

    toc_QA.reset()
    toc_QA.initiate_chat(assistant, problem=message, silent=False, n_results=5)
    assistant.stop_reply_at_receive(toc_QA)
    # expert.human_input_mode, expert.max_consecutive_auto_reply = "NEVER", 0
    # final message sent from the expert
    # return the last message the expert received
    last_message = assistant.last_message()["content"]
    if last_message.strip() == "TERMINATE(QA)":
        return assistant.get_messages()[-3]["content"]
    else:
        return last_message


def ask_Summary(name):
    toc_summarizer = AssistantAgent(
        name="toc_summarizer",
        system_message=dialog_summarize_prompt,
        llm_config=llm_config,
    )

    chat_log = toc_manager.chat_messages
    user_proxy.initiate_chat(toc_summarizer, message=chat_log)
    last_message = toc_summarizer.last_message()["content"]
    if last_message == "TERMINATE(SUMMARIZE)":
        summary = toc_summarizer.get_messages()[-3]["content"].replace("TERMINATE", "")
        return summary
    else:
        summary = last_message.replace("TERMINATE", "")
        return summary


toc_manager = AssistantAgent(
    name="toc_manager",
    is_termination_msg=lambda x: isinstance(x, dict)
    and "TERMINATE(SUMMARIZE)" in str(x.get("content", ""))[-20:].upper(),
    system_message=supervisor_prompt,
    llm_config=llm_config_function,
    human_input_mode="NEVER",
    code_execution_config=False,
)

user_proxy = UserProxyAgent(
    name="tester",
    llm_config=False,
    is_termination_msg=lambda x: isinstance(x, dict)
    and "TERMINATE(ASK)" in str(x.get("content", ""))[-20:].upper(),
    human_input_mode="NEVER",
    code_execution_config=False,
    function_map={"ask_DB": ask_DB, "ask_Summary": ask_Summary},
)

user_proxy.initiate_chat(toc_manager, silent=False, message="use function")
