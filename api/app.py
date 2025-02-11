import json
from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# 📌 Charger les modèles
models = {
    "random_forest": joblib.load("models/iris_model.pkl"),
    "NB": joblib.load("models/iris_modelNB.pkl"),
    "DT": joblib.load("models/iris_modelDT.pkl"),
    "SVM": joblib.load("models/iris_modelSVM.pkl")
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

        # 🔥 Vérifier que des modèles sont inscrits (staked=True)
        active_models = [m for m in db if db[m]["staked"]]
        if not active_models:
            return jsonify({"error": "Aucun modèle actif, tous ont été exclus."}), 400

        total_weight = sum(db[model]["weight"] for model in active_models)

        for model_name in active_models:
            model = models[model_name]

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
            "weights": {model: db[model]["weight"] for model in active_models}
        })

    except Exception as e:
        return jsonify({"error": str(e)})
@app.route("/stake", methods=["POST"])
def stake():
    try:
        data = request.get_json()
        model_name = data["model"]

        db = load_db()

        if model_name not in models:
            return jsonify({"error": "Modèle inconnu"}), 400

        # 📌 Vérifier si le modèle est déjà inscrit
        if db.get(model_name, {}).get("staked", False):
            return jsonify({"message": f"{model_name} est déjà inscrit."})

        # 🚀 Ajouter le modèle avec un dépôt initial
        db[model_name] = {
            "weight": 1.0,
            "balance": 1000,
            "staked": True
        }

        save_db(db)
        return jsonify({"message": f"{model_name} a rejoint le système avec 1000€ de dépôt.", "database": db})

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/update_scores", methods=["POST"])
def update_scores():
    try:
        data = request.get_json()
        correct_prediction = int(data["correct_prediction"])  # La vraie valeur à prédire
        db = load_db()

        for model_name, prediction in data["predictions"].items():
            if model_name not in db:
                continue  # Si un modèle a déjà été supprimé, on l'ignore

            if prediction == correct_prediction:
                # ✅ Récompense : Augmente la balance et le poids du modèle
                db[model_name]["balance"] += 10
                db[model_name]["weight"] = min(db[model_name]["weight"] + 0.1, 2.0)
            else:
                # ❌ Pénalité (Slashing) : Diminue la balance et le poids du modèle
                db[model_name]["balance"] -= 50
                db[model_name]["weight"] = max(db[model_name]["weight"] - 0.2, 0.1)

            # 🚨 Suppression d'un modèle si son balance atteint 0
            if db[model_name]["balance"] <= 0:
                del db[model_name]

        save_db(db)

        return jsonify({"message": "Scores mis à jour", "database": db})

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
