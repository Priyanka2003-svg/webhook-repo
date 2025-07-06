from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
client = MongoClient("mongodb+srv://priyankadoijode:priyankadoijode@priyanka.gsqag2g.mongodb.net/?retryWrites=true&w=majority&appName=priyanka")
db = client["webhook_db"]
collection = db["events"]

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')

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
        return jsonify({"message": "Event ignored"}), 200

    collection.insert_one(entry)
    return jsonify({"message": "Event saved"}), 200

@app.route('/events')
def get_events():
    events = list(collection.find().sort("timestamp", -1).limit(10))
    for e in events:
        e["_id"] = str(e["_id"])
    return jsonify(events)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
