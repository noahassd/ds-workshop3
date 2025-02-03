from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

# 📌 Charger les modèles AVANT l'utilisation dans l'API
models = {
    "random_forest": joblib.load("models/iris_model.pkl"),
    "NB": joblib.load("models/iris_modelNB.pkl")
}

@app.route("/")
def home():
    return "API de prédiction avec plusieurs modèles est en ligne !"

@app.route("/predict", methods=["GET"])
def predict():
    try:
        f1 = float(request.args.get("f1"))
        f2 = float(request.args.get("f2"))
        f3 = float(request.args.get("f3"))
        f4 = float(request.args.get("f4"))
        model_type = request.args.get("model", "random_forest")  # Par défaut : Random Forest

        if model_type not in models:
            return jsonify({"error": "Modèle non disponible"}), 400

        model = models[model_type]
        
        # Vérifier si predict_proba est disponible
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(np.array([[f1, f2, f3, f4]]))[0]
            prediction = int(np.argmax(proba))
            confidence = float(np.max(proba))
        else:
            prediction = model.predict(np.array([[f1, f2, f3, f4]]))[0]
            confidence = None  # Pas de score de confiance disponible

        return jsonify({"model": model_type, "prediction": prediction, "confidence": confidence})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
