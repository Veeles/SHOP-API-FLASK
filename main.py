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
    products = Product.query.filter_by(category='garden')[:10]
    print(products)

    return render_template('index.html', products=products )


if __name__ == "__main__":
    app.run()