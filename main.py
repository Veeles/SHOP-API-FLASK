from flask import Flask, render_template, request, session
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import os

basket_products = []
app = Flask(__name__)
Bootstrap(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db = SQLAlchemy(app)
app.secret_key = os.urandom(24)  # Sekretny klucz używany do szyfrowania sesji

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(150), unique=True, nullable=False)
    category = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(350), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    pieces = db.Column(db.Integer, nullable=False)
    photo_path = db.Column(db.String(100), nullable=False)



with app.app_context():
    db.create_all()
@app.route('/')
def index_page():
    products = Product.query.all()
    products1 = Product.query.filter_by(category='garden')[:10]
    products2 = Product.query.filter_by(category='kids')[:10]
    products3 = Product.query.order_by(Product.price.asc()).all()
    carousel_items = [products[i:i+3] for i in range(0, len(products), 3)]
    if 'cartt' not in session:
        session['cartt'] = []


    print(products1)

    return render_template('index.html', products1=products1, products2=products2, products3=products3, carousel_items=carousel_items, products4=products3 )

@app.route('/category/<category>')
def category(category):
    
    products = Product.query.all()
    #category_lower = str(category_path.lower())
    #print(category_lower)
    category_products = Product.query.filter_by(category=str(category.lower()))

    products1 = Product.query.filter_by(category='kids')[:10]
    return render_template('category.html', products=category_products)


@app.route("/product/<int:id>", methods=['GET'])
def product(id):
    print(id)
    product = Product.query.filter_by(id=id).first()
    print(product)
    if 'cartt' not in session:
        session['cartt'] = []
    return render_template("product.html", product=product)

@app.route("/basket", methods=['GET'])
def basket():
    if 'cartt' not in session:
        session['cartt'] = []
    global basket_products
    products = []
    print("hejop")
    product_id = request.args.get('product_number')
    basket_products.append(product_id) 
    if product_id is not None:
        product_id = str(product_id)
        cart = session['cartt']
        cart.append(product_id)
        session['cartt'] = cart
        for one_cart in cart:
            print(one_cart)
            one_product = Product.query.filter_by(id=one_cart).first()
            products.append(one_product)
            
        
    return render_template("basket.html", products_id=basket_products, cart=cart, products=products)
if __name__ == "__main__":
    app.run()

