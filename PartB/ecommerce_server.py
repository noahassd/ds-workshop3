from flask import Flask, request, jsonify

app = Flask(__name__)

# 📦 Base de données simple (JSON en mémoire)
products = []
carts = {}
orders = []

# 🔹 ROUTES PRODUITS
@app.route("/products", methods=["GET"])
def get_products():
    return jsonify(products)

@app.route("/products", methods=["POST"])
def add_product():
    data = request.get_json()
    product = {
        "id": len(products) + 1,
        "name": data["name"],
        "price": data["price"],
        "stock": data["stock"]
    }
    products.append(product)
    return jsonify(product), 201

# 🔹 ROUTES PANIER
@app.route("/cart/<user_id>", methods=["POST"])
def add_to_cart(user_id):
    data = request.get_json()
    if user_id not in carts:
        carts[user_id] = []
    carts[user_id].append({"product_id": data["product_id"], "quantity": data["quantity"]})
    return jsonify({"message": "Produit ajouté au panier", "cart": carts[user_id]})

@app.route("/cart/<user_id>", methods=["GET"])
def get_cart(user_id):
    return jsonify(carts.get(user_id, []))

# 🔹 ROUTES COMMANDES
@app.route("/orders", methods=["POST"])
def place_order():
    data = request.get_json()
    order = {
        "id": len(orders) + 1,
        "user_id": data["user_id"],
        "items": data["items"],
        "total_price": sum(p["price"] * p["quantity"] for p in products if p["id"] in [i["product_id"] for i in data["items"]])
    }
    orders.append(order)
    return jsonify(order), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)
