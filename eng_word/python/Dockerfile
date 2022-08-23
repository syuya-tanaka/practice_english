FROM python:3.9.2-slim-buster AS builder
# FROM python:3.10.6-slim-buster
# 本当はpython:3.10.6-slim-busterを使いたかったが、
# distroless/python-debian11がpython3.9.2の為、止むを得ず。
ENV PYTHONUNBUFFERED=1
WORKDIR /code

COPY . /code
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

FROM gcr.io/distroless/python3-debian11
COPY --from=builder /code /code
WORKDIR /code
CMD ["/code/answer_eng.py"]