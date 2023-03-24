from langchain.chat_models.base import BaseChatModel
from langchain.output_parsers.base import BaseOutputParser
from langchain.llms.huggingface_pipeline import HuggingFacePipeline
from langchain.agents.conversational.base import ConversationalAgent

from env import settings

from core.prompts.input import EVAL_PREFIX, EVAL_SUFFIX
from core.tools.base import BaseToolSet
from core.tools.factory import ToolsFactory

from .llm import ChatOpenAI
from .chat_agent import ConversationalChatAgent
from .parser import EvalOutputParser


class AgentBuilder:
    def __init__(self, toolsets: list[BaseToolSet] = []):
        self.llm: BaseChatModel = None
        self.parser: BaseOutputParser = None
        self.global_tools: list = None
        self.toolsets = toolsets

    def build_llm(self):
        self.llm = HuggingFacePipeline.from_model_id(
            model_id="chavinlo/alpaca-native",
            task="text-generation",
            model_kwargs={
                "load_in_8bit": True,
                "device_map": "auto",
                "max_length": 8192,
            },
        )

    def build_parser(self):
        self.parser = EvalOutputParser()

    def build_global_tools(self):
        if self.llm is None:
            raise ValueError("LLM must be initialized before tools")

        toolnames = ["python_repl", "wikipedia"]

        if settings["SERPAPI_API_KEY"]:
            toolnames.append("serpapi")
        if settings["BING_SEARCH_URL"] and settings["BING_SUBSCRIPTION_KEY"]:
            toolnames.append("bing-search")

        self.global_tools = [
            *ToolsFactory.create_global_tools_from_names(toolnames, llm=self.llm),
            *ToolsFactory.create_global_tools(self.toolsets),
        ]

    def get_global_tools(self):
        if self.global_tools is None:
            raise ValueError("Global tools are not initialized yet")

        return self.global_tools

    def get_agent(self):
        if self.llm is None:
            raise ValueError("LLM must be initialized before agent")

        if self.parser is None:
            raise ValueError("Parser must be initialized before agent")

        if self.global_tools is None:
            raise ValueError("Global tools must be initialized before agent")

        return ConversationalAgent.from_llm_and_tools(
            llm=self.llm,
            tools=[
                *self.global_tools,
                *ToolsFactory.create_per_session_tools(
                    self.toolsets
                ),  # for names and descriptions
            ],
        )
