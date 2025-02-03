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

# 🔹 Initialisation des données (6 products, 2 carts, 3 orders)
def init_data():
    products.extend([
        {"id": 1, "name": "Produit 1", "price": 100, "stock": 50},
        {"id": 2, "name": "Produit 2", "price": 150, "stock": 30},
        {"id": 3, "name": "Produit 3", "price": 200, "stock": 20},
        {"id": 4, "name": "Produit 4", "price": 250, "stock": 10},
        {"id": 5, "name": "Produit 5", "price": 300, "stock": 5},
        {"id": 6, "name": "Produit 6", "price": 50, "stock": 100}
    ])
    
    carts["user_1"] = [
        {"product_id": 1, "quantity": 2},
        {"product_id": 3, "quantity": 1}
    ]
    carts["user_2"] = [
        {"product_id": 2, "quantity": 3},
        {"product_id": 5, "quantity": 1}
    ]
    
    orders.extend([
        {"id": 1, "user_id": "user_1", "items": [{"product_id": 1, "quantity": 2}, {"product_id": 3, "quantity": 1}], "total_price": 350},
        {"id": 2, "user_id": "user_2", "items": [{"product_id": 2, "quantity": 3}, {"product_id": 5, "quantity": 1}], "total_price": 850},
        {"id": 3, "user_id": "user_1", "items": [{"product_id": 4, "quantity": 1}], "total_price": 250}
    ])

init_data()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)
