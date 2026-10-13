from flask import Flask, request, jsonify
import datetime
import json

app = Flask(__name__)

RAW_LOG_FILE = "grafana_raw.log"
PROCESSED_FILE = "grafana_parsed.json"

@app.route("/", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True, silent=True)
        

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"\n=== WEBHOOK RECEIVED at {now} ===")

        if not data:
            print("No JSON payload received")
            return jsonify({"status": "no data"}), 400

        #Логирование
        pretty_raw = json.dumps(data, indent=2, ensure_ascii=False)
        with open(RAW_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n\n===== {now} =====\n")
            f.write(pretty_raw)
                
        alerts_list = data.get("alerts", [])
        
        processed_alerts = []

        for alert in alerts_list:
            labels = alert.get("labels", {})
            
            alert_item = {
                "measurement": "alert_stat",
                "tags": {
                    "status": alert.get("status", "unknown"),
                    "alertname": labels.get("alertname", "N/A"),
                    "grafana_folder": labels.get("grafana_folder", "N/A")
                },
                "fields": {
                    "status": 1
                }
            }
            processed_alerts.append(alert_item)

        print(f"Processed {len(processed_alerts)} alerts.")
        
        # Упаковываем в JSON и сохраняем
        if processed_alerts:
            processed_json = json.dumps(processed_alerts, indent=2, ensure_ascii=False)
            
            with open(PROCESSED_FILE, "a", encoding="utf-8") as f:
                f.write(processed_json + "\n") # Добавляем перенос строки для читаемости

        print("==================================================\n")

        return jsonify({"status": "ok", "processed_count": len(processed_alerts)}), 200

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def health():
    return "Webhook server is running", 200


if __name__ == "__main__":
    print("🚀 Starting Grafana webhook listener on port 9000...")
    app.run(host="0.0.0.0", port=9000)