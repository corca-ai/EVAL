import os
import re
from pathlib import Path
from typing import Dict, List

from fastapi.templating import Jinja2Templates

from core.agents.manager import AgentManager
from core.handlers.base import BaseHandler, FileHandler, FileType
from core.handlers.dataframe import CsvToDataframe
from core.tools.base import BaseToolSet
from core.tools.cpu import ExitConversation, RequestsGet
from core.tools.editor import CodeEditor
from core.tools.terminal import Terminal
from core.upload import StaticUploader
from env import settings

BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(BASE_DIR / settings["PLAYGROUND_DIR"])


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

templates = Jinja2Templates(directory=BASE_DIR / "api" / "templates")

uploader = StaticUploader.from_settings(
    settings, path=BASE_DIR / "static", endpoint="static"
)

reload_dirs = [BASE_DIR / "core", BASE_DIR / "api"]
