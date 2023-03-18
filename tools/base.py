from langchain.agents.tools import Tool, BaseTool


def tool(name, description):
    def decorator(func):
        func.name = name
        func.description = description
        func.is_tool = True
        return func

    return decorator


class BaseToolSet:
    def to_tools(cls) -> list[BaseTool]:
        method_tools = [getattr(cls, m) for m in dir(cls) if m.is_tool]
        return [
            Tool(name=m.name, description=m.description, func=m) for m in method_tools
        ]
