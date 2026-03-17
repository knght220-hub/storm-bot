import requests
import time
from datetime import datetime

API_KEY = "d510fd82a5bf5e322924208d7a5b48c3"

TORNADO_WEBHOOK = "https://discord.com/api/webhooks/1483534093919457413/JReTKaJribWIkkULZ0VHRESx76fwUKq0w83PsU1S-VjN54e46BPBlcEa8Kh1VDGeCVgK"
HURRICANE_WEBHOOK = "https://discord.com/api/webhooks/1483534194310254593/WMBnzfOlA2iBq3tv9F_4s9JclgLms05d2juzwVzoP23nMiEGXwY-xclzizQ9ooWptr7T"

sent_alerts = set()

def get_alerts():
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat=0&lon=0&appid={API_KEY}"
    res = requests.get(url)
    data = res.json()
    return data.get("alerts", [])

def send_embed(webhook, title, description, source):
    embed = {
        "title": title,
        "description": description[:2000],
        "color": 16711680,
        "fields": [
            {"name": "Source", "value": source, "inline": True},
            {"name": "Time", "value": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}
        ]
    }

    requests.post(webhook, json={"embeds": [embed]})

def process_alerts(alerts):
    for alert in alerts:
        alert_id = alert.get("event") + alert.get("start", "")

        if alert_id in sent_alerts:
            continue

        event = alert.get("event", "").lower()
        desc = alert.get("description", "No details.")
        sender = alert.get("sender_name", "Unknown")

        if "tornado" in event:
            send_embed(
                TORNADO_WEBHOOK,
                "🌪️ Tornado Warning",
                desc,
                sender
            )
            sent_alerts.add(alert_id)

        elif "cyclone" in event or "hurricane" in event or "typhoon" in event:
            send_embed(
                HURRICANE_WEBHOOK,
                "🌀 Tropical Cyclone Alert",
                desc,
                sender
            )
            sent_alerts.add(alert_id)

def main():
    print("Bot running...")

    while True:
        try:
            alerts = get_alerts()
            process_alerts(alerts)
        except Exception as e:
            print("Error:", e)

        time.sleep(300)  # 5 minutes

main()