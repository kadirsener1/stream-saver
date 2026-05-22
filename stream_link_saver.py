#!/usr/bin/env python3
import requests
from datetime import datetime
import os
import urllib3
import re

# SSL uyarılarını devre dışı bırak
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Ortam değişkenlerinden ayarları oku
STREAM_URL = os.getenv("STREAM_URL", "http://127.0.0.1:6878/ace/getstream?id=9bc4c83abc04cb94a885e9de9a88aef98285d564&pid=7561")
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "/data/streams.m3u")
TIMEOUT = int(os.getenv("TIMEOUT", "5"))

def get_and_save_stream():
    try:
        response = requests.get(STREAM_URL, timeout=TIMEOUT, verify=False)
        playlist_content = response.text.strip()
        
        # Eğer response bir playlist ise direkt kaydet
        if playlist_content.startswith("#EXTM3U"):
            # m3u dosyasını başlat
            if not os.path.exists(OUTPUT_FILE):
                with open(OUTPUT_FILE, "w") as f:
                    f.write("#EXTM3U\n")
            
            # m3u8 playlist'ini direkt dosyaya yaz
            with open(OUTPUT_FILE, "w") as f:
                f.write(playlist_content + "\n")
            
            # Kaç tane segment olduğunu say
            segments = len(re.findall(r'\.ts\n', playlist_content))
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✓ Playlist kaydedildi ({segments} segment)")
        
        # Eğer response bir URL ise (.m3u8 ile bitiyorsa)
        elif playlist_content.endswith('.m3u8'):
            # URL'den playlist'i çek
            m3u8_response = requests.get(playlist_content, timeout=TIMEOUT, verify=False)
            m3u8_content = m3u8_response.text.strip()
            
            # m3u dosyasını başlat
            if not os.path.exists(OUTPUT_FILE):
                with open(OUTPUT_FILE, "w") as f:
                    f.write("#EXTM3U\n")
            
            # m3u8 playlist'ini direkt dosyaya yaz
            with open(OUTPUT_FILE, "w") as f:
                f.write(m3u8_content + "\n")
            
            # Kaç tane segment olduğunu say
            segments = len(re.findall(r'\.ts\n', m3u8_content))
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✓ m3u8 URL çekilen playlist kaydedildi ({segments} segment)")
            print(f"    URL: {playlist_content[:80]}...")
        
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✗ Bilinmeyen format: {playlist_content[:100]}")
        
    except requests.exceptions.ConnectionError:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✗ Sunucuya bağlanılamadı: {STREAM_URL}")
    except requests.exceptions.Timeout:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✗ Timeout: {TIMEOUT}s")
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✗ Hata: {e}")

if __name__ == "__main__":
    get_and_save_stream()
