# Flask and standard library imports
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import sqlite3
import io
import csv
import uuid
from datetime import datetime

# Third-party imports
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# Local imports
from database import (
    get_all_products, get_all_locations, get_recent_movements, 
    get_inventory_report, get_db, init_db, populate_initial_data
)

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_flash' # Required for flash messages

# Initialize DB when the app starts
with app.app_context():
    # init_db() and populate_initial_data() are called on database.py import
    pass

@app.route('/')
def index():
    """Renders the main index page (Inventory Report)."""
    # Fetch report data using the new SQLite function
    report_data = get_inventory_report()
    
    # Fetch data for dropdowns (even though this page only shows the report)
    products = get_all_products()
    locations = get_all_locations()
    movements = get_recent_movements()

    return render_template(
        'index.html', 
        active_page='report',
        report_data=report_data,
        products=products,
        locations=locations,
        movements=movements
    )

# --- CRUD Routes for Products ---

@app.route('/products', methods=['GET'])
def products_view():
    """Renders the Products management page."""
    products = get_all_products()
    locations = get_all_locations()
    movements = get_recent_movements()
    
    # Render with necessary data, passing only products list
    return render_template(
        'index.html', 
        active_page='products',
        products=products,
        locations=locations,
        movements=movements
    )

@app.route('/products/add', methods=['POST'])
def add_product():
    """Handles adding a new product."""
    name = request.form.get('name').strip()
    if not name:
        flash('Product name cannot be empty.', 'error')
    else:
        try:
            with get_db() as db:
                product_id = str(uuid.uuid4())  # Generate UUID for primary key
                db.execute("INSERT INTO Product (product_id, name) VALUES (?, ?)", (product_id, name))
                db.commit()
                flash(f'Product "{name}" added successfully!', 'success')
        except sqlite3.IntegrityError:
            flash(f'Error: Product name "{name}" already exists.', 'error')
        except Exception as e:
            flash(f'An error occurred while adding product: {e}', 'error')

    return redirect(url_for('products_view'))

@app.route('/products/edit/<product_id>', methods=['POST'])
def edit_product(product_id):
    """Handles editing an existing product."""
    name = request.form.get('name').strip()
    if not name:
        flash('Product name cannot be empty.', 'error')
    else:
        try:
            with get_db() as db:
                # Check if product exists
                product = db.execute("SELECT * FROM Product WHERE product_id = ?", (product_id,)).fetchone()
                if not product:
                    flash('Product not found.', 'error')
                else:
                    db.execute("UPDATE Product SET name = ? WHERE product_id = ?", (name, product_id))
                    db.commit()
                    flash(f'Product updated to "{name}" successfully!', 'success')
        except sqlite3.IntegrityError:
            flash(f'Error: Product name "{name}" already exists.', 'error')
        except Exception as e:
            flash(f'An error occurred while updating product: {e}', 'error')
    
    return redirect(url_for('products_view'))

@app.route('/products/delete/<product_id>', methods=['POST'])
def delete_product(product_id):
    """Handles deleting a product."""
    try:
        with get_db() as db:
            # Check if product exists
            product = db.execute("SELECT * FROM Product WHERE product_id = ?", (product_id,)).fetchone()
            if not product:
                flash('Product not found.', 'error')
            else:
                # Check if product is used in any movements
                movements = db.execute("SELECT COUNT(*) as count FROM ProductMovement WHERE product_id = ?", (product_id,)).fetchone()
                if movements['count'] > 0:
                    flash(f'Cannot delete product "{product["name"]}" because it has movement history.', 'error')
                else:
                    db.execute("DELETE FROM Product WHERE product_id = ?", (product_id,))
                    db.commit()
                    flash(f'Product "{product["name"]}" deleted successfully!', 'success')
    except Exception as e:
        flash(f'An error occurred while deleting product: {e}', 'error')
    
    return redirect(url_for('products_view'))

# --- CRUD Routes for Locations ---

@app.route('/locations', methods=['GET'])
def locations_view():
    """Renders the Locations management page."""
    products = get_all_products()
    locations = get_all_locations()
    movements = get_recent_movements()
    
    return render_template(
        'index.html', 
        active_page='locations',
        products=products,
        locations=locations,
        movements=movements
    )

@app.route('/locations/add', methods=['POST'])
def add_location():
    """Handles adding a new location."""
    name = request.form.get('name').strip()
    if not name:
        flash('Location name cannot be empty.', 'error')
    else:
        try:
            with get_db() as db:
                location_id = str(uuid.uuid4()) # Generate UUID for primary key
                db.execute("INSERT INTO Location (location_id, name) VALUES (?, ?)", (location_id, name))
                db.commit()
                flash(f'Location "{name}" added successfully!', 'success')
        except sqlite3.IntegrityError:
            flash(f'Error: Location name "{name}" already exists.', 'error')
        except Exception as e:
            flash(f'An error occurred while adding location: {e}', 'error')

    return redirect(url_for('locations_view'))

