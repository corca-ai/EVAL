import os
import re
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, List, TypedDict

import uvicorn
from fastapi import FastAPI, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pydantic import BaseModel

from core.agents.manager import AgentManager
from core.handlers.base import BaseHandler, FileHandler, FileType
from core.handlers.dataframe import CsvToDataframe
from core.tools.base import BaseToolSet
from core.tools.cpu import ExitConversation, RequestsGet
from core.tools.editor import CodeEditor
from core.tools.terminal import Terminal
from core.upload import StaticUploader
from env import settings

app = FastAPI()


BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(BASE_DIR / settings["PLAYGROUND_DIR"])

uploader = StaticUploader.from_settings(
    settings, path=BASE_DIR / "static", endpoint="static"
)
app.mount("/static", StaticFiles(directory=uploader.path), name="static")

templates = Jinja2Templates(directory=BASE_DIR / "api" / "templates")

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
file_handler = FileHandler(handlers=handlers, path=BASE_DIR)


class ExecuteRequest(BaseModel):
    session: str
    prompt: str
    files: List[str]


class ExecuteResponse(TypedDict):
    answer: str
    files: List[str]


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.post("/upload")
async def create_upload_file(files: List[UploadFile]):
    urls = []
    for file in files:
        extension = "." + file.filename.split(".")[-1]
        with NamedTemporaryFile(suffix=extension) as tmp_file:
            tmp_file.write(file.file.read())
            tmp_file.flush()
            urls.append(uploader.upload(tmp_file.name))
    return {"urls": urls}


@app.post("/api/execute")
async def execute(request: ExecuteRequest) -> ExecuteResponse:
    query = request.prompt
    files = request.files
    session = request.session

    executor = agent_manager.get_or_create_executor(session)

    promptedQuery = "\n".join([file_handler.handle(file) for file in files])
    promptedQuery += query

    try:
        res = executor({"input": promptedQuery})
    except Exception as e:
        return {"answer": str(e), "files": []}

    files = re.findall(r"\[file/\S*\]", res["output"])
    files = [file[1:-1] for file in files]

    return {
        "answer": res["output"],
        "files": [uploader.upload(file) for file in files],
    }


def serve():
    uvicorn.run("api.main:app", host="0.0.0.0", port=settings["EVAL_PORT"])


def dev():
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=settings["EVAL_PORT"],
        reload=True,
        reload_dirs=[BASE_DIR / "core", BASE_DIR / "api"],
    )
