from typing import Dict, Tuple

from llm import ChatOpenAI
from langchain.agents.agent import AgentExecutor
from langchain.agents.initialize import initialize_agent
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.memory.chat_memory import BaseChatMemory
from langchain.chat_models.base import BaseChatModel

from prompts.input import AWESOMEGPT_PREFIX, AWESOMEGPT_SUFFIX

from tools.base import BaseToolSet
from tools.factory import ToolsFactory
from handlers.base import BaseHandler, FileHandler, FileType
from env import settings


class AgentBuilder:
    def __init__(self):
        self.llm: BaseChatModel = None
        self.memory: BaseChatMemory = None
        self.tools: list = None
        self.handler: FileHandler = None

    def build_llm(self):
        self.llm = ChatOpenAI(temperature=0)

    def build_memory(self):
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

    def build_tools(self, toolsets: list[BaseToolSet] = []):
        if self.llm is None:
            raise ValueError("LLM must be initialized before tools")

        toolnames = ["python_repl", "wikipedia"]

        if settings["SERPAPI_API_KEY"]:
            toolnames.append("serpapi")
        if settings["BING_SEARCH_URL"] and settings["BING_SUBSCRIPTION_KEY"]:
            toolnames.append("bing-search")

        self.tools = [
            *ToolsFactory.from_names(toolnames, llm=self.llm),
            *ToolsFactory.from_toolsets(toolsets),
        ]

    def build_handler(self, handlers: Dict[FileType, BaseHandler]):
        self.handler = FileHandler(handlers)

    def get_agent(self):
        print("Initializing AwesomeGPT")
        if self.llm is None:
            raise ValueError("LLM must be initialized before agent")

        if self.tools is None:
            raise ValueError("Tools must be initialized before agent")

        if self.memory is None:
            raise ValueError("Memory must be initialized before agent")

        return initialize_agent(
            self.tools,
            self.llm,
            agent="chat-conversational-react-description",
            verbose=True,
            memory=self.memory,
            agent_kwargs={
                "system_message": AWESOMEGPT_PREFIX,
                "human_message": AWESOMEGPT_SUFFIX,
            },
        )

    def get_handler(self):
        if self.handler is None:
            raise ValueError("Handler must be initialized before returning")

        return self.handler

    @staticmethod
    def get_agent_and_handler(
        toolsets: list[BaseToolSet], handlers: Dict[FileType, BaseHandler]
    ) -> Tuple[AgentExecutor, FileHandler]:
        builder = AgentBuilder()
        builder.build_llm()
        builder.build_memory()
        builder.build_tools(toolsets)
        builder.build_handler(handlers)

        agent = builder.get_agent()
        handler = builder.get_handler()

        return (agent, handler)