@app.route('/locations/edit/<location_id>', methods=['POST'])
def edit_location(location_id):
    """Handles editing an existing location."""
    name = request.form.get('name').strip()
    if not name:
        flash('Location name cannot be empty.', 'error')
    else:
        try:
            with get_db() as db:
                # Check if location exists
                location = db.execute("SELECT * FROM Location WHERE location_id = ?", (location_id,)).fetchone()
                if not location:
                    flash('Location not found.', 'error')
                else:
                    db.execute("UPDATE Location SET name = ? WHERE location_id = ?", (name, location_id))
                    db.commit()
                    flash(f'Location updated to "{name}" successfully!', 'success')
        except sqlite3.IntegrityError:
            flash(f'Error: Location name "{name}" already exists.', 'error')
        except Exception as e:
            flash(f'An error occurred while updating location: {e}', 'error')
    
    return redirect(url_for('locations_view'))

@app.route('/locations/delete/<location_id>', methods=['POST'])
def delete_location(location_id):
    """Handles deleting a location."""
    try:
        with get_db() as db:
            # Check if location exists
            location = db.execute("SELECT * FROM Location WHERE location_id = ?", (location_id,)).fetchone()
            if not location:
                flash('Location not found.', 'error')
            else:
                # Check if location is used in any movements
                movements = db.execute(
                    "SELECT COUNT(*) as count FROM ProductMovement WHERE from_location = ? OR to_location = ?", 
                    (location_id, location_id)
                ).fetchone()
                if movements['count'] > 0:
                    flash(f'Cannot delete location "{location["name"]}" because it has movement history.', 'error')
                else:
                    db.execute("DELETE FROM Location WHERE location_id = ?", (location_id,))
                    db.commit()
                    flash(f'Location "{location["name"]}" deleted successfully!', 'success')
    except Exception as e:
        flash(f'An error occurred while deleting location: {e}', 'error')
    
    return redirect(url_for('locations_view'))

# --- Movement Routes ---

@app.route('/movements', methods=['GET'])
def movements_view():
    """Renders the Movements page."""
    products = get_all_products()
    locations = get_all_locations()
    movements = get_recent_movements()
    
    return render_template(
        'index.html', 
        active_page='movements',
        products=products,
        locations=locations,
        movements=movements
    )

@app.route('/movements/add', methods=['POST'])
def add_movement():
    """Handles adding a new movement record."""
    product_id = request.form.get('product_id')
    from_location = request.form.get('from_location')
    to_location = request.form.get('to_location')
    qty_str = request.form.get('qty')

    if not product_id or not qty_str:
        flash('Product and Quantity are required.', 'error')
        return redirect(url_for('movements_view'))
    
    try:
        qty = int(qty_str)
        if qty <= 0:
            flash('Quantity must be greater than zero.', 'error')
            return redirect(url_for('movements_view'))
    except ValueError:
        flash('Quantity must be a valid number.', 'error')
        return redirect(url_for('movements_view'))

    # Check for the core business rule
    if not from_location and not to_location:
        flash('Movement must have a "From" or "To" location (or both).', 'error')
        return redirect(url_for('movements_view'))
    
    # Set blank values to None for database (SQLite NULL)
    from_location_db = from_location if from_location else None
    to_location_db = to_location if to_location else None

    # Optional: Check if source and destination are the same
    if from_location_db and to_location_db and from_location_db == to_location_db:
        flash('Source and Destination locations cannot be the same.', 'error')
        return redirect(url_for('movements_view'))
        
    try:
        with get_db() as db:
            db.execute(
                "INSERT INTO ProductMovement (timestamp, from_location, to_location, product_id, qty) VALUES (?, ?, ?, ?, ?)",
                (datetime.now(), from_location_db, to_location_db, product_id, qty)
            )
            db.commit()
            flash('Movement recorded successfully!', 'success')
    except Exception as e:
        flash(f'An error occurred while recording movement: {e}', 'error')

    return redirect(url_for('movements_view'))
@app.route('/report/download', methods=['GET'])
def download_report():
    """
    Generate a PDF of the overall inventory report and send it
    as a file download.
    """
    report_data = get_inventory_report()

    if not report_data:
        flash("No data available to generate PDF.", "error")
        return redirect(url_for("index"))

    # --- Prepare PDF in memory ---
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title = Paragraph("📊 Inventory Report", styles['Title'])
    elements.append(title)

    # Convert data to table format
    # Detect columns from first row
    first = report_data[0]
    if hasattr(first, 'keys'):  # sqlite3.Row or dict
        cols = list(first.keys())
        data = [cols] + [[str(r[c]) for c in cols] for r in report_data]
    elif isinstance(first, dict):
        cols = list(first.keys())
        data = [cols] + [[str(r.get(c, '')) for c in cols] for r in report_data]
    else:  # tuple/list
        ncols = len(first)
        cols = [f"Col {i+1}" for i in range(ncols)]
        data = [cols] + [list(map(str, r)) for r in report_data]

    # Build table
    table = Table(data, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4CAF50")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    # Return file for download
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"inventory_report.pdf",
        mimetype="application/pdf"
    )


# Entry point for running the Flask app
if __name__ == '__main__':
    app.run(debug=True)
