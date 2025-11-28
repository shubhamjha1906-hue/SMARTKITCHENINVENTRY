"""
Smart Kitchen Inventory System
A beginner-friendly Flask application for tracking kitchen items
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from functools import wraps
import os
import csv
from io import StringIO, BytesIO
import sys

# Initialize Flask
app = Flask(__name__)

# Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "db", "smart_kitchen.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-this')

# Initialize Database
db = SQLAlchemy(app)

# ==================== DATABASE MODELS ====================

class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    items = db.relationship('Item', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and store password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'


class Item(db.Model):
    """Item model for inventory"""
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), default='Other')
    barcode = db.Column(db.String(100), nullable=True)
    quantity = db.Column(db.Float, default=1)
    unit = db.Column(db.String(20), default='pcs')  # pcs, kg, L, ml, etc
    expiry_date = db.Column(db.Date, nullable=True)
    location = db.Column(db.String(100), default='Pantry')
    low_stock_threshold = db.Column(db.Float, default=5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def is_expired(self):
        """Check if item is expired"""
        if self.expiry_date:
            return self.expiry_date < datetime.now().date()
        return False
    
    def is_expiring_soon(self, days=7):
        """Check if item is expiring within X days"""
        if self.expiry_date:
            days_left = (self.expiry_date - datetime.now().date()).days
            return 0 <= days_left <= days
        return False
    
    def is_low_stock(self):
        """Check if item is below threshold"""
        return self.quantity < self.low_stock_threshold
    
    def to_dict(self):
        """Convert to dictionary for CSV/JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'barcode': self.barcode or '',
            'quantity': self.quantity,
            'unit': self.unit,
            'expiry_date': self.expiry_date.strftime('%Y-%m-%d') if self.expiry_date else '',
            'location': self.location,
            'low_stock_threshold': self.low_stock_threshold
        }
    
    def __repr__(self):
        return f'<Item {self.name}>'


# Ensure DB directory exists so sqlite can create the file
db_dir = os.path.join(basedir, "db")
os.makedirs(db_dir, exist_ok=True)

# ==================== HELPER FUNCTIONS ====================

