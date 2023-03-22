from typing import Dict, Any

from langchain.agents.tools import BaseTool
from langchain.agents.agent import Agent, AgentExecutor
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.memory.chat_memory import BaseChatMemory

from tools.base import BaseToolSet
from tools.factory import ToolsFactory

from agents.builder import AgentBuilder


class AgentManager:
    def __init__(
        self,
        agent: Agent,
        global_tools: list[BaseTool],
        toolsets: list[BaseToolSet] = [],
    ):
        self.agent: Agent = agent
        self.global_tools: list[BaseTool] = global_tools
        self.toolsets: list[BaseToolSet] = toolsets
        self.executors: Dict[str, AgentExecutor] = {}

    def create_memory(self) -> BaseChatMemory:
        return ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    def create_executor(self, session: str) -> AgentExecutor:
        memory: BaseChatMemory = self.create_memory()
        return AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=[
                *self.global_tools,
                *ToolsFactory.create_per_session_tools(
                    self.toolsets,
                    session,
                ),
            ],
            memory=memory,
            verbose=True,
        )

    def remove_executor(self, session: str) -> None:
        if session in self.executors:
            del self.executors[session]

    def get_or_create_executor(self, session: str) -> AgentExecutor:
        if not (session in self.executors):
            self.executors[session] = self.create_executor(session)
        return self.executors[session]

    @staticmethod
    def create(toolsets: list[BaseToolSet]) -> "AgentManager":
        builder = AgentBuilder(toolsets)
        builder.build_llm()
        builder.build_parser()
        builder.build_global_tools()

        agent = builder.get_agent()
        global_tools = builder.get_global_tools()

        return AgentManager(
            agent=agent,
            global_tools=global_tools,
            toolsets=toolsets,
        )
