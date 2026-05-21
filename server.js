const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

// Vavoo'nun kabul ettiği standartta cihaz ID'si üreten fonksiyon
function makeDeviceId() {
    let result = '';
    const characters = '0123456789abcdef';
    for (let i = 0; i < 16; i++) {
        result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    return result;
}

app.get('/', (req, res) => {
    res.send("Vavoo Proxy Sunucusu Aktif! Kullanım: /oynat?url=VAVOO_LINKI");
});

app.get('/oynat', async (req, res) => {
    const targetUrl = req.query.url;
    
    if (!targetUrl) {
        return res.status(400).send("Hata: 'url' parametresi eksik!");
    }

    try {
        const deviceId = makeDeviceId();
        
        // 400 hatasını aşmak için Vavoo uygulamasının tam gövde (body) şablonu
        const payload = {
            version: "2.6",
            service: "vavoo",
            device: "android",
            id: deviceId,
            hardware: "骁龙625", // Yaygın bir Android işlemci adı taklidi
            rules: ["no-premium"]
        };

        // Node.js yerleşik fetch ile ham istek atıyoruz (Axios'un eklediği bazı otomatik başlıklar 400'e sebep olabilir)
        const authResponse = await fetch("https://www.vavoo.tv/api/app/ping", {
            method: "POST",
            headers: {
                "Host": "www.vavoo.tv",
                "User-Agent": "VAVOO/2.6",
                "Accept": "application/json",
                "Content-Type": "application/json; charset=utf-8",
                "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip"
            },
            body: JSON.stringify(payload)
        });

        const responseText = await authResponse.text();
        
        let authData;
        try {
            authData = JSON.parse(responseText);
        } catch (e) {
            return res.status(500).send(`Vavoo API JSON formatında dönmedi. Yanıt: ${responseText}`);
        }

        // Token kontrolü
        const token = authData.signed || (authData[0] ? authData[0].signed : null);

        if (!token) {
            return res.status(500).send(`Vavoo isteği kabul etti (200) ama token dönmedi. Yanıt: ${responseText}`);
        }

        // Linki imzala ve yönlendir
        const separator = targetUrl.includes('?') ? '&' : '?';
        const signedUrl = `${targetUrl}${separator}n=1&b=1&vavoo_auth=${token}`;

        res.redirect(302, signedUrl);

    } catch (error) {
        res.status(500).send("Proxy Sunucu Hatası: " + error.message);
    }
});

app.use((req, res) => {
    res.status(404).send("Hatalı istek yolu.");
});

app.listen(PORT, () => console.log(`Proxy ${PORT} portunda aktif.`));
