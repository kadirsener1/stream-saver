import requests
from datetime import datetime

url = "http://127.0.0.1:6878/ace/getstream?id=9bc4c83abc04cb94a885e9de9a88aef98285d564&pid=7561"

try:
    response = requests.get(url, timeout=5)
    stream_link = response.text.strip()
    
    # m3u başlığı varsa kontrol et
    with open("streams.m3u", "r") as f:
        content = f.read()
    
    if "#EXTM3U" not in content:
        with open("streams.m3u", "w") as f:
            f.write("#EXTM3U\n")
    
    # Linki m3u formatında kaydet
    with open("streams.m3u", "a") as f:
        f.write(f"#EXTINF:-1, Stream ({datetime.now().strftime('%H:%M:%S')})\n")
        f.write(f"{stream_link}\n")
    
    print(f"✓ Link kaydedildi: {stream_link}")
except requests.exceptions.ConnectionError:
    print("✗ Sunucuya bağlanılamadı")
except Exception as e:
    print(f"✗ Hata: {e}")
