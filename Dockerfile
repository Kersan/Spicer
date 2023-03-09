FROM python:3.11-slim

WORKDIR /app

RUN apt update
RUN apt install -y git

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD ["python", "start.py"]