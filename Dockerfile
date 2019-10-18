FROM node:alpine as builder

RUN mkdir -p /opt/app
COPY ./app /opt/app
WORKDIR /opt/app
RUN npm install -g yarn && yarn build


FROM python:2.7-alpine
RUN apk update && \
    apk add python python-dev libffi-dev gcc make musl-dev py-pip mysql-client jpeg-dev zlib-dev npm bash && \
    pip install pipenv

RUN mkdir -p /opt/server
RUN mkdir -p /opt/server/app/build

COPY ./web.py /opt/server
COPY ./vector.py /opt/server
COPY ./main.py /opt/server
COPY ./Pipfile  /opt/server
COPY ./Pipfile.lock /opt/server
COPY ./engine.py /opt/server
COPY ./start.sh /opt/server
COPY --from=builder /opt/app/build /opt/server/app/build

WORKDIR /opt/server
RUN pipenv install

EXPOSE 8080
EXPOSE 6000
CMD ["./start.sh"]
