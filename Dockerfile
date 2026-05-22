FROM python:3.11-alpine

WORKDIR /app

# requirements
RUN pip install --no-cache-dir requests

# Script ve entrypoint'i kopyala
COPY stream_link_saver.py .
COPY entrypoint.sh .

# Veri dizini
RUN mkdir -p /data && chmod +x /app/entrypoint.sh

# Default command
CMD ["/app/entrypoint.sh"]
