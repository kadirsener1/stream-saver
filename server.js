const express = require('express');
const axios = require('axios');
const app = express();
const PORT = process.env.PORT || 3000;

// Sunucunun çalışıp çalışmadığını test etmek için ANA SAYFA (Sorunu anlamaya yardımcı olur)
app.get('/', (req, res) => {
    res.send("Vavoo Proxy Sunucusu Aktif ve Çalışıyor! Kullanım: /oynat?url=VAVOO_LINKI");
});

// Canlı yayın yönlendirme rotası
app.get('/oynat', async (req, res) => {
    // URL parametresini alıyoruz
    const targetUrl = req.query.url;
    
    if (!targetUrl) {
        return res.status(400).send("Hata: 'url' parametresi eksik! Örnek: /oynat?url=https://vavoo...");
    }

    try {
        // Vavoo API'sine istek atma
        const response = await axios.post('https://www.vavoo.tv/api/app/ping', {
            version: "2.6",
            service: "vavoo",
            device: "android",
            id: Math.random().toString(36).substring(2, 15),
            hardware: "arm64-v8a",
            rules: ["no-premium"]
        }, {
            headers: {
                'User-Agent': 'VAVOO/2.6 (Linux;Android 10)',
                'Content-Type': 'application/json; charset=utf-8'
            }
        });

        // Gelen veriden token çekme
        const token = response.data.signed || (response.data[0] ? response.data[0].signed : null);

        if (!token) {
            return res.status(500).send("Vavoo'dan cevap geldi ama token alınamadı. Gelen veri: " + JSON.stringify(response.data));
        }

        // Linki imzalama
        const separator = targetUrl.includes('?') ? '&' : '?';
        const signedUrl = `${targetUrl}${separator}n=1&b=1&vavoo_auth=${token}`;

        // Oynatıcıyı yeni linke 302 ile yönlendir
        res.redirect(302, signedUrl);

    } catch (error) {
        res.status(500).send("Proxy Sunucu Hatası: " + error.message);
    }
});

// Kalan tüm hatalı istekler için yakalayıcı (Neden hata aldığınızı yazar)
app.use((req, res) => {
    res.status(404).send(`Hata: Girdiğiniz '${req.originalUrl}' yolu sunucuda bulunamadı. Lütfen /oynat?url=... şeklinde kullanın.`);
});

app.listen(PORT, () => console.log(`Proxy ${PORT} portunda aktif.`));
