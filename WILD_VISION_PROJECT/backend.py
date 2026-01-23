from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/api/poaching", methods=["POST"])
def poaching():
    data = request.json
    print("🚨 POACHING ALERT RECEIVED:", data)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=5000)
