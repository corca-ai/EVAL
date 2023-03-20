from typing import Optional

from langchain.agents import load_tools
from langchain.agents.tools import BaseTool
from langchain.llms.base import BaseLLM

from .base import BaseToolSet


class ToolsFactory:
    @staticmethod
    def from_toolsets(toolsets: list[BaseToolSet]) -> list[BaseTool]:
        tools = []
        for toolset in toolsets:
            tools.extend(toolset.to_tools())
        return tools

    @staticmethod
    def from_names(toolnames: list[str], llm: Optional[BaseLLM]) -> list[BaseTool]:
        return load_tools(toolnames, llm=llm)
