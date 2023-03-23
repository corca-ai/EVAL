from typing import Callable, Tuple
from enum import Enum

from langchain.agents.tools import Tool, BaseTool
from langchain.agents.agent import AgentExecutor


class ToolScope(Enum):
    GLOBAL = "global"
    SESSION = "session"


SessionGetter = Callable[[], Tuple[str, AgentExecutor]]


def tool(
    name: str,
    description: str,
    scope: ToolScope = ToolScope.GLOBAL,
):
    def decorator(func):
        func.name = name
        func.description = description
        func.is_tool = True
        func.scope = scope
        return func

    return decorator


class ToolWrapper:
    def __init__(self, name: str, description: str, scope: ToolScope, func):
        self.name = name
        self.description = description
        self.scope = scope
        self.func = func

    def is_global(self) -> bool:
        return self.scope == ToolScope.GLOBAL

    def is_per_session(self) -> bool:
        return self.scope == ToolScope.SESSION

    def to_tool(
        self,
        get_session: SessionGetter = lambda: [],
    ) -> BaseTool:
        func = self.func
        if self.is_per_session():
            func = lambda *args, **kwargs: self.func(
                *args, **kwargs, get_session=get_session
            )

        return Tool(
            name=self.name,
            description=self.description,
            func=func,
        )


class BaseToolSet:
    def tool_wrappers(cls) -> list[ToolWrapper]:
        methods = [
            getattr(cls, m) for m in dir(cls) if hasattr(getattr(cls, m), "is_tool")
        ]
        return [ToolWrapper(m.name, m.description, m.scope, m) for m in methods]
