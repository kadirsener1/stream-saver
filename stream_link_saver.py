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
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Response Status: {response.status_code}, URL: {response.url}")
        
        # Response'tan m3u8 URL'sini çıkar
        m3u8_url = extract_m3u8_url(response)
        
        if not m3u8_url:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✗ m3u8 URL bulunamadı")
            print(f"Response (first 500 chars): {response.text[:500]}")
            return
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✓ m3u8 URL bulundu: {m3u8_url[:100]}...")
        
        # m3u8 URL'den playlist'i çek
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] → m3u8 playlist çekiliyor...")
        m3u8_response = requests.get(m3u8_url, timeout=TIMEOUT, verify=False)
        m3u8_content = m3u8_response.text.strip()
        
        if not m3u8_content.startswith('#EXTM3U'):
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✗ m3u8 geçersiz format")
            return
        
        # m3u dosyasına yaz
        with open(OUTPUT_FILE, "w") as f:
            f.write(m3u8_content + "\n")
        
        # İstatistik
        segments = len(re.findall(r'\.ts\n', m3u8_content))
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✓ Playlist kaydedildi ({segments} segment)")
        
    except requests.exceptions.ConnectionError as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✗ Sunucuya bağlanılamadı: {e}")
    except requests.exceptions.Timeout:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✗ Timeout: {TIMEOUT}s")
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✗ Hata: {type(e).__name__}: {e}")

if __name__ == "__main__":
    get_and_save_stream()
