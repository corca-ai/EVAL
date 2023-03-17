from typing import List, TypedDict, Callable
import re

from langchain.agents import load_tools
from langchain.agents.initialize import initialize_agent
from langchain.agents.tools import Tool


from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from s3 import upload

from llm import ChatOpenAI
from file import handle
from utils import (
    AWESOMEGPT_PREFIX,
    AWESOMEGPT_SUFFIX,
    ERROR_PROMPT,
)
from tools import AWESOME_MODEL, memory

load_dotenv()


app = FastAPI()


print("Initializing AwesomeGPT")
llm = ChatOpenAI(temperature=0)
tools = [
    *load_tools(
        ["python_repl", "serpapi", "wikipedia", "bing-search"],
        llm=llm,
    ),
]

for class_name, instance in AWESOME_MODEL.items():
    for e in dir(instance):
        if e.startswith("inference"):
            func = getattr(instance, e)
            tools.append(Tool(name=func.name, description=func.description, func=func))

agent = initialize_agent(
    tools,
    llm,
    agent="chat-conversational-react-description",
    verbose=True,
    memory=memory,
    agent_kwargs={
        "system_message": AWESOMEGPT_PREFIX,
        "human_message": AWESOMEGPT_SUFFIX,
    },
)


class Request(BaseModel):
    text: str
    state: List[str]
    files: List[str]
    key: str


class Response(TypedDict):
    text: str
    response: str
    additional: List[str]


@app.get("/")
async def index():
    return {"message": "Hello World"}


@app.post("/command")
async def command(request: Request) -> Response:
    text = request.text
    state = request.state
    files = request.files
    key = request.key

    print("=============== Running =============")
    print("Inputs:", text, state, files)
    # TODO - add state to memory (use key)

    print("======>Previous memory:\n %s" % agent.memory)

    promptedText = ""

    for i, file in enumerate(files):
        promptedText += handle(file)(i + 1, file)

    promptedText += text

    print("======>Prompted Text:\n %s" % promptedText)

    try:
        res = agent({"input": promptedText})
    except Exception as e:
        try:
            res = agent(
                {
                    "input": ERROR_PROMPT.format(promptedText=promptedText, e=str(e)),
                }
            )
        except Exception as e:
            return {"text": promptedText, "response": str(e), "additional": []}

    images = re.findall("(image/\S*png)", res["output"])

    return {
        "text": promptedText,
        "response": res["output"],
        "additional": [upload(image) for image in images],
    }
