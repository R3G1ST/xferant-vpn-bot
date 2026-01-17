const tg = window.Telegram.WebApp;

function sendAction(action) { 
    tg.sendData(JSON.stringify({ action })); 
}

function showLink(link) {
    document.getElementById("link").innerHTML = "🔒 Ваша конфигурация Xferant VPN:<br><code>" + link + "</code>";
    QRCode.toCanvas(document.getElementById("qr"), link, { 
        width: 180,
        colorDark: "#00ff88",
        colorLight: "#1a1a1a"
    });
}

window.Telegram.WebApp.onEvent("web_app_data_sent", function(response) {
    if(response.text) showLink(response.text);
});

// Расширяем Telegram Web App на весь экран
tg.expand();
tg.setHeaderColor("#1a1a1a");
tg.setBackgroundColor("#1a1a1a");
