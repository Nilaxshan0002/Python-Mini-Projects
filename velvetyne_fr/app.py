from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, Font, CartItem
from sqlalchemy.exc import OperationalError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///velvetyne.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'velvetyne-secret-key'
db.init_app(app)

# Context processor to make cart count available everywhere
@app.context_processor
def inject_cart_count():
    try:
        count = sum(item.quantity for item in CartItem.query.all())
    except Exception:
        count = 0
    return {'cart_count': count}

# ---------- Routes ----------
@app.route('/')
def index():
    category_filter = request.args.get('category', 'All')
    if category_filter and category_filter != 'All':
        fonts = Font.query.filter_by(category=category_filter).all()
    else:
        fonts = Font.query.all()
    categories = ['All', 'Serif', 'Sans', 'Display', 'Script']
    return render_template('index.html', fonts=fonts, categories=categories, active_filter=category_filter)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        fonts = Font.query.filter(Font.name.ilike(f'%{query}%')).all()
    else:
        fonts = Font.query.all()
    return render_template('search.html', fonts=fonts, query=query)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/journal')
def journal():
    return render_template('journal.html')

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/custom')
def custom():
    return render_template('custom.html')

# ---------- Cart Routes ----------
@app.route('/add_to_cart/<int:font_id>', methods=['POST'])
def add_to_cart(font_id):
    font = Font.query.get_or_404(font_id)
    existing_item = CartItem.query.filter_by(font_id=font_id).first()
    if existing_item:
        existing_item.quantity += 1
    else:
        db.session.add(CartItem(font_id=font_id, quantity=1))
    db.session.commit()
    flash(f'"{font.name}" added to cart!', 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/cart')
def cart():
    items = CartItem.query.all()
    total = sum(item.font.price * item.quantity for item in items)
    return render_template('cart.html', items=items, total=total)

@app.route('/remove_from_cart/<int:item_id>')
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Item removed from cart.', 'info')
    return redirect(url_for('cart'))

# ---------- Checkout & Contact Routes ----------
@app.route('/checkout', methods=['POST'])
def checkout():
    # Clear the cart upon successful checkout
    CartItem.query.delete()
    db.session.commit()
    return render_template('checkout_success.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        # In a real app, you would send an email or save to DB here
        flash(f'Thank you {name}! Your project inquiry has been sent.', 'success')
        return redirect(url_for('index'))
    return render_template('contact.html')

# ---------- Admin ----------
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        new_font = Font(
            name=request.form['name'],
            category=request.form['category'],
            description=request.form['description'],
            font_family_css=request.form['font_family_css'],
            price=float(request.form.get('price', 50.0))
        )
        db.session.add(new_font)
        db.session.commit()
        flash('Font added successfully!', 'success')
        return redirect(url_for('admin'))
    
    fonts = Font.query.all()
    return render_template('admin.html', fonts=fonts)

# ---------- Boot / Seed ----------
with app.app_context():
    # FIX: Automatically drop and recreate the database if the schema is outdated
    try:
        Font.query.count()
    except OperationalError as e:
        if "no such column" in str(e):
            db.drop_all()
            print("Outdated database schema detected. Rebuilding database...")
    
    db.create_all()
    
    # Seed initial data if the database is empty
    if Font.query.count() == 0:
        db.session.add_all([
            Font(name='Neue Machina', category='Sans', description='A technical grotesque with an engineered skeleton.', font_family_css='Arial, sans-serif', price=50),
            Font(name='Bodoni Blaze', category='Serif', description='Elegant Didone with a contemporary edge.', font_family_css='"Times New Roman", serif', price=60),
            Font(name='Calder', category='Display', description='Playful, chunky display for everyday use.', font_family_css='Impact, sans-serif', price=40),
            Font(name='Hans Kind', category='Serif', description='Expressive display font with a solid attitude.', font_family_css='Georgia, serif', price=55)
        ])
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)