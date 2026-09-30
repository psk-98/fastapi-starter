FROM oven/bun:1 AS emails-build
WORKDIR /src
COPY package.json ./package.json
COPY packages/react-email/package.json ./packages/react-email/package.json
RUN bun install
COPY ./packages/react-email ./packages/react-email
RUN bun run --filter emails export


FROM python:3.12-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# define in docker compose
ARG port=8000

WORKDIR /code

COPY ./uv.lock /code/uv.lock
COPY ./pyproject.toml /code/pyproject.toml
RUN uv sync

COPY . /code/

# Email templates rendered at build time from the React Email sources
COPY --from=emails-build /src/app/email_templates/build /code/app/email_templates/build

COPY ./.docker/app/entrypoint /entrypoint
RUN chmod +x /entrypoint

COPY ./.docker/app/start /start
RUN chmod +x /start

COPY ./.docker/app/start-celery-worker /start-celery-worker
RUN chmod +x /start-celery-worker

COPY ./.docker/app/start-flower /start-flower
RUN chmod +x /start-flower

ENTRYPOINT [ "/entrypoint" ]
