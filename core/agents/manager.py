from typing import Dict

from langchain.agents.agent import Agent, AgentExecutor
from langchain.agents.tools import BaseTool
from langchain.callbacks import set_handler
from langchain.callbacks.base import CallbackManager
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.memory.chat_memory import BaseChatMemory

from core.tools.base import BaseToolSet
from core.tools.factory import ToolsFactory

from .builder import AgentBuilder
from .callback import EVALCallbackHandler

callback_manager = CallbackManager([EVALCallbackHandler()])
set_handler(EVALCallbackHandler())


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
        tools = [
            *self.global_tools,
            *ToolsFactory.create_per_session_tools(
                self.toolsets,
                get_session=lambda: (session, self.executors[session]),
            ),
        ]
        for tool in tools:
            tool.set_callback_manager(callback_manager)

        return AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=tools,
            memory=memory,
            callback_manager=callback_manager,
            verbose=True,
        )

    def remove_executor(self, session: str) -> None:
        if session in self.executors:
            del self.executors[session]

    def get_or_create_executor(self, session: str) -> AgentExecutor:
        if not (session in self.executors):
            self.executors[session] = self.create_executor(session=session)
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
