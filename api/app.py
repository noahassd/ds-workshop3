from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

model = joblib.load("iris_model.pkl")

@app.route("/")
def home():
    return "API de prédiction avec Flask est en ligne !"

@app.route("/predict", methods=["GET"])
def predict():
    try:
        f1 = float(request.args.get("f1"))
        f2 = float(request.args.get("f2"))
        f3 = float(request.args.get("f3"))
        f4 = float(request.args.get("f4"))

        prediction = model.predict(np.array([[f1, f2, f3, f4]]))[0]

        return jsonify({"prediction": int(prediction)})
    
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
