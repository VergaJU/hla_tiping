FROM python:3.8-slim-buster


WORKDIR /app
RUN /usr/local/bin/python -m pip install --upgrade pip

RUN pip install pandas

COPY aggregate.py .
RUN chmod +x aggregate.py
ENV PATH /app:$PATH