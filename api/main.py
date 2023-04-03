from typing import Dict, List, TypedDict
import re
import uvicorn

import torch
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

from env import settings

from core.prompts.error import ERROR_PROMPT
from core.agents.manager import AgentManager
from core.tools.base import BaseToolSet
from core.tools.terminal import Terminal
from core.tools.editor import CodeEditor
from core.tools.cpu import (
    RequestsGet,
    WineDB,
    ExitConversation,
)
from core.tools.gpu import (
    ImageEditing,
    InstructPix2Pix,
    Text2Image,
    VisualQuestionAnswering,
)
from core.handlers.base import BaseHandler, FileHandler, FileType
from core.handlers.image import ImageCaptioning
from core.handlers.dataframe import CsvToDataframe
from core.upload import StaticUploader

from logger import logger
from ansi import ANSI, Color

app = FastAPI()

app.mount("/static", StaticFiles(directory=StaticUploader.STATIC_DIR), name="static")
uploader = StaticUploader.from_settings(settings)

use_gpu = settings["USE_GPU"] and torch.cuda.is_available()

toolsets: List[BaseToolSet] = [
    Terminal(),
    CodeEditor(),
    RequestsGet(),
    ExitConversation(),
]

if use_gpu:
    toolsets.extend(
        [
            Text2Image("cuda"),
            ImageEditing("cuda"),
            InstructPix2Pix("cuda"),
            VisualQuestionAnswering("cuda"),
        ]
    )

handlers: Dict[FileType, BaseHandler] = {}
handlers[FileType.DATAFRAME] = CsvToDataframe()
if use_gpu:
    handlers[FileType.IMAGE] = ImageCaptioning("cuda")

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

    executor = agent_manager.get_or_create_executor(session)

    promptedQuery = "\n".join([file_handler.handle(file) for file in files])
    promptedQuery += query
    logger.info(ANSI("Prompted Text").to(Color.yellow()) + f": {promptedQuery}")

    try:
        res = executor({"input": promptedQuery})
    except Exception as e:
        logger.error(f"error while processing request: {str(e)}")
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
        "files": [uploader.upload(image) for image in images]
        + [uploader.upload(dataframe) for dataframe in dataframes],
    }


def serve():
    uvicorn.run("api.main:app", host="0.0.0.0", port=settings["PORT"])
