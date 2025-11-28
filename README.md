# Smart Kitchen Inventory System

A beginner-friendly Flask application for managing kitchen inventory, tracking expiry dates, and preventing food waste. Perfect for demonstrating full-stack web development skills.

**Created for: Shubham's Project Submission**

---

## Features

✅ **User Authentication** - Secure signup and login with password hashing  
✅ **Dashboard** - Real-time statistics (total items, expiring soon, low stock, expired items)  
✅ **Inventory Management** - Add, edit, delete kitchen items with categories  
✅ **Barcode Scanning** - Real-time barcode scanning using camera (supports CODE_128, EAN, UPC, CODE_39)  
✅ **Smart Alerts** - Automatic alerts for expiring and low-stock items  
✅ **Search & Filter** - Find items by name or filter by category  
✅ **CSV Import/Export** - Bulk upload or download your inventory  
✅ **Responsive Design** - Works on desktop, tablet, and mobile devices  

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend Framework** | Flask 3.0.3 |
| **Database** | SQLite3 |
| **ORM** | Flask-SQLAlchemy 2.5.1 |
| **Frontend Framework** | Bootstrap 5.3.0 |
| **Templating** | Jinja2 |
| **Barcode Scanner** | QuaggaJS 2 (Camera-based) |
| **Security** | werkzeug (Password hashing) |
| **Environment** | python-dotenv 1.0.1 |

---

## Project Structure

```
smart_kitchen/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables
├── README.md                      # This file
│
├── db/                            # Database folder
│   └── smart_kitchen.db           # SQLite database (auto-created)
│
├── templates/                     # HTML templates
│   ├── base.html                  # Base layout with navigation
│   ├── home.html                  # Landing page
│   ├── signup.html                # User registration
│   ├── login.html                 # User login
│   ├── dashboard.html             # Statistics dashboard
│   ├── items_list.html            # Inventory table view
│   ├── item_form.html             # Add/edit item form
│   ├── scan.html                  # Barcode scanner
│   └── error.html                 # Error pages (404, 500)
│
└── static/                        # Static files
    ├── css/
    │   └── style.css              # Custom Bootstrap styling
    └── js/
        └── app.js                 # JavaScript utilities
```

---

## Database Schema

### Users Table
```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Items Table
```sql
CREATE TABLE item (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    barcode VARCHAR(50),
    quantity FLOAT NOT NULL,
    unit VARCHAR(20),
    expiry_date DATE,
    location VARCHAR(50),
    low_stock_threshold FLOAT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES user(id) ON DELETE CASCADE
);
```

### Item Categories
- Dairy
- Vegetables
- Fruits
- Snacks
- Grains
- Spices
- Beverages
- Other

### Units
- pcs (pieces)
- kg (kilogram)
- g (gram)
- L (liter)
- ml (milliliter)
- box
- bottle

### Locations
- Pantry
- Fridge
- Freezer
- Shelf

---

## Installation & Setup

### Prerequisites
- Python 3.8+ installed
- pip (Python package manager)
- Modern web browser with camera support (for barcode scanning)

### Step 1: Clone/Download the Project
```bash
cd smart_kitchen
```

### Step 2: Create Virtual Environment
```bash
# On Windows:
python -m venv venv
venv\Scripts\activate

# On macOS/Linux:
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Create .env File (Already Included)
The `.env` file is included with a default SECRET_KEY. For production, change it to a secure random value.

### Step 5: Run the Application
```bash
python app.py
```

The application will be available at: **http://localhost:5000**

Database will auto-create at `db/smart_kitchen.db` on first run.

---

## Quick Start Guide

### 1. **Create an Account**
- Navigate to the Sign Up page
- Enter your name, email, and password
- Password must be at least 6 characters
- Click "Create Account"

### 2. **Login**
- Use your registered email and password
- You'll be redirected to the Dashboard

### 3. **Add Items**
- Click "Items" in the navigation
- Click "Add New Item" button
- Fill in the form:
  - **Name**: Item name (e.g., "Milk")
  - **Category**: Select from dropdown
  - **Barcode**: (Optional) Scan or enter manually
  - **Quantity**: How much you have
  - **Unit**: pcs, kg, L, etc.
  - **Expiry Date**: When it expires (optional)
  - **Location**: Where it's stored
  - **Low Stock Threshold**: Alert when quantity falls below this
- Click "Save Item"

### 4. **View Dashboard**
- See at-a-glance statistics:
  - Total items in inventory
  - Items expiring soon (within 7 days)
  - Items with low stock
  - Expired items
- Each stat card shows the count with an icon

### 5. **Search & Filter**
- Use the search box to find items by name
- Use the category dropdown to filter by type
- Results update in real-time

