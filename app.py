from flask import Flask, render_template, request, jsonify
from main import TourismAgent

app = Flask(__name__)
tourism_agent = TourismAgent()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/plan", methods=["POST"])
def plan():
    data = request.json or {}
    place = data.get("place", "")
    mode = data.get("mode", "both")  # "weather", "places", or "both"

    want_weather = mode in ("weather", "both")
    want_places = mode in ("places", "both")

    reply = tourism_agent.plan_trip(place, want_weather, want_places)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
