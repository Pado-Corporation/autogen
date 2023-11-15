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
        "request_timeout": 60,
        "seed": 42,
        "config_list": config_list,
    },
)
termination_msg = lambda x: isinstance(x, dict) and "TERMINATE" in str(x.get("content", ""))[-20:].upper()
print("LLM models: ", [config_list[i]["model"] for i in range(len(config_list))])

print(autogen.__file__)
openai_ef = embedding_functions.OpenAIEmbeddingFunction(config_list[0]["api_key"])

from autogen.agentchat.contrib.RAGfunctioncall_agent import LocalBasedRAGFunctioncallAgent
from autogen.agentchat.assistant_agent import AssistantAgent
from autogen.agentchat.user_proxy_agent import UserProxyAgent


user_goal = "I want to write a investment report for cameco."
user_context = "I'm not expert in investment, so write in easy to read."
user_toc = """
Table of Contents (TOC) :
- Introduction
    - Company Overview
    - Purpose and Scope of the Report
- Market Analysis
    - Current State of the Uranium Market
    - Demand and Supply Trends
    - Analysis of Competitors
- Company Analysis
    - Financial Health
    - Business Model and Strategy
    - SWOT Analysis (Strengths, Weaknesses, Opportunities, Threats)
- Risk Factors
    - Market Risks
    - Operational Risks
    - Regulatory Risks
- Financial Performance Analysis
    - Income Statement Analysis
    - Balance Sheet Analysis
    - Cash Flow Analysis
- Valuation
    - Valuation Methodologies
    - Value Assessment
- Investment Opinion and Conclusion
    - Final Investment Recommendation
    - Conclusion and Outlook
"""
content_must_include = """
What makes CAMECO so different from other nuclear companies.
"""
all_groupchat = autogen.GroupChat(agents=[], messages=[], max_round=12)
#### DB Research PART
DB_researcher = LocalBasedRAGFunctioncallAgent(
    name="DB_researcher",
    system_message="Agent has a power to find information in DB, Before using ideabank, it first turn on.",
    db_path="/Users/parkgyutae/dev/Pado/ASQ_Summarizer/cameco/",
    collection_name="test",
    embedding_function=openai_ef,
    llm_config=llm_config,
)
user_agent = UserProxyAgent(name="user", code_execution_config=False)

all_groupchat.agents.append(DB_researcher)

##### IDEA BANK PART
DB_researcher_for_ideabank = LocalBasedRAGFunctioncallAgent(
    name="DB_researcher_for_ideabank",
    system_message="Agent has a power to find information in DB",
    db_path="/Users/parkgyutae/dev/Pado/ASQ_Summarizer/cameco/",
    collection_name="test",
    embedding_function=openai_ef,
    llm_config=llm_config,
)
brain_for_ideabank = AssistantAgent(
    name="Ideabank",
    system_message="ideabank's brain, which infers information that cannot be found in the existing DB based on information that can be found in the DB.",
    llm_config=llm_config,
)
ideabank_groupchat = autogen.GroupChat(
    agents=[DB_researcher_for_ideabank, brain_for_ideabank], messages=[], max_round=12
)
idea_banker = autogen.GroupChatManager(
    groupchat=ideabank_groupchat,
    llm_config=llm_config,
    system_message="infers information that cannot be found in the existing DB based on information that can be found in the DB. This must turn on if simple db research failed. dependency = [DB_researcher]",
)

all_groupchat.agents.append(idea_banker)

##### Coordinator PART
coordinator_memory = autogen.GroupChatMemory(groupchat=all_groupchat)
coordinator = autogen.AssistantAgent(
    name="cordinator_for_report",
    system_message=f"""you are the cordinator which oversee multi-agent-system. The idea of multi agent system is that instead of having a single LLM, you have multiple LLMs with separate roles, and they talk to each other to solve complex problems, so you can solve more complex problems because there are fewer things for each LLM to consider.
    In this scenario you should solve "{user_goal}" in this context : {user_context}. and make report this form: 
    {user_toc}
    and must contain this content : {content_must_include}
    
    You have a total of three actions to choose from.
    1. you can ask the DB a question to solve this problem, and the DB will find or deduce the information you are looking for and return it to you. Try to break your question down into the smallest possible pieces to make it easier for the DB to understand. If the DB doesn't answer the question correctly, don't ask it again.
    2. You have a bad memory, so you need to record as much information as possible. From the answers you get back, you can extract the parts you need for your final report and commit them to memory. You have to remember that even when the DB doesn't answer your question correctly.
    3. Once you have enough information to accomplish your goal, you can call Writer. Writer will create a report based on your memory.

    You can't do anything else: you're asking individual questions to other LLMs, so keep that in mind and give them direction so that they behave well.
    """,
)
all_groupchat.agents.append(*[coordinator, coordinator_memory])
##### Writer PART
writer_hand = autogen.GroupChatMemoryUseAgent(
    groupchat=all_groupchat,
    name="Report_Writer",
    system_message=f"""You are the agent that creates the report based on what is in your memory. Make sure you know the following before you create your report. Make sure you include everything.
    USER GOAL : {user_goal}
    USER CONTEXT : {user_context}
    TOC of REPORT : {user_toc}
    CONTENT MUST INCLUDED: {content_must_include}

    If you finished to Write, then reply with DONE
    """,
)
writer_head = autogen.UserProxyAgent(
    name="writer_head",
    llm_config=None,
    default_auto_reply="continue",
    termination_msg=lambda x: isinstance(x, dict) and "DONE" in str(x.get("content", ""))[-5:].upper(),
)
writer_groupchat = autogen.GroupChat(agents=[writer_hand, writer_head], messages=[], max_round=12)
writer = autogen.GroupChatManager(
    groupchat=writer_groupchat,
    llm_config=None,
    system_message="Write Report based on Memory of Coordinator. It must be final step of whole process.",
)
all_groupchat.agents.append(writer)


all_manager = autogen.GroupChatManager(
    groupchat=all_groupchat, llm_config=llm_config, system_message="Allocator of Whole Project"
)


user_agent.initiate_chat(all_manager, silent=False, message="Make a report")
