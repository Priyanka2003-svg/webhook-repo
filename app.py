from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
from urllib.parse import quote_plus

app = Flask(__name__)

# MongoDB credentials
username = quote_plus("PriyankaDoijode")
password = quote_plus("Priyanka@953146")
mongo_uri = f"mongodb+srv://{username}:{password}@priyanka.gsqag2g.mongodb.net/?retryWrites=true&w=majority&appName=priyanka"

# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client["webhookDB"]
collection = db["github_events"]

# Webhook route
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    event_type = request.headers.get("X-GitHub-Event")
    print("✅ Webhook received!")

    entry = {}

    if event_type == "push":
        entry = {
            "type": "PUSH",
            "author": data["pusher"]["name"],
            "to_branch": data["ref"].split("/")[-1],
            "timestamp": datetime.utcnow()
        }
    elif event_type == "pull_request":
        entry = {
            "type": "PULL_REQUEST",
            "author": data["pull_request"]["user"]["login"],
            "from_branch": data["pull_request"]["head"]["ref"],
            "to_branch": data["pull_request"]["base"]["ref"],
            "timestamp": datetime.utcnow()
        }
    else:
        print(f"Ignored event type: {event_type}")
        return jsonify({"message": "Event ignored"}), 200

    print("✅ Inserting into MongoDB:", entry)
    collection.insert_one(entry)
    return jsonify({"message": "Event saved"}), 200

# Serve frontend
@app.route("/")
def index():
    return render_template("index.html")

# Serve latest events for frontend
@app.route("/events", methods=["GET"])
def get_events():
    events = list(collection.find().sort("timestamp", -1).limit(10))
    for event in events:
        event["_id"] = str(event["_id"])
        event["timestamp"] = event["timestamp"].isoformat()
    return jsonify(events)

if __name__ == "__main__":
    app.run(debug=True)
