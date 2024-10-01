import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("APPLICATION_SECRET_KEY", "SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URL", 'sqlite:///db/prodcuts.db')
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

    def serialize(self):
        return {
            "id": self.id,
            "price": self.price,
            "quantity": self.quantity,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "product_id": self.product_id
        }


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=os.environ.get("port", "5002"))
