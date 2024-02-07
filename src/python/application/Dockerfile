FROM scratch
# pull official base image
FROM python:3.12.1 as builder

EXPOSE 8000

# set work directory
WORKDIR /usr/src/app

# set environment variablesdoc
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN python -m venv /opt/venv
RUN apt-get update
RUN apt-get update -y
# Enable venv
ENV PATH="/opt/venv/bin:$PATH"

RUN python -m pip install --upgrade pip
COPY requirements.txt .
COPY constraints.txt .
# install dependencies
RUN python -m pip install -r requirements.txt -c constraints.txt
COPY . .


CMD [ "python", "./manage.py", "runserver", "0.0.0.0:8000"]