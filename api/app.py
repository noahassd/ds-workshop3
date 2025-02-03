import json
from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# 📌 Charger les modèles
models = {
    "random_forest": joblib.load("models/iris_model.pkl"),
    "NB": joblib.load("models/iris_modelNB.pkl")
}

# 📌 Charger la base de données JSON pour stocker les poids et balances
DB_FILE = "api/models_db.json"

def load_db():
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

@app.route("/")
def home():
    return "API avec pondération des modèles est en ligne !"

@app.route("/predict_all", methods=["GET"])
def predict_all():
    try:
        f1 = float(request.args.get("f1"))
        f2 = float(request.args.get("f2"))
        f3 = float(request.args.get("f3"))
        f4 = float(request.args.get("f4"))

        db = load_db()
        predictions = {}
        weighted_predictions = []

        total_weight = sum(db[model]["weight"] for model in models)

        for model_name, model in models.items():
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(np.array([[f1, f2, f3, f4]]))[0]
                prediction = int(np.argmax(proba))
            else:
                prediction = model.predict(np.array([[f1, f2, f3, f4]]))[0]

            predictions[model_name] = prediction
            weighted_predictions.append(db[model_name]["weight"] * prediction)

        # Calcul du consensus pondéré
        consensus_prediction = round(sum(weighted_predictions) / total_weight)

        return jsonify({
            "predictions": predictions,
            "consensus_prediction": int(consensus_prediction),
            "weights": {model: db[model]["weight"] for model in models}
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
