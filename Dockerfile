FROM python:3.10.6-slim-buster AS base
ENV PYTHONUNBUFFERED=true
WORKDIR /app
RUN apt update && apt install -y libraqm-dev && apt clean && rm -rf /var/cache/apt/lists

FROM base as poetry
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH="$POETRY_HOME/bin:$PATH"
RUN python -c 'from urllib.request import urlopen; print(urlopen("https://install.python-poetry.org").read().decode())' | python -
COPY . ./
RUN poetry install --no-interaction --no-ansi -vvv

FROM base as runtime
ENV PATH="/app/.venv/bin:$PATH"
COPY --from=poetry /app /app
COPY fonts fonts
COPY image_generators image_generators
COPY images images
COPY dashboard.py dashboard.py
COPY image_translate.py image_translate.py
CMD python dashboard.py