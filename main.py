from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
Bootstrap(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db = SQLAlchemy(app)


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
    return render_template("product.html", product=product)
if __name__ == "__main__":
    app.run()

