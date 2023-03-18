from typing import Tuple

from llm import ChatOpenAI
from langchain.agents.agent import AgentExecutor
from langchain.agents.initialize import initialize_agent
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.memory.chat_memory import BaseChatMemory
from langchain.chat_models.base import BaseChatModel

from prompts.input import AWESOMEGPT_PREFIX, AWESOMEGPT_SUFFIX

from tools.factory import ToolsFactory
from tools.cpu import (
    Terminal,
    RequestsGet,
    WineDB,
    ExitConversation,
)
from tools.gpu import (
    ImageEditing,
    InstructPix2Pix,
    Text2Image,
    VisualQuestionAnswering,
)
from handlers.base import FileHandler, FileType
from handlers.image import ImageCaptioning
from handlers.dataframe import CsvToDataframe
from env import settings


class AgentFactory:
    def __init__(self):
        self.llm: BaseChatModel = None
        self.memory: BaseChatMemory = None
        self.tools: list = None
        self.handler: FileHandler = None

    def create(self):
        print("Initializing AwesomeGPT")
        self.create_llm()
        self.create_memory()
        self.create_tools()
        self.create_handler()
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

    def create_llm(self):
        self.llm = ChatOpenAI(temperature=0)

    def create_memory(self):
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

    def create_tools(self):
        if self.memory is None:
            raise ValueError("Memory must be initialized before tools")

        if self.llm is None:
            raise ValueError("LLM must be initialized before tools")

        toolnames = ["python_repl", "wikipedia"]

        if settings["SERPAPI_API_KEY"]:
            toolnames.append("serpapi")
        if settings["BING_SEARCH_URL"] and settings["BING_SUBSCRIPTION_KEY"]:
            toolnames.append("bing-search")

        toolsets = [
            Terminal(),
            RequestsGet(),
            ExitConversation(self.memory),
            Text2Image("cuda"),
            ImageEditing("cuda"),
            InstructPix2Pix("cuda"),
            VisualQuestionAnswering("cuda"),
        ]

        if settings["WINEDB_HOST"] and settings["WINEDB_PASSWORD"]:
            toolsets.append(WineDB())

        self.tools = [
            *ToolsFactory.from_names(toolnames, llm=self.llm),
            *ToolsFactory.from_toolsets(toolsets),
        ]

    def create_handler(self):
        self.handler = FileHandler(
            {
                FileType.IMAGE: ImageCaptioning("cuda"),
                FileType.DATAFRAME: CsvToDataframe(),
            }
        )

    def get_handler(self):
        if self.handler is None:
            raise ValueError("Handler must be initialized before returning")

        return self.handler

    @staticmethod
    def get_agent_and_handler() -> Tuple[AgentExecutor, FileHandler]:
        factory = AgentFactory()
        agent = factory.create()
        handler = factory.get_handler()

        return (agent, handler)
