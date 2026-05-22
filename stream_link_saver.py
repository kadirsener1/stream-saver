#!/usr/bin/env python3
import requests
from datetime import datetime
import os

# Ortam değişkenlerinden ayarları oku
STREAM_URL = os.getenv("STREAM_URL", "http://127.0.0.1:6878/ace/getstream?id=9bc4c83abc04cb94a885e9de9a88aef98285d564&pid=7561")
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "/data/streams.m3u")
TIMEOUT = int(os.getenv("TIMEOUT", "5"))

def get_and_save_stream():
    try:
        response = requests.get(STREAM_URL, timeout=TIMEOUT)
        stream_link = response.text.strip()
        
        # m3u dosyasını başlat (ilk kez)
        if not os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, "w") as f:
                f.write("#EXTM3U\n")
        
        # Linki m3u formatında kaydet
        with open(OUTPUT_FILE, "a") as f:
            f.write(f"#EXTINF:-1, Stream ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n")
            f.write(f"{stream_link}\n")
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✓ Link kaydedildi: {stream_link}")
        
    except requests.exceptions.ConnectionError:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✗ Sunucuya bağlanılamadı: {STREAM_URL}")
    except requests.exceptions.Timeout:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✗ Timeout: {TIMEOUT}s")
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✗ Hata: {e}")

if __name__ == "__main__":
    get_and_save_stream()
