FROM python:3.6
WORKDIR /app

COPY ./requirements.txt /app

RUN mkdir -p logs
RUN mkdir -p temp
RUN pip install -r requirements.txt

COPY . /app/

EXPOSE  4567
CMD     ["python", "main.py", "dev"]