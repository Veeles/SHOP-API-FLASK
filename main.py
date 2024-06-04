from flask import Flask, render_template, request, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import EmailType, PasswordType
from datetime import timedelta
import os
from forms import SignUpForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from passlib.hash import sha256_crypt
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import stripe




login_manager = LoginManager()


crypt_context = CryptContext(
    schemes=["bcrypt", "sha256_crypt"],
    deprecated=["auto"],
)
basket_products = []
app = Flask(__name__)
Bootstrap(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db = SQLAlchemy(app)
app.secret_key = os.urandom(24)  # Sekretny klucz używany do szyfrowania sesji
login_manager.init_app(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(150), unique=True, nullable=False)
    category = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(350), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    pieces = db.Column(db.Integer, nullable=False)
    photo_path = db.Column(db.String(100), nullable=False)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(450), nullable=False)
    email = db.Column(EmailType, unique=True)

    

with app.app_context():
    db.create_all()

YOUR_DOMAIN = 'http://127.0.0.1:5000'
@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price':'{{PRICE_ID}}',
                    'quantity':'{{HOW_MUCH}}',
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/success.html',
            cencel_url=YOUR_DOMAIN + '/cancel.html',
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index_page'))
@app.route('/')
def index_page():
    products = Product.query.all()
    products1 = Product.query.filter_by(category='garden')[:10]
    products2 = Product.query.filter_by(category='kids')[:10]
    products3 = Product.query.order_by(Product.price.asc()).all()
    carousel_items = [products[i:i+3] for i in range(0, len(products), 3)]
    if 'cartt' not in session:
        session['cartt'] = []
    if 'pieces' not in session:
        session['pieces'] = []


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
    if 'pieces' not in session:
        session['pieces'] = []    
    return render_template("product.html", product=product)

@app.route("/basket", methods=['GET', 'POST'])
def basket():
    if 'cartt' not in session:
        session['cartt'] = []
    if 'pieces' not in session:
        session['pieces'] = []
    global basket_products
    products = []
    print("hejop")
    product_id = request.args.get('product_number')
    pieces = request.args.get("piec")
    print(pieces)
    basket_products.append(product_id) 
    if product_id is not None:
        product_id = str(product_id)
        pieces = str(pieces)
        cart = session['cartt']
        piece = session['pieces']
        cart.append(product_id)
        piece.append(pieces)
        session['cartt'] = cart
        session['pieces'] = piece
        print(pieces)
        cartt_len = len(session['cartt'])
        for one_cart in cart:
            print(one_cart)
            one_product = Product.query.filter_by(id=one_cart).first()
            if one_product not in products:
                products.append(one_product)
    elif product_id is None:
        cart = session['cartt']

        for one_cart in cart:
            print(one_cart)
            one_product = Product.query.filter_by(id=one_cart).first()
            if one_product not in products:
                products.append(one_product)
    # full_price = 0
    # for product in products:
    #     full_price =+ product.price
    #     return full_price

    # print(full_price)        
            
        
    return render_template("basket.html", products_id=basket_products, products=products, cartt=session['cartt'])

@app.route("/Buy-now")
@login_required
def buynow():
    return render_template('buy.html')

@app.route("/my-webbazaar")
def mywebbazaar():
    sign_up_form = SignUpForm()
    login_form = LoginForm()
    print("dupa")
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template("my_shop.html", form=sign_up_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit(): 
        password = login_form.password.data 
        email = login_form.email.data 
        hashed_password = generate_password_hash(password)
        print("muu")
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            print('hiiiiiii')
            print(current_user.name)
            return render_template('test.html')
        elif not user:
            return 'bad email'
        elif user and not check_password_hash(user.password, password):
            return "bad password"
    print("sram")
    
    return render_template('login.html', form=login_form)

@app.route('/signin',  methods=['GET', 'POST'])
def signin():
    sign_form = SignUpForm()
    if sign_form.validate_on_submit(): 
        name = sign_form.name.data 
        password = sign_form.password.data 
        email = sign_form.email.data 
        hashed_password = generate_password_hash(password)
        try:
            new = User(name=name, password=hashed_password, email=email)
            db.session.add(new)
            db.session.commit()
            login_user(new)
        except IntegrityError:
            db.session.rollback()  # Przywróć sesję do stanu przed operacją dodawania użytkownika
            return "Ten adres e-mail już istnieje, proszę wybrać inny."
       



        return f'Name: {name} < br > Password: {hashed_password} <br > Remember me: {email}'
    return render_template('signin.html', form=sign_form)
if __name__ == "__main__":
    app.run()

