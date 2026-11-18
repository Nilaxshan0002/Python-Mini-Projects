from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, AppShot
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///appshot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'appshot-gallery-secret-key'
db.init_app(app)

# ---------- Helpers ----------
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access only.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return wrapper

# ---------- Public Routes ----------
@app.route('/')
def index():
    search = request.args.get('q', '')
    category = request.args.get('category', '')
    color = request.args.get('color', '')

    query = AppShot.query

    if search:
        query = query.filter(AppShot.app_name.ilike(f'%{search}%') | AppShot.title.ilike(f'%{search}%'))
    if category:
        query = query.filter_by(category=category)
    if color:
        query = query.filter_by(color=color)

    shots = query.order_by(AppShot.id.desc()).all()
    categories = [r[0] for r in db.session.query(AppShot.category).distinct().all() if r[0]]
    colors = [r[0] for r in db.session.query(AppShot.color).distinct().all() if r[0]]

    return render_template('index.html', shots=shots, categories=categories, colors=colors,
                           search=search, active_category=category, active_color=color)

# ---------- Auth ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already taken. Try another one.', 'danger')
            return redirect(url_for('register'))
        
        # Create new user (default role is 'user')
        new_user = User(
            username=username,
            password=generate_password_hash(password),
            role='user'
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('login.html', mode='register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username'].strip()).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html', mode='login')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('index'))

# ---------- Admin ----------
@app.route('/admin', methods=['GET', 'POST'])
@admin_required
def admin():
    if request.method == 'POST':
        shot = AppShot(
            title=request.form['title'],
            app_name=request.form['app_name'],
            category=request.form['category'],
            color=request.form['color'],
            image_url=request.form['image_url']
        )
        db.session.add(shot)
        db.session.commit()
        flash('AppShot added successfully!', 'success')
        return redirect(url_for('admin'))
    
    shots = AppShot.query.order_by(AppShot.id.desc()).all()
    return render_template('admin.html', shots=shots)

@app.route('/admin/delete/<int:id>')
@admin_required
def delete_shot(id):
    shot = AppShot.query.get_or_404(id)
    db.session.delete(shot)
    db.session.commit()
    flash('AppShot deleted.', 'info')
    return redirect(url_for('admin'))

# ---------- Boot / Seed ----------
with app.app_context():
    db.create_all()
    
    # Seed Admin account
    if not User.query.filter_by(username='admin').first():
        db.session.add(User(username='admin', password=generate_password_hash('admin123'), role='admin'))
        db.session.commit()
    
    # Seed dummy data
    if AppShot.query.count() == 0:
        db.session.add_all([
            AppShot(title='Money Tracker App', app_name='Wallet', category='Finance', color='Dark', image_url='https://images.unsplash.com/photo-1616077167803-e0ceb2b7c56a?w=500&q=80'),
            AppShot(title='Meditation & Sleep', app_name='Calm', category='Health', color='Blue', image_url='https://images.unsplash.com/photo-1512438248247-f0f2a5a8b7f0?w=500&q=80'),
            AppShot(title='Task Management', app_name='TaskFlow', category='Productivity', color='Light', image_url='https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?w=500&q=80'),
        ])
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)