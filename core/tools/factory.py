from typing import Optional
from langchain.agents import load_tools
from langchain.agents.tools import BaseTool
from langchain.llms.base import BaseLLM

from .base import BaseToolSet, SessionGetter


class ToolsFactory:
    @staticmethod
    def from_toolset(
        toolset: BaseToolSet,
        only_global: Optional[bool] = False,
        only_per_session: Optional[bool] = False,
        get_session: SessionGetter = lambda: [],
    ) -> list[BaseTool]:
        tools = []
        for wrapper in toolset.tool_wrappers():
            if only_global and not wrapper.is_global():
                continue
            if only_per_session and not wrapper.is_per_session():
                continue
            tools.append(wrapper.to_tool(get_session=get_session))
        return tools

    @staticmethod
    def create_global_tools(
        toolsets: list[BaseToolSet],
    ) -> list[BaseTool]:
        tools = []
        for toolset in toolsets:
            tools.extend(
                ToolsFactory.from_toolset(
                    toolset=toolset,
                    only_global=True,
                )
            )
        return tools

    @staticmethod
    def create_per_session_tools(
        toolsets: list[BaseToolSet],
        get_session: SessionGetter = lambda: [],
    ) -> list[BaseTool]:
        tools = []
        for toolset in toolsets:
            tools.extend(
                ToolsFactory.from_toolset(
                    toolset=toolset,
                    only_per_session=True,
                    get_session=get_session,
                )
            )
        return tools

    @staticmethod
    def create_global_tools_from_names(
        toolnames: list[str],
        llm: Optional[BaseLLM],
    ) -> list[BaseTool]:
        return load_tools(toolnames, llm=llm)
