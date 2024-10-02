import os
from functools import wraps

from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from datetime import datetime
from decimal import Decimal


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("APPLICATION_SECRET_KEY", "SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URL", f'sqlite:///{os.path.join(os.getcwd(), "db", "products.db")}')
app.config["JWT_SECRET_KEY"] = os.environ.get("APPLICATION_JWT_SECRET_KEY", 'your_jwt_secret_key')
db = SQLAlchemy(app)
# JWT Initialization
jwt = JWTManager(app)
auth_service_base_url = os.environ.get("auth_service_base_url", "http://auth_service:5001")

"""
Models
"""


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    category = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    stock = db.relationship("Stock", backref="products", lazy="select", uselist=False)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class Stock(db.Model):
    __tablename__ = "stocks"
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    product_id = db.Column(db.Integer, db.ForeignKey(Product.id, ondelete="CASCADE"), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)

    def serialize(self):
        return {
            "id": self.id,
            "price": self.price,
            "quantity": self.quantity,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "product_id": self.product_id
        }


with app.app_context():
    db.create_all()

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


@app.route("/products", methods=["POST", "GET"])
@token_required
def products_api_view():
    user = g.current_user
    if request.method == "POST":
        if not user["is_admin"]:
            return jsonify({"error": "You are not allowed to do this"}), 401
        data = request.get_json()
        product = Product()
        product.name = data["name"]
        product.category = data["category"]
        db.session.add(product)
        db.session.commit()
        stock = Stock()
        stock.price = 0
        stock.quantity = 0
        stock.product_id = product.id
        db.session.add(stock)
        db.session.commit()
        return jsonify(product.serialize()), 200
    if request.method == "GET":
        products_query = Product.query
        page = request.args.get('page', 1, type=int)
        products = products_query.order_by(Product.name.desc()).paginate(page=page, per_page=100)
        return jsonify([product.serialize() for product in products]), 200


@app.route("/products/<product_id>/stocks", methods=["POST", "GET"])
@token_required
def single_stock_api_view(product_id):
    user = g.current_user
    if request.method == "POST":
        if not user["is_admin"]:
            return jsonify({"error": "You are not allowed to do this"}), 401
        data = request.get_json()
        Stock.query.filter(Stock.product_id == product_id).update(
            {
                "price": Decimal(data["price"]),
                "quantity": int(data["quantity"]),
                "is_completed": True
            }
        )
        db.session.commit()
        return jsonify(
            Stock.query.filter(Stock.product_id == product_id).one_or_none().serialize()
        ), 200
    if request.method == "GET":
        return jsonify(
            Stock.query.filter(Stock.product_id == product_id and Stock.is_completed).one_or_none().serialize()
        ), 200


if __name__ == "__main__":

    app.run(debug=True, host="0.0.0.0", port=os.environ.get("port", "5002"))
