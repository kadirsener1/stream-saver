const express = require('express');
const axios = require('axios');
const app = express();
const PORT = process.env.PORT || 3000;

app.get('/oynat', async (req, res) => {
    const targetUrl = req.query.url;
    if (!targetUrl) return res.status(400).send("Hata: url eksik.");

    try {
        // Axios ile gerçek bir cihaz gibi istek atıyoruz
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
                'Content-Type': 'application/json'
            }
        });

        const token = response.data.signed || (response.data[0] ? response.data[0].signed : null);

        if (!token) {
            return res.status(500).send("Token alınamadı: " + JSON.stringify(response.data));
        }

        const separator = targetUrl.includes('?') ? '&' : '?';
        const signedUrl = `${targetUrl}${separator}n=1&b=1&vavoo_auth=${token}`;

        // Oynatıcıyı yönlendir
        res.redirect(302, signedUrl);

    } catch (error) {
        res.status(500).send("Proxy Hatası: " + error.message);
    }
});

app.listen(PORT, () => console.log(`Proxy ${PORT} portunda aktif.`));
