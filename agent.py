from typing import Dict, List, Tuple

from llm import ChatOpenAI
from langchain.agents import load_tools
from langchain.agents.agent import AgentExecutor
from langchain.agents.tools import Tool
from langchain.agents.initialize import initialize_agent
from langchain.chains.conversation.memory import ConversationBufferMemory

from utils import AWESOMEGPT_PREFIX, AWESOMEGPT_SUFFIX

from tools.cpu import (
    RequestsGet,
    WineDB,
    ExitConversation,
)
from tools.gpu import (
    ImageEditing,
    InstructPix2Pix,
    Text2Image,
    ImageCaptioning,
    VisualQuestionAnswering,
)
from handler import Handler, FileType
from env import settings


def get_agent() -> Tuple[AgentExecutor, Handler]:
    print("Initializing AwesomeGPT")
    llm = ChatOpenAI(temperature=0)

    tool_names = ["python_repl", "terminal", "wikipedia"]

    if settings["SERPAPI_API_KEY"]:
        tool_names.append("serpapi")
    if settings["BING_SEARCH_URL"] and settings["BING_SUBSCRIPTION_KEY"]:
        tool_names.append("bing-search")
    tools = [*load_tools(tool_names, llm=llm)]

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    models = {
        "RequestsGet": RequestsGet(),
        "WineDB": WineDB(),
        "ExitConversation": ExitConversation(memory),
        "Text2Image": Text2Image("cuda"),
        "ImageEditing": ImageEditing("cuda"),
        "InstructPix2Pix": InstructPix2Pix("cuda"),
        "VisualQuestionAnswering": VisualQuestionAnswering("cuda"),
    }

    for _, instance in models.items():
        for e in dir(instance):
            if e.startswith("inference"):
                func = getattr(instance, e)
                tools.append(
                    Tool(name=func.name, description=func.description, func=func)
                )

    handle_models: Dict[FileType, str] = {
        FileType.IMAGE: ImageCaptioning("cuda"),
    }

    handler = Handler(
        handle_func={
            file_type: model.inference for file_type, model in handle_models.items()
        }
    )

    return (
        initialize_agent(
            tools,
            llm,
            agent="chat-conversational-react-description",
            verbose=True,
            memory=memory,
            agent_kwargs={
                "system_message": AWESOMEGPT_PREFIX,
                "human_message": AWESOMEGPT_SUFFIX,
            },
        ),
        handler,
    )
