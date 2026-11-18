from flask import Flask, render_template, request, redirect, url_for, flash
from markupsafe import Markup
from models import db, Component
from sqlalchemy.exc import OperationalError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gallery.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'gallery-secret-key'
db.init_app(app)

# Custom filter to render raw HTML in Jinja templates safely
@app.template_filter('safe_html')
def safe_html(text):
    return Markup(text)

# ---------- Routes ----------
@app.route('/')
def index():
    category_filter = request.args.get('category', 'All')
    search_query = request.args.get('q', '')

    query = Component.query

    # Filter by category
    if category_filter and category_filter != 'All':
        query = query.filter_by(category=category_filter)
    
    # Search by title
    if search_query:
        query = query.filter(Component.title.ilike(f'%{search_query}%'))

    # Get components, newest first
    components = query.order_by(Component.id.desc()).all()
    
    # Get unique categories for the sidebar
    all_categories = [r[0] for r in db.session.query(Component.category).distinct().all() if r[0]]
    categories = ['All'] + all_categories

    return render_template('index.html', components=components, categories=categories, 
                           active_category=category_filter, search=search_query)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        new_comp = Component(
            title=request.form['title'],
            category=request.form['category'],
            description=request.form['description'],
            code_snippet=request.form['code_snippet']
        )
        db.session.add(new_comp)
        db.session.commit()
        flash('Component added successfully!', 'success')
        return redirect(url_for('admin'))
    
    # Get all components for the admin list
    comps = Component.query.order_by(Component.id.desc()).all()
    return render_template('admin.html', components=comps)

@app.route('/delete/<int:id>')
def delete(id):
    comp = Component.query.get_or_404(id)
    db.session.delete(comp)
    db.session.commit()
    flash('Component deleted.', 'info')
    return redirect(url_for('admin'))

# ---------- Boot / Seed ----------
with app.app_context():
    try:
        Component.query.count()
    except OperationalError:
        db.drop_all()
    
    db.create_all()
    
    # Seed initial components if the database is empty
    if Component.query.count() == 0:
        db.session.add_all([
            Component(
                title="Primary Button",
                category="Buttons",
                description="A clean, modern button with a subtle hover effect.",
                code_snippet="<button style='background: #111; color: white; padding: 12px 24px; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; font-family: sans-serif; transition: 0.2s;' onmouseover=\"this.style.background='#333'\" onmouseout=\"this.style.background='#111'\">Click Me</button>"
            ),
            Component(
                title="Gradient Card",
                category="Cards",
                description="A beautiful card with a subtle gradient background.",
                code_snippet="<div style='background: linear-gradient(135deg, #f6d365 0%, #fda085 100%); padding: 24px; border-radius: 12px; width: 250px; color: #111; font-family: sans-serif;'><h3 style='margin:0 0 8px 0;'>Pro Plan</h3><p style='margin:0; font-size: 0.9rem; opacity: 0.8;'>Everything you need to scale.</p></div>"
            ),
            Component(
                title="Neon Input",
                category="Inputs",
                description="An input field with a glowing focus state.",
                code_snippet="<input type='text' placeholder='Enter email...' style='padding: 12px 16px; border-radius: 8px; border: 2px solid #eee; outline: none; font-family: sans-serif; transition: 0.3s;' onfocus=\"this.style.borderColor='#3b82f6'; this.style.boxShadow='0 0 0 4px rgba(59, 130, 246, 0.2)'\" onblur=\"this.style.borderColor='#eee'; this.style.boxShadow='none'\">"
            ),
            Component(
                title="Glassmorphism Nav",
                category="Navigation",
                description="A frosted glass navigation bar effect.",
                code_snippet="<div style='background: rgba(255,255,255,0.7); backdrop-filter: blur(10px); border-bottom: 1px solid rgba(0,0,0,0.05); padding: 16px 24px; border-radius: 12px; display: flex; gap: 20px; font-family: sans-serif; font-weight: 500;'><span>Home</span><span>About</span><span>Contact</span></div>"
            )
        ])
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)