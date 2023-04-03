FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# System dependencies:
RUN pip install poetry

# Setup workdir
WORKDIR /code/src/microservice/

# Copy only requirements to cache them in docker layer
COPY poetry.lock pyproject.toml ./

# Project initialization:
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction

# Creating folders, and files for a project:
COPY . .
