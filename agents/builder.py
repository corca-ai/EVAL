from langchain.chat_models.base import BaseChatModel
from langchain.output_parsers.base import BaseOutputParser

from prompts.input import EVAL_PREFIX, EVAL_SUFFIX
from env import settings

from tools.base import BaseToolSet
from tools.factory import ToolsFactory

from .llm import ChatOpenAI
from .chat_agent import ConversationalChatAgent
from .parser import EvalOutputParser


class AgentBuilder:
    def __init__(self):
        self.llm: BaseChatModel = None
        self.parser: BaseOutputParser = None
        self.tools: list = None

    def build_llm(self):
        self.llm = ChatOpenAI(temperature=0)

    def build_parser(self):
        self.parser = EvalOutputParser()

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

    def get_tools(self):
        if self.tools is None:
            raise ValueError("Tools must be initialized before agent")

        return self.tools

    def get_agent(self):
        if self.llm is None:
            raise ValueError("LLM must be initialized before agent")

        if self.parser is None:
            raise ValueError("Parser must be initialized before agent")

        if self.tools is None:
            raise ValueError("Tools must be initialized before agent")

        return ConversationalChatAgent.from_llm_and_tools(
            llm=self.llm,
            tools=self.tools,
            system_message=EVAL_PREFIX.format(bot_name=settings["BOT_NAME"]),
            human_message=EVAL_SUFFIX.format(bot_name=settings["BOT_NAME"]),
            output_parser=self.parser,
        )
