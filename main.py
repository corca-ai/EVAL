from typing import Dict, List, TypedDict
import re

from fastapi import FastAPI
from pydantic import BaseModel

from s3 import upload
from env import settings

from prompts.error import ERROR_PROMPT
from agents.manager import AgentManager
from tools.base import BaseToolSet
from tools.cpu import (
    Terminal,
    CodeEditor,
    RequestsGet,
    WineDB,
)
from tools.gpu import (
    ImageEditing,
    InstructPix2Pix,
    Text2Image,
    VisualQuestionAnswering,
)
from handlers.base import BaseHandler, FileHandler, FileType
from handlers.image import ImageCaptioning
from handlers.dataframe import CsvToDataframe

app = FastAPI()


toolsets: List[BaseToolSet] = [
    Terminal(),
    CodeEditor(),
    RequestsGet(),
    Text2Image("cuda"),
    ImageEditing("cuda"),
    InstructPix2Pix("cuda"),
    VisualQuestionAnswering("cuda"),
]

handlers: Dict[FileType, BaseHandler] = {
    FileType.IMAGE: ImageCaptioning("cuda"),
    FileType.DATAFRAME: CsvToDataframe(),
}

if settings["WINEDB_HOST"] and settings["WINEDB_PASSWORD"]:
    toolsets.append(WineDB())

agent_manager = AgentManager.create(toolsets=toolsets)
file_handler = FileHandler(handlers=handlers)


class Request(BaseModel):
    key: str
    query: str
    files: List[str]


class Response(TypedDict):
    response: str
    files: List[str]


@app.get("/")
async def index():
    return {"message": f"Hello World. I'm {settings['BOT_NAME']}."}


@app.post("/command")
async def command(request: Request) -> Response:
    query = request.query
    files = request.files
    session = request.key

    print("=============== Running =============")
    print("Inputs:", query, files)
    executor = agent_manager.get_or_create_executor(session)

    print("======>Previous memory:\n %s" % executor.memory)

    promptedQuery = "\n".join([file_handler.handle(file) for file in files])
    promptedQuery += query
    print("======>Prompted Text:\n %s" % promptedQuery)

    try:
        res = executor({"input": promptedQuery})
    except Exception as e:
        try:
            res = executor(
                {
                    "input": ERROR_PROMPT.format(promptedQuery=promptedQuery, e=str(e)),
                }
            )
        except Exception as e:
            return {"response": str(e), "files": []}

    images = re.findall("(image/\S*png)", res["output"])
    dataframes = re.findall("(dataframe/\S*csv)", res["output"])

    return {
        "response": res["output"],
        "files": [upload(image) for image in images]
        + [upload(dataframe) for dataframe in dataframes],
    }
