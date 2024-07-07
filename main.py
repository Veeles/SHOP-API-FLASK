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
from alembic import op
import uuid
new_api_key = os.environ['NEW_API_KEY'] = "xxx"
api_secret_key = os.environ['API_SECRET_KEY'] = 'xxx'
api_key = os.getenv('API_KEY')
stripe.api_key = api_secret_key

def format_price(price):
    return f'{price / 100:.2f} PLN'

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
app.secret_key = os.urandom(24) 
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
    for product in products1:
        product.formatted_price = format_price(product.price)
    for product in products:
        product.formatted_price = format_price(product.price)   

    for product in products2:
        product.formatted_price = format_price(product.price)

    for product in products3:
        product.formatted_price = format_price(product.price)

    if 'cartt' not in session:
        session['cartt'] = []
    if 'pieces' not in session:
        session['pieces'] = []



    return render_template('index.html', products1=products1, products2=products2, products3=products3, carousel_items=carousel_items, products4=products3 )

@app.route('/category/<category>')
def category(category):
    
    products = Product.query.all()

    category_products = Product.query.filter_by(category=str(category.lower()))
    for product in category_products:
        product.formatted_price = format_price(product.price)
    products1 = Product.query.filter_by(category='kids')[:10]
    return render_template('category.html', products=category_products)


@app.route("/product/<int:id>", methods=['GET'])
def product(id):
    product = Product.query.filter_by(id=id).first()
    
    product.formatted_price = format_price(product.price)
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
    product_id = request.args.get('product_number')
    pieces = request.args.get("piec")
    basket_products.append(product_id) 
    final_price=0
    if product_id is not None:
        product_id = str(product_id)
        pieces = str(pieces)
        cart = session['cartt']
        piece = session['pieces']
        cart.append(product_id)
        piece.append(pieces)
        session['cartt'] = cart
        session['pieces'] = piece
        cartt_len = len(session['cartt'])
        final_price = 0
        for one_cart in cart:
            one_product = Product.query.filter_by(id=one_cart).first()
            if one_product not in products:
                products.append(one_product)
                index = products.index(one_product)
              
                piece_int = list(map(int, piece))
                piece_int[index] += 1
               

            elif one_product in products:
                index = products.index(one_product)
            
                piece_int = list(map(int, piece))
                piece_int[index] += 1
          

    elif product_id is None:
        cart = session['cartt']
        final_price_formated = 0
        piece_int = 0

        for one_cart in cart:
            one_product = Product.query.filter_by(id=one_cart).first()
            if one_product not in products:
                products.append(one_product)
            elif one_product in products:
                index = products.index(one_product)
                piece_int = list(map(int, piece))
                piece_int[index] += 1
                piece[index] += 1
                
        
    for index,product in enumerate(products):
            pieces_mult = session['pieces'][index]
            pieces_mult = int(pieces_mult)
            price_mult = product.price * pieces_mult 

            product.formatted_price = format_price(price_mult)

            final_price = price_mult + final_price
            final_price_formated = format_price(final_price)
            session['final_price_end'] = final_price
            final_price_end = session.get('final_price_end')
    return render_template("basket.html", products_id=basket_products, products=products, cartt=session['cartt'], final_price=final_price_formated, piece=piece_int, final_price_noformated=final_price)

@app.route("/Buy-now")
@login_required
def buynow():
    return render_template('buy.html')

@app.route("/my-webbazaar")
def mywebbazaar():
    sign_up_form = SignUpForm()
    login_form = LoginForm()
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
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
         
            return render_template('test.html')
        elif not user:
            return 'bad email'
        elif user and not check_password_hash(user.password, password):
            return "bad password"
    
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



@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
  final_price_end = request.form.get('final_price_new')
 
  session = stripe.checkout.Session.create(
    line_items=[{
      'price_data': {
        'currency': 'usd',
        'product_data': {
          'name': 'WebBazaarHome',
        },
        'unit_amount': final_price_end,
      },
      'quantity': 1,
    }],
    mode='payment',
    success_url='http://127.0.0.1:4242/success',
    cancel_url='http://localhost:4242/cancel',
  )

  return redirect(session.url, code=303)
@app.route('/success')
def success():
    return render_template('success.html')
@app.route('/cancel')
def cancel():
    return render_template('cancel.html')

@app.route('/checkout/<final_price_new>', methods=['GET', 'POST'])
def checkout(final_price_new):

    return render_template('checkout.html', final_price_new=final_price_new)


if __name__ == "__main__":
    app.run(port=4242)

