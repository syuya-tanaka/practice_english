FROM python:3.10.6
ENV PYTHONUNBUFFERED=1
WORKDIR /code

COPY . /code
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
