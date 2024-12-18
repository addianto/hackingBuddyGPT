FROM docker.io/library/python:3.12.8-alpine

ARG USER_NAME=buddy
ARG USER_UID=1000

RUN apk update && \
    apk add --no-cache build-base cargo rust openssh

RUN adduser -u $USER_UID -D $USER_NAME

USER $USER_NAME

WORKDIR /opt/app

COPY --chown=$USER_NAME:$USER_NAME . .

RUN export PATH="$HOME/.local/bin:$PATH" && \
    mkdir -p /opt/app/log && \
    pip install --no-cache-dir -e .

VOLUME /opt/app/log

ENTRYPOINT ["python", "src/hackingBuddyGPT/cli/wintermute.py"]