FROM python:3.9-bullseye

# get portaudio and ffmpeg
RUN apt-get update \
        && apt-get install libportaudio2 libportaudiocpp0 portaudio19-dev libasound-dev libsndfile1-dev -y
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

WORKDIR /code
COPY ./pyproject.toml /code/pyproject.toml
COPY ./poetry.lock /code/poetry.lock
RUN pip install --no-cache-dir --upgrade poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-interaction --no-ansi
COPY main.py /code/main.py
COPY survey.json /code/survey.json
COPY utils/chatbot.py /code/utils/chatbot.py
COPY utils/db.py /code/utils/db.py
COPY utils/sms.py /code/utils/sms.py


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]