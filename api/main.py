import re
from typing import Dict, List, TypedDict

import uvicorn
from core.agents.manager import AgentManager
from core.handlers.base import BaseHandler, FileHandler, FileType
from core.handlers.dataframe import CsvToDataframe
from core.prompts.error import ERROR_PROMPT
from core.tools.base import BaseToolSet
from core.tools.cpu import ExitConversation, RequestsGet
from core.tools.editor import CodeEditor
from core.tools.terminal import Terminal
from core.upload import StaticUploader
from env import settings
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from logger import logger
from pydantic import BaseModel

app = FastAPI()

app.mount("/static", StaticFiles(directory=StaticUploader.STATIC_DIR), name="static")
uploader = StaticUploader.from_settings(settings)


toolsets: List[BaseToolSet] = [
    Terminal(),
    CodeEditor(),
    RequestsGet(),
    ExitConversation(),
]
handlers: Dict[FileType, BaseHandler] = {FileType.DATAFRAME: CsvToDataframe()}

if settings["USE_GPU"]:
    import torch
    from core.handlers.image import ImageCaptioning
    from core.tools.gpu import (
        ImageEditing,
        InstructPix2Pix,
        Text2Image,
        VisualQuestionAnswering,
    )

    if torch.cuda.is_available():
        toolsets.extend(
            [
                Text2Image("cuda"),
                ImageEditing("cuda"),
                InstructPix2Pix("cuda"),
                VisualQuestionAnswering("cuda"),
            ]
        )
        handlers[FileType.IMAGE] = ImageCaptioning("cuda")

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
