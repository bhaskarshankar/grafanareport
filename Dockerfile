FROM python:alpine3.7

RUN apk add --update --no-cache curl py-pip \
&& pip install --upgrade pip


# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

ENTRYPOINT [ "python" ]

CMD [ "webconsole.py" ]