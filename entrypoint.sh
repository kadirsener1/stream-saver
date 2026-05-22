#!/bin/sh
# Komut dosyasını her 5 dakikada bir çalıştır
while true; do
    python3 /app/stream_link_saver.py
    sleep 300
done
