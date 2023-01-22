FROM python:3.10-slim-buster

WORKDIR app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY src src
COPY __main__.py __main__.py
CMD ["python3", "-u", "__main__.py"]
