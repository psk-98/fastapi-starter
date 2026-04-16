FROM python:3.12-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# define in docker compose
ARG port=8000

WORKDIR /code

COPY ./uv.lock /code/uv.lock
COPY ./pyproject.toml /code/pyproject.toml

RUN uv sync

COPY . /code/

CMD [ "uv", "run", "fastapi","run", "app/main.py","--port", "8000" ]
