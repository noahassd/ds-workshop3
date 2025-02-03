from flask import Flask, jsonify

app = Flask(__name__)

ACTIVE_SERVER = "localhost:3001"

@app.route("/getServer", methods=["GET"])
def get_server():
    return jsonify({"code": 200, "server": ACTIVE_SERVER})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
