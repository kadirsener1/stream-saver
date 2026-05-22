FROM python:3.11-alpine

WORKDIR /app

RUN pip install --no-cache-dir requests

COPY stream_link_saver.py .
COPY entrypoint.sh .

RUN mkdir -p /data && chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