def get_current_user():
    """Get current logged-in user from session"""
    from flask import session
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not get_current_user():
            flash('Please log in first', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROUTES ====================

# ===== PUBLIC ROUTES =====

@app.route('/')
def home():
    """Home page"""
    if get_current_user():
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup route"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not name or not email or not password:
            flash('All fields are required', 'danger')
            return render_template('signup.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return render_template('signup.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('signup.html')
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please login.', 'info')
            return redirect(url_for('login'))
        
        # Create new user
        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Account created! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login route"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            from flask import session
            session['user_id'] = user.id
            flash(f'Welcome {user.name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout route"""
    from flask import session
    session.pop('user_id', None)
    flash('Logged out successfully', 'info')
    return redirect(url_for('home'))

# ===== AUTHENTICATED ROUTES =====

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard with statistics"""
    user = get_current_user()
    items = Item.query.filter_by(user_id=user.id).all()
    
    today = datetime.now().date()
    
    # Calculate stats
    total_items = len(items)
    low_stock_items = [item for item in items if item.is_low_stock()]
    expiring_soon = [item for item in items if item.is_expiring_soon()]
    expired_items = [item for item in items if item.is_expired()]
    
    stats = {
        'total_items': total_items,
        'low_stock_count': len(low_stock_items),
        'expiring_soon_count': len(expiring_soon),
        'expired_count': len(expired_items)
    }
    
    return render_template('dashboard.html', stats=stats, user=user)

@app.route('/items')
@login_required
def items_list():
    """List all items"""
    user = get_current_user()
    search = request.args.get('search', '').strip().lower()
    category_filter = request.args.get('category', '').strip()
    
    query = Item.query.filter_by(user_id=user.id)
    
    # Apply filters
    if search:
        query = query.filter(Item.name.ilike(f'%{search}%'))
    
    if category_filter:
        query = query.filter_by(category=category_filter)
    
    items = query.order_by(Item.created_at.desc()).all()
    
    # Get unique categories
    all_categories = list(set([item.category for item in Item.query.filter_by(user_id=user.id).all()]))
    
    return render_template(
        'items_list.html',
        items=items,
        search=search,
        category_filter=category_filter,
        categories=all_categories,
        user=user
    )

@app.route('/item/add', methods=['GET', 'POST'])
@login_required
def add_item():
    """Add new item"""
    user = get_current_user()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category = request.form.get('category', 'Other').strip()
        barcode = request.form.get('barcode', '').strip()
        quantity = request.form.get('quantity', '0')
        unit = request.form.get('unit', 'pcs').strip()
        expiry_date_str = request.form.get('expiry_date', '')
        location = request.form.get('location', 'Pantry').strip()
        low_stock_threshold = request.form.get('low_stock_threshold', '5')
        
        # Validation
        if not name:
            flash('Item name is required', 'danger')
            return render_template('item_form.html', mode='add', user=user)
        
        try:
            quantity = float(quantity) if quantity else 0
            low_stock_threshold = float(low_stock_threshold) if low_stock_threshold else 5
        except ValueError:
            flash('Quantity must be a number', 'danger')
            return render_template('item_form.html', mode='add', user=user)
        
        expiry_date = None
        if expiry_date_str:
            try:
                expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format', 'danger')
                return render_template('item_form.html', mode='add', user=user)
        
        # Create item
        item = Item(
            user_id=user.id,
            name=name,
            category=category,
            barcode=barcode,
            quantity=quantity,
            unit=unit,
            expiry_date=expiry_date,
            location=location,
            low_stock_threshold=low_stock_threshold
        )
        
        db.session.add(item)
        db.session.commit()
        
        flash(f'Item "{name}" added successfully!', 'success')
        return redirect(url_for('items_list'))
    
    return render_template('item_form.html', mode='add', user=user)

@app.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    """Edit item"""
    user = get_current_user()
    item = Item.query.get_or_404(item_id)
    
    # Check ownership
    if item.user_id != user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('items_list'))
    
    if request.method == 'POST':
        item.name = request.form.get('name', item.name).strip()
        item.category = request.form.get('category', item.category).strip()
        item.barcode = request.form.get('barcode', item.barcode).strip()
        item.location = request.form.get('location', item.location).strip()
        item.unit = request.form.get('unit', item.unit).strip()
        
        try:
            item.quantity = float(request.form.get('quantity', item.quantity))
            item.low_stock_threshold = float(request.form.get('low_stock_threshold', item.low_stock_threshold))
        except ValueError:
            flash('Quantity must be a number', 'danger')
            return render_template('item_form.html', mode='edit', item=item, user=user)
        
        expiry_date_str = request.form.get('expiry_date', '')
        if expiry_date_str:
            try:
                item.expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format', 'danger')
                return render_template('item_form.html', mode='edit', item=item, user=user)
        else:
            item.expiry_date = None
        
        db.session.commit()
        flash(f'Item "{item.name}" updated successfully!', 'success')
        return redirect(url_for('items_list'))
    
    return render_template('item_form.html', mode='edit', item=item, user=user)

@app.route('/item/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(item_id):
    """Delete item"""
    user = get_current_user()
    item = Item.query.get_or_404(item_id)
    
    if item.user_id != user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('items_list'))
    
    item_name = item.name
    db.session.delete(item)
    db.session.commit()
    
    flash(f'Item "{item_name}" deleted successfully!', 'success')
    return redirect(url_for('items_list'))

@app.route('/scan')
@login_required
def scan():
    """Barcode scanner page"""
    user = get_current_user()
    return render_template('scan.html', user=user)

@app.route('/export-csv')
@login_required
def export_csv():
    """Export items as CSV"""
    user = get_current_user()
    items = Item.query.filter_by(user_id=user.id).all()
    
    # Create CSV
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        'name', 'category', 'barcode', 'quantity', 'unit', 
        'expiry_date', 'location', 'low_stock_threshold'
    ])
    
    writer.writeheader()
    for item in items:
        writer.writerow(item.to_dict())
    
    output.seek(0)
    
    # Convert to BytesIO for download
    mem = BytesIO()
    mem.write(output.getvalue().encode('utf-8'))
    mem.seek(0)
    
    return send_file(
        mem,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'inventory_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/import-csv', methods=['POST'])
@login_required
def import_csv():
    """Import items from CSV"""
    user = get_current_user()
    
    if 'file' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('items_list'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('items_list'))
    
    if not file.filename.endswith('.csv'):
        flash('Only CSV files are allowed', 'danger')
        return redirect(url_for('items_list'))
    
    try:
        stream = file.stream.read().decode('UTF-8')
        csv_reader = csv.DictReader(StringIO(stream))
        
        imported_count = 0
        
        for row in csv_reader:
            try:
                # Parse data
                expiry_date = None
                if row.get('expiry_date', '').strip():
                    expiry_date = datetime.strptime(row['expiry_date'], '%Y-%m-%d').date()
                
                quantity = float(row.get('quantity', 1))
                threshold = float(row.get('low_stock_threshold', 5))
                
                # Create item
                item = Item(
                    user_id=user.id,
                    name=row.get('name', 'Unknown').strip(),
                    category=row.get('category', 'Other').strip(),
                    barcode=row.get('barcode', '').strip(),
                    quantity=quantity,
                    unit=row.get('unit', 'pcs').strip(),
                    expiry_date=expiry_date,
                    location=row.get('location', 'Pantry').strip(),
                    low_stock_threshold=threshold
                )
                
                db.session.add(item)
                imported_count += 1
            
            except Exception as e:
                print(f"Error importing row: {e}", file=sys.stderr)
                continue
        
        db.session.commit()
        flash(f'Successfully imported {imported_count} items!', 'success')
    
    except Exception as e:
        flash(f'Error importing CSV: {str(e)}', 'danger')
    
    return redirect(url_for('items_list'))

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return render_template('error.html', error='Server error'), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    # Print DB URI and create tables at startup (avoid running at import time)
    with app.app_context():
        print("Using DB:", app.config.get('SQLALCHEMY_DATABASE_URI'))
        db.create_all()

    print("=" * 60)
    print("🍳 Smart Kitchen Inventory System")
    print("=" * 60)
    print("Server running at: http://127.0.0.1:5000")
    print("Press CTRL+C to stop the server")
    print("=" * 60)

    app.run(debug=True, host='127.0.0.1', port=5000)
