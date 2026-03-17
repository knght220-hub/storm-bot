import os
import requests
import time
from datetime import datetime, timezone

# Load secrets from Railway Shared Variables
API_KEY = os.environ["API_KEY"]
TORNADO_WEBHOOK = os.environ["TORNADO_WEBHOOK"]
HURRICANE_WEBHOOK = os.environ["HURRICANE_WEBHOOK"]

# Keep track of already sent alerts (avoid duplicates)
sent_alerts = set()

def get_alerts():
    """Fetch global weather alerts from OpenWeather."""
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat=0&lon=0&appid={API_KEY}"
    try:
        res = requests.get(url)
        data = res.json()
        return data.get("alerts", [])
    except Exception as e:
        print("Error fetching alerts:", e)
        return []

def send_embed(webhook, title, description, source):
    """Send a professional-looking embed to Discord."""
    embed = {
        "title": title,
        "description": description[:2000],
        "color": 16711680,
        "fields": [
            {"name": "Source", "value": source, "inline": True},
            {"name": "Time", "value": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}
        ]
    }
    try:
        requests.post(webhook, json={"embeds": [embed]})
    except Exception as e:
        print(f"Error sending embed to {webhook}: {e}")

def process_alerts(alerts):
    """Check alerts and send to appropriate Discord webhook."""
    for alert in alerts:
        alert_id = alert.get("event", "") + str(alert.get("start", ""))
        if alert_id in sent_alerts:
            continue  # skip duplicates

        event = alert.get("event", "").lower()
        desc = alert.get("description", "No details provided.")
        sender = alert.get("sender_name", "Unknown Source")

        # Tornado alerts
        if "tornado" in event:
            send_embed(TORNADO_WEBHOOK, "🌪️ Tornado Warning", desc, sender)
            sent_alerts.add(alert_id)

        # Hurricane / cyclone alerts
        elif "cyclone" in event or "hurricane" in event or "typhoon" in event:
            send_embed(HURRICANE_WEBHOOK, "🌀 Tropical Cyclone Alert", desc, sender)
            sent_alerts.add(alert_id)

def main():
    print("Storm bot running...")

    while True:
        try:
            alerts = get_alerts()
            process_alerts(alerts)
        except Exception as e:
            print("Error in main loop:", e)

        time.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    main()
