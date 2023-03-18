FROM nvidia/cuda:11.7.0-runtime-ubuntu20.04
WORKDIR /app/

RUN \
  apt-get update && \
  apt-get install -y python3 python3-pip
RUN apt-get install uvicorn -y

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["sleep", "infinity"]
# ENTRYPOINT ["python3", "-m", "uvicorn", "main:app", "--reload", "--host=0.0.0.0", "--port=8000"]