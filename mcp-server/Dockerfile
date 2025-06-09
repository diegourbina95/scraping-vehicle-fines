FROM python:3.13.3
WORKDIR /app

COPY ./requirements.txt /app

RUN mkdir -p logs
RUN mkdir -p temp
RUN pip install -r requirements.txt

COPY . /app/

EXPOSE  4200