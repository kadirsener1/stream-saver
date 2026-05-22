#!/usr/bin/env python3
import requests
from datetime import datetime
import os
import urllib3
import re

# SSL uyarılarını devre dışı bırak
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Ortam değişkenlerinden ayarları oku
STREAM_URL = os.getenv("STREAM_URL", "https://vavooproxy.magnitude.workers.dev/resolve?url=https://vavoo.to/vavoo-iptv/play/38229012391e140a7f75ba")
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "/data/streams.m3u")
CHANNEL_NAME = os.getenv("CHANNEL_NAME", "Stream")
CHANNEL_ID = os.getenv("CHANNEL_ID", "channel.1")
CHANNEL_LOGO = os.getenv("CHANNEL_LOGO", "")
CHANNEL_GROUP = os.getenv("CHANNEL_GROUP", "General")
TIMEOUT = int(os.getenv("TIMEOUT", "5"))

def extract_m3u8_url(response):
    """Response'tan m3u8 URL'sini çıkar"""
    
    # 1. Final URL redirect URL ise (location header)
    if hasattr(response, 'url') and '.m3u8' in response.url:
        return response.url
    
    # 2. HTML/Text içinde m3u8 URL ara
    text = response.text
    patterns = [
        r'(https?://[a-zA-Z0-9\-\.]+/[^\s"\'<>]*\.m3u8[^\s"\'<>]*)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if '.m3u8' in match:
                return match
    
    # 3. History'de redirect URL'leri kontrol et
    if hasattr(response, 'history'):
        for resp in response.history:
            if 'location' in resp.headers:
                loc = resp.headers.get('location', '')
                if '.m3u8' in loc:
                    return loc
    
    return None

def get_and_save_stream():
    try:
        # İlk request - proxy URL'den response al
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] → Proxy URL taranıyor...")
        response = requests.get(STREAM_URL, timeout=TIMEOUT, verify=False, allow_redirects=True)
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Response Status: {response.status_code}")
        
        # Response'tan m3u8 URL'sini çıkar
        m3u8_url = extract_m3u8_url(response)
        
        if not m3u8_url:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✗ m3u8 URL bulunamadı")
            return
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✓ m3u8 URL bulundu")
        
        # m3u dosyasını oluştur (basit format)
        logo_attr = f' tvg-logo="{CHANNEL_LOGO}"' if CHANNEL_LOGO else ''
        extinf_line = f"#EXTINF:-1 tvg-id=\"{CHANNEL_ID}\"{logo_attr} group-title=\"{CHANNEL_GROUP}\",{CHANNEL_NAME}"
        
        with open(OUTPUT_FILE, "w") as f:
            f.write("#EXTM3U\n")
            f.write(f"{extinf_line}\n")
            f.write(f"{m3u8_url}\n")
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✓ M3U dosyası kaydedildi")
        print(f"    Kanal: {CHANNEL_NAME}")
        print(f"    URL: {m3u8_url[:80]}...")
        
    except requests.exceptions.ConnectionError as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✗ Sunucuya bağlanılamadı: {e}")
    except requests.exceptions.Timeout:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✗ Timeout: {TIMEOUT}s")
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✗ Hata: {type(e).__name__}: {e}")

if __name__ == "__main__":
    get_and_save_stream()
