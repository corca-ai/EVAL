from typing import Dict

from langchain.agents.agent import Agent, AgentExecutor
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.memory.chat_memory import BaseChatMemory

from tools.base import BaseToolSet

from .builder import AgentBuilder


class AgentManager:
    def __init__(self, agent: Agent, tools: list[BaseToolSet]):
        self.agent: Agent = agent
        self.tools: list[BaseToolSet] = tools
        self.executors: Dict[str, AgentExecutor] = {}

    def create_memory(self) -> BaseChatMemory:
        return ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    def create_executor(self) -> AgentExecutor:
        memory: BaseChatMemory = self.create_memory()
        return AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            memory=memory,
        )

    def remove_executor(self, key: str) -> None:
        if key in self.executors:
            del self.executors[key]

    def get_or_create_executor(self, key: str) -> AgentExecutor:
        if not (key in self.executors):
            self.executors[key] = self.create_executor()
        return self.executors[key]

    @staticmethod
    def create(toolsets: list[BaseToolSet]) -> "AgentManager":
        builder = AgentBuilder()
        builder.build_llm()
        builder.build_parser()
        builder.build_tools(toolsets)
        agent = builder.get_agent()
        tools = builder.get_tools()

        return AgentManager(agent, tools)