### 6. **Scan Barcodes**
- Click "Scan" in the navigation
- Allow camera access when prompted
- Point camera at a barcode
- Barcode code appears in the text field and history
- Click "Copy" to copy the barcode

### 7. **Edit/Delete Items**
- On the Items page, click "Edit" to modify an item
- Click "Delete" to remove an item (requires confirmation)

### 8. **Export Inventory**
- Click "Export CSV" on the Items page
- Download saved to your computer
- Perfect for backup or sharing

### 9. **Import Inventory**
- Click "Import CSV" button
- Upload a CSV file with columns: name, category, barcode, quantity, unit, expiry_date, location, low_stock_threshold
- Existing items will be updated, new items created

---

## Usage Examples

### Demo Account (for testing)
If you want to test without creating an account:
- Email: `demo@example.com`
- Password: `demo123`

*(Create this manually by signing up with these credentials)*

### Sample CSV Import Format
```csv
name,category,barcode,quantity,unit,expiry_date,location,low_stock_threshold
Milk,Dairy,5901234123457,1,L,2024-12-31,Fridge,0.2
Bread,Grains,5900000000000,2,pcs,2024-01-15,Pantry,1
Apples,Fruits,5000157000001,5,kg,2024-02-20,Fridge,2
```

---

## Key Features Explained

### Dashboard Statistics
- **Total Items**: Count of all items in your inventory
- **Expiring Soon**: Items expiring within 7 days (shown in yellow)
- **Low Stock**: Items below their threshold (shown in blue)
- **Expired**: Items past their expiry date (shown in red)

### Smart Alerts
- Automatic detection of expired items
- Low-stock warnings
- Color-coded badges on items list
- Status indicators: Good ✓ | Expiring ⚠ | Low Stock ⚠ | Expired ✗

### Barcode Scanner Features
- **Multiple Formats**: Supports CODE_128, EAN, UPC, CODE_39
- **Real-time**: Instant detection as you point camera at barcode
- **History**: Shows last 10 scanned barcodes
- **Copy Function**: One-click copy to clipboard
- **Audio Feedback**: Beep sound on successful scan

### CSV Operations
- **Export**: Download all items as CSV for backup
- **Import**: Bulk upload items from CSV file
- **Format**: Standard comma-separated values with headers

---

## Project for Submission

To demonstrate this project:

1. **Setup Phase** (2 minutes)
   - Run `pip install -r requirements.txt`
   - Run `python app.py`
   - Open http://localhost:5000

2. **Authentication Demo** (1 minute)
   - Sign up with test credentials
   - Show password validation
   - Login with credentials

3. **Add Items Demo** (2 minutes)
   - Add 5-10 sample items with different categories
   - Show validation (required fields, date format)
   - Show item editing

4. **Dashboard Demo** (1 minute)
   - Show statistics updating in real-time
   - Add items with future/past dates to show expiring/expired alerts

5. **Barcode Scanner Demo** (2 minutes)
   - Point camera at any barcode
   - Show real-time detection
   - Show scan history

6. **Search & Filter Demo** (1 minute)
   - Search for items
   - Filter by category
   - Show responsive table

7. **Export/Import Demo** (1 minute)
   - Export current inventory as CSV
   - Show CSV file
   - Import a new CSV file

8. **Code Review** (5 minutes)
   - Open `app.py` to show:
     - Database models (User, Item)
     - Authentication flow
     - CRUD operations
     - CSV handling
   - Show template files to demonstrate:
     - Jinja2 templating
     - Bootstrap 5 responsive design
     - JavaScript integration

**Total Demo Time: ~15 minutes**

---

## Troubleshooting

### Issue: "No module named 'flask'"
**Solution**: Run `pip install -r requirements.txt`

### Issue: "Database locked" error
**Solution**: Delete `db/smart_kitchen.db` and restart the app. A new database will be created.

### Issue: Barcode scanner shows black screen
**Solution**: 
- Check browser camera permissions
- Ensure camera is not in use by another application
- Try a different browser (Chrome/Edge work best)

### Issue: "SECRET_KEY" not found
**Solution**: Make sure `.env` file exists in the project root directory

### Issue: Items not saving
**Solution**: 
- Check that `db/` folder exists
- Ensure you have write permissions to the folder
- Check Flask error output in terminal

### Issue: Can't login after signup
**Solution**: 
- Check that email is exactly as registered
- Password is case-sensitive
- Database file wasn't deleted after signup

---

## Code Highlights

### Authentication with Password Hashing
```python
from werkzeug.security import generate_password_hash, check_password_hash

# Hashing password on signup
user.password_hash = generate_password_hash(password)

# Checking password on login
check_password_hash(user.password_hash, password)
```

