const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

// Orijinal Vavoo Android uygulamasının kabul ettiği UUID/Cihaz ID formatı
function makeVavooDeviceId() {
    const s4 = () => Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);
    // Genellikle 8-4-4-4-12 karakterli standart ama tamamen küçük harf/rakam bazlı UUID şablonu
    return `${s4()}${s4()}-${s4()}-${s4()}-${s4()}-${s4()}${s4()}${s4()}`;
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
        const deviceId = makeVavooDeviceId();
        
        // Uygulamanın doğrudan kabul ettiği en sade ve onaylı parametreler
        const payload = {
            version: "2.6",
            service: "vavoo",
            device: "android",
            id: deviceId,
            hardware: "premium", // "Invalid Request" hatasını bypass eden kritik değer
            rules: ["no-premium"]
        };

        const authResponse = await fetch("https://www.vavoo.tv/api/app/ping", {
            method: "POST",
            headers: {
                "Host": "www.vavoo.tv",
                "User-Agent": "VAVOO/2.6",
                "Accept": "application/json",
                "Content-Type": "application/json; charset=utf-8",
                "Connection": "Keep-Alive"
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

        // Vavoo bazen objeyi doğrudan verir, bazen de bir dizi (array) içinde döner. İkisini de kontrol ediyoruz.
        let token = null;
        if (authData && typeof authData === 'object') {
            token = authData.signed || (authData[0] ? authData[0].signed : null);
        }

        if (!token) {
            return res.status(500).send(`Vavoo isteği kabul etti (200) ama token dönmedi. Yanıt: ${responseText}`);
        }

        // Linki imzala ve yönlendir
        const separator = targetUrl.includes('?') ? '&' : '?';
        // b=1 ve n=1 parametreleri akışın kopmasını engeller
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
