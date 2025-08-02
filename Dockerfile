FROM python:3.11-alpine

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD [ "uvicorn",  "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload" ]