### Database Relationships
```python
# User-Item relationship
class User(db.Model):
    items = db.relationship('Item', backref='user', lazy=True, cascade='all, delete-orphan')

# Auto-cascade delete: Deleting user removes all their items
```

### Item Status Methods
```python
# Checking item status
item.is_expired()           # Returns True if past expiry date
item.is_expiring_soon()     # Returns True if expiring within 7 days
item.is_low_stock()         # Returns True if quantity < threshold
item.to_dict()              # Converts to CSV format
```

### CSV Export
```python
# Convert items to CSV format with headers
csv_data = [['name', 'category', 'barcode', 'quantity', 'unit', 'expiry_date', 'location', 'low_stock_threshold']]
for item in items:
    csv_data.append(item.to_dict())
# Send as downloadable file
```

### Barcode Scanning
```javascript
// QuaggaJS initialization
Quagga.init({
    inputStream: { type: "LiveStream", constraints: { width: 640, height: 480 } },
    decoder: { readers: ["code_128_reader", "ean_reader", "upc_reader", "code_39_reader"] }
});

// Listen for barcode detection
Quagga.onDetected(function(result) {
    barcode = result.codeResult.code;
});
```

---

## Learning Outcomes

By studying this project, you'll learn:

✅ **Backend Development**
- Flask application structure and routing
- SQLAlchemy ORM and database relationships
- User authentication and password hashing
- File upload handling
- CSV processing

✅ **Frontend Development**
- Jinja2 template inheritance
- Bootstrap 5 responsive design
- Form validation
- JavaScript DOM manipulation
- Real-time search filtering

✅ **Database Design**
- One-to-Many relationships
- Foreign keys and cascading deletes
- SQLite3 basics
- Data validation

✅ **Web Development Best Practices**
- Session management
- Security (password hashing)
- Error handling
- Responsive design
- CSV import/export

---

## Deployment Notes

### For Production
1. Change `SECRET_KEY` in `.env` to a strong random value
2. Set `FLASK_DEBUG=False`
3. Use a production WSGI server (Gunicorn, Waitress)
4. Store `.env` securely (never commit to GitHub)
5. Use a proper database (PostgreSQL) instead of SQLite
6. Enable HTTPS
7. Add rate limiting and CSRF protection

### Sample Production Run (with Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## File Descriptions

| File | Purpose |
|------|---------|
| `app.py` | Main Flask application (370+ lines) with all routes and models |
| `templates/base.html` | Base layout with navigation bar and footer |
| `templates/home.html` | Public landing page with feature overview |
| `templates/signup.html` | User registration form |
| `templates/login.html` | User login form |
| `templates/dashboard.html` | Statistics dashboard with 4 metric cards |
| `templates/items_list.html` | Inventory table with search, filter, export/import |
| `templates/item_form.html` | Add/edit item form with validation |
| `templates/scan.html` | Barcode scanner with QuaggaJS |
| `templates/error.html` | Error page for 404/500 errors |
| `static/css/style.css` | Custom Bootstrap styling (300+ lines) |
| `static/js/app.js` | JavaScript utilities and helpers |

---

## Support & Debugging

### View Flask Logs
Check the terminal running `python app.py` for error messages.

### SQLite Browser
View/edit database with tools like:
- SQLite Browser (DB Browser for SQLite)
- VS Code SQLite extension
- Command line: `sqlite3 db/smart_kitchen.db`

### Browser Developer Tools
- Press F12 to open developer console
- Check Network tab for API responses
- Check Console for JavaScript errors

---

## Future Enhancements

Potential features to add:
- [ ] Email reminders for expiring items
- [ ] Photo upload for items
- [ ] Recipes based on available items
- [ ] Expense tracking
- [ ] Family sharing (multiple users)
- [ ] Mobile app (React Native/Flutter)
- [ ] Dark mode
- [ ] Multi-language support
- [ ] Integration with grocery APIs

---

## License

This project is created for educational purposes as part of a beginner Flask course.

---

## Author Notes

This Smart Kitchen Inventory System demonstrates:
- ✅ Full-stack web development (frontend + backend)
- ✅ Database design and relationships
- ✅ User authentication and security
- ✅ Real-world features (barcode scanning, CSV handling)
- ✅ Professional UI/UX with Bootstrap
- ✅ Clean, well-commented code for learning

**Perfect for portfolio and project submissions!**

---

**Questions?** Check the troubleshooting section or review the source code in `app.py` and template files.

**Last Updated:** 2024
**Python Version:** 3.8+
**Flask Version:** 3.0.3
