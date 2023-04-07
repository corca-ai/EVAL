from celery import Celery
from celery.result import AsyncResult

from api.container import agent_manager
from env import settings

celery_app = Celery(__name__)
celery_app.conf.broker_url = settings["CELERY_BROKER_URL"]
celery_app.conf.result_backend = settings["CELERY_BROKER_URL"]
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],  # Ignore other content
    result_serializer="json",
    enable_utc=True,
)


@celery_app.task(name="task_execute")
def task_execute(session: str, prompt: str):
    executor = agent_manager.get_or_create_executor(session)
    response = executor({"input": prompt})
    return {"output": response["output"]}


def get_task_result(task_id):
    return AsyncResult(task_id)


def start_worker():
    celery_app.worker_main(
        [
            "worker",
            "--loglevel=INFO",
        ]
    )