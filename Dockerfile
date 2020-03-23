FROM node:buster as builder

RUN mkdir -p /opt/app
COPY ./app /opt/app
WORKDIR /opt/app
RUN yarn install && yarn build


FROM python:3-buster
RUN apt-get update && \
    apt-get install -y python python-dev libffi-dev gcc make python-pip bash && \
    pip install pipenv

RUN mkdir -p /opt/server
RUN mkdir -p /opt/server/app/build
WORKDIR /opt/server

COPY ./web.py /opt/server
COPY ./main.py /opt/server
COPY ./Pipfile  /opt/server
COPY ./Pipfile.lock /opt/server
COPY ./engine.py /opt/server
COPY ./start.sh /opt/server
COPY --from=builder /opt/app/build /opt/server/app/build


RUN pipenv install

EXPOSE 8080
EXPOSE 6000
CMD ["./start.sh"]
