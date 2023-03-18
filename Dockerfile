FROM nvidia/cuda:11.7.0-runtime-ubuntu20.04
WORKDIR /app/

ENV DEBIAN_FRONTEND=noninteractive

RUN \
  apt-get update && \
  apt-get install -y software-properties-common && \
  add-apt-repository ppa:deadsnakes/ppa && \
  apt-get install -y python3.10 python3-pip curl && \
  curl -sSL https://install.python-poetry.org | python3 -

ENV PATH "/root/.local/bin:$PATH"

COPY pyproject.toml .
COPY poetry.lock .

RUN poetry env use 3.10
RUN poetry install --with tools

COPY . .

ENTRYPOINT ["poetry", "run", "python3", "-m", "uvicorn", "main:app", "--reload", "--host=0.0.0.0", "--port=8000"]