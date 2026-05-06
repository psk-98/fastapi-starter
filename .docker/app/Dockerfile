FROM python:3.12-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# define in docker compose
ARG port=8000

WORKDIR /code

COPY ./uv.lock /code/uv.lock
COPY ./pyproject.toml /code/pyproject.toml
RUN uv sync

COPY . /code/

COPY ./.docker/app/entrypoint /entrypoint
RUN chmod +x /entrypoint

COPY ./.docker/app/start /start
RUN chmod +x /start

COPY ./.docker/app/start-celery-worker /start-celery-worker
RUN chmod +x /start-celery-worker

COPY ./.docker/app/start-flower /start-flower
RUN chmod +x /start-flower

ENTRYPOINT [ "/entrypoint" ]

# CMD [ "uv", "run", "fastapi","run", "app/main.py","--port", "8000" ]
