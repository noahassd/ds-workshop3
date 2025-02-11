import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Active CORS pour toutes les routes

# 📦 Base de données en mémoire
products = []
carts = {}
orders = []

# 🔥 Liste des serveurs de backup
BACKUP_SERVERS = ["http://localhost:3002"]


# Fonction pour synchroniser les données avec les autres serveurs
def replicate_data(route, data):
    for server in BACKUP_SERVERS:
        try:
            requests.post(f"{server}{route}", json=data)
        except requests.exceptions.RequestException:
            print(f"⚠️ Erreur de synchronisation avec {server}")

# 🔹 ROUTES PRODUITS
@app.route("/products", methods=["GET"])
def get_products():
    return jsonify(products)

@app.route("/products/<int:id>", methods=["GET"])
def get_product(id):
    # Recherche du produit par ID
    product = next((prod for prod in products if prod["id"] == id), None)
    
    # Si le produit est trouvé, on le retourne en JSON
    if product:
        return jsonify(product)
    
    # Si le produit n'est pas trouvé, on retourne une erreur 404
    return jsonify({"error": "Product not found"}), 404

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

    # 🔄 Réplication vers le serveur secondaire
    replicate_data("/products", product)

    return jsonify(product), 201

@app.route("/products/<int:id>", methods=["PUT"])
def update_product(id):
    product = next((prod for prod in products if prod["id"] == id), None)
    
    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json()

    product["name"] = data.get("name", product["name"])
    product["description"] = data.get("description", product["description"])
    product["price"] = data.get("price", product["price"])
    product["category"] = data.get("category", product["category"])
    product["stock"] = data.get("stock", product["stock"])

    return jsonify(product)

@app.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    product = next((prod for prod in products if prod["id"] == id), None)

    if not product:
        return jsonify({"error": "Product not found"}), 404

    products.remove(product)

    return jsonify({"message": f"Product with ID {id} has been deleted successfully."}), 200


# 🔹 ROUTES PANIER
@app.route("/cart/<user_id>", methods=["POST"])
def add_to_cart(user_id):
    data = request.get_json()
    if user_id not in carts:
        carts[user_id] = []
    carts[user_id].append({"product_id": data["product_id"], "quantity": data["quantity"]})

    # 🔄 Réplication du panier
    replicate_data(f"/cart/{user_id}", carts[user_id])

    return jsonify({"message": "Produit ajouté au panier", "cart": carts[user_id]})

# 🔹 ROUTES COMMANDES
@app.route("/orders", methods=["POST"])
def place_order():
    data = request.get_json()
    order = {
        "id": len(orders) + 1,
        "user_id": data["user_id"],
        "items": data["items"],
        "total_price": sum(i["quantity"] * next(p["price"] for p in products if p["id"] == i["product_id"]) for i in data["items"])
    }
    orders.append(order)

    # 🔄 Réplication des commandes
    replicate_data("/orders", order)

    return jsonify(order), 201

@app.route("/cart/<user_id>", methods=["GET"])
def get_cart(user_id):
    cart = carts.get(user_id, [])
    
    cart_details = []
    total_price = 0

    for item in cart:
        product = next((prod for prod in products if prod["id"] == item["product_id"]), None)
        if product:
            total_price += product["price"] * item["quantity"]
            cart_details.append({
                "product_name": product["name"],
                "quantity": item["quantity"],
                "price_per_item": product["price"],
                "total_price": product["price"] * item["quantity"]
            })

    return jsonify({"user_id": user_id, "cart": cart_details, "total_price": total_price})



@app.route("/cart/<user_id>/item/<int:product_id>", methods=["DELETE"])
def delete_item_from_cart(user_id, product_id):
    cart = carts.get(user_id, [])
    
    cart_item = next((item for item in cart if item["product_id"] == product_id), None)

    if cart_item:
        cart.remove(cart_item)
        return jsonify({"message": f"Product {product_id} removed from cart.", "cart": cart})

    return jsonify({"error": "Product not found in cart"}), 404

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
