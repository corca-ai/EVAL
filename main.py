from typing import List, TypedDict
import re

from fastapi import FastAPI
from pydantic import BaseModel
from s3 import upload

from utils import ERROR_PROMPT
from agent import get_agent


app = FastAPI()
agent, handler = get_agent()


class Request(BaseModel):
    key: str
    query: str
    files: List[str]


class Response(TypedDict):
    response: str
    files: List[str]


@app.get("/")
async def index():
    return {"message": "Hello World. I'm AwesomeGPT."}


@app.post("/command")
async def command(request: Request) -> Response:
    query = request.query
    files = request.files
    key = request.key

    print("=============== Running =============")
    print("Inputs:", query, files)
    # TODO - add state to memory (use key)

    print("======>Previous memory:\n %s" % agent.memory)

    promptedQuery = ""
    import time

    for i, file in enumerate(files):
        promptedQuery += handler.handle(i + 1, file)

    promptedQuery += query

    print("======>Prompted Text:\n %s" % promptedQuery)

    try:
        res = agent({"input": promptedQuery})
    except Exception as e:
        try:
            res = agent(
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
