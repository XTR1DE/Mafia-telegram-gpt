FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install requirements.txt

COPY . .

CMD ["py", "bot.py"]