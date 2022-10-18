FROM python:3.10-slim-buster

RUN apt-get update && \
    apt-get install -y locales && \
    sed -i -e 's/# en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen && \
    locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

WORKDIR app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY src .
CMD ["python3", "-u", "app.py"]
