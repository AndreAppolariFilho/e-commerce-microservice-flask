import os
from functools import wraps

from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import requests
from decimal import Decimal

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("APPLICATION_SECRET_KEY", "SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URL", f'sqlite:///{os.path.join(os.getcwd(), "db", "shopping.db")}')
app.config["JWT_SECRET_KEY"] = os.environ.get("APPLICATION_JWT_SECRET_KEY", 'your_jwt_secret_key')
db = SQLAlchemy(app)
# JWT Initialization
jwt = JWTManager(app)
auth_service_base_url = os.environ.get("auth_service_base_url", "http://auth_service:5001")
products_service_base_url = os.environ.get("products_service_base_url", "http://products_service:5002")

"""
Models
"""


class ShoppingCart(db.Model):
    __tablename__ = "shoppingcarts"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    shopping_items = db.relationship("ShoppingCartItem", backref="shoppingcarts", lazy="select")

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "items": [item.serialize() for item in self.shopping_items]
        }


class ShoppingCartItem(db.Model):
    __tablename__ = "shoppingcartitems"
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.Text, nullable=False)
    product_category = db.Column(db.Text, nullable=False)
    shopping_cart_id = db.Column(db.Integer, db.ForeignKey(ShoppingCart.id, ondelete="CASCADE"), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "price": self.price,
            "quantity": self.quantity,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "product_category": self.product_category
        }



"""
Views
"""


def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Authorization token is missing!'}), 401
        response = requests.post(f"{auth_service_base_url}/validate", headers={'Authorization': token})
        if response.status_code != 200:
            return jsonify({'error': f'Invalid or expired token! Error: {response.content}'}), 401
        g.current_user = response.json()
        return f(*args, **kwargs)
    return wrapper


@app.route("/shopping_carts", methods=["POST", "GET"])
@token_required
def shopping_carts_list_api_view():
    user = g.current_user
    if request.method == "POST":
        shopping_cart = ShoppingCart.query.filter(ShoppingCart.username == user["username"]).one_or_none()
        if not shopping_cart:
            shopping_cart = ShoppingCart()
            shopping_cart.username = user["username"]
            db.session.add(shopping_cart)
            db.session.commit()
        token = request.headers.get('Authorization')
        data = request.get_json()
        product_id = data["product_id"]
        quantity = int(data["quantity"])
        response = requests.get(
            f"{products_service_base_url}/products/{product_id}/stocks",
            headers={'Authorization': token}
        )

        if response.status_code == 404:
            return jsonify({"error": "This product doesn't exist or there's no stock registered for it."}), 404

        if response.status_code > 299:
            return jsonify({"error": "Not possible to get the product value"}), 400

        product_data = response.json()
        shopping_cart_item = ShoppingCartItem()
        shopping_cart_item.price = Decimal(product_data["price"]) * quantity
        shopping_cart_item.quantity = quantity
        shopping_cart_item.product_id = product_id
        shopping_cart_item.product_category = product_data["category"]
        shopping_cart_item.product_name = product_data["name"]
        shopping_cart_item.shopping_cart_id = shopping_cart.id
        db.session.add(shopping_cart_item)
        db.session.commit()
        return jsonify(shopping_cart.serialize()), 200

    if request.method == "GET":
        shopping_cart = ShoppingCart.query.filter(ShoppingCart.username == user["username"]).one_or_none()
        if not shopping_cart:
            return jsonify({"error": "There's no shopping cart for your account."}), 404
        return jsonify(shopping_cart.serialize()), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=os.environ.get("port", "5003"))
