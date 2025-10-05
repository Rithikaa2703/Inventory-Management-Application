"""
Inventory Management System - Flask Application

A comprehensive inventory management system built with Flask that provides
functionality for managing products, locations, and tracking inventory movements.

Author: Generated Application
Date: October 3, 2025
Version: 1.0.0
"""

# Standard library imports
import csv
import io
import logging
import os
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Third-party imports
from flask import Flask, flash, redirect, render_template, request, send_file, url_for
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

# Local imports
from database import (
    get_all_locations,
    get_all_products,
    get_db,
    get_inventory_report,
    get_recent_movements,
    init_db,
    populate_initial_data
)

# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================

class Config:
    """Application configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super_secret_key_for_flash'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    HOST = os.environ.get('FLASK_HOST', '127.0.0.1')
    PORT = int(os.environ.get('FLASK_PORT', 5000))

# ============================================================================
# APPLICATION FACTORY
# ============================================================================

def create_app(config_class=Config) -> Flask:
    """
    Create and configure the Flask application.
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure logging
    if not app.debug:
        logging.basicConfig(level=logging.INFO)
    
    # Initialize database when the app starts
    with app.app_context():
        # Database initialization happens on import
        pass
    
    return app

# Create application instance
app = create_app()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def handle_database_error(operation: str, error: Exception) -> None:
    """
    Handle database errors consistently.
    
    Args:
        operation: Description of the operation that failed
        error: The exception that occurred
    """
    if isinstance(error, sqlite3.IntegrityError):
        flash(f'Database integrity error during {operation}: {str(error)}', 'error')
    else:
        flash(f'An unexpected error occurred during {operation}: {str(error)}', 'error')
        app.logger.error(f'Database error in {operation}: {str(error)}')

def validate_input(value: str, field_name: str) -> bool:
    """
    Validate input fields.
    
    Args:
        value: The value to validate
        field_name: Name of the field for error messages
        
    Returns:
        True if valid, False otherwise
    """
    if not value or not value.strip():
        flash(f'{field_name} cannot be empty.', 'error')
        return False
    return True

# ============================================================================
# MAIN/DASHBOARD ROUTES
# ============================================================================

@app.route('/')
def index() -> str:
    """
    Render the main dashboard page with inventory report.
    
    Returns:
        Rendered HTML template for the inventory report
    """
    try:
        report_data = get_inventory_report()
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
    except Exception as e:
        handle_database_error('loading dashboard', e)
        return render_template('index.html', active_page='report')

# ============================================================================
# PRODUCT MANAGEMENT ROUTES
# ============================================================================

@app.route('/products', methods=['GET'])
def products_view() -> str:
    """
    Render the Products management page.
    
    Returns:
        Rendered HTML template for product management
    """
    try:
        products = get_all_products()
        locations = get_all_locations()
        movements = get_recent_movements()
        
        return render_template(
            'index.html', 
            active_page='products',
            products=products,
            locations=locations,
            movements=movements
        )
    except Exception as e:
        handle_database_error('loading products', e)
        return render_template('index.html', active_page='products')

@app.route('/products/add', methods=['POST'])
def add_product() -> str:
    """
    Handle adding a new product.
    
    Returns:
        Redirect to products view
    """
    name = request.form.get('name', '').strip()
    
    if not validate_input(name, 'Product name'):
        return redirect(url_for('products_view'))
    
    try:
        with get_db() as db:
            product_id = str(uuid.uuid4())
            db.execute(
                "INSERT INTO Product (product_id, name) VALUES (?, ?)", 
                (product_id, name)
            )
            db.commit()
            flash(f'Product "{name}" added successfully!', 'success')
            app.logger.info(f'Added new product: {name} (ID: {product_id})')
    except Exception as e:
        handle_database_error('adding product', e)

    return redirect(url_for('products_view'))

@app.route('/products/edit/<product_id>', methods=['POST'])
def edit_product(product_id: str) -> str:
    """
    Handle editing an existing product.
    
    Args:
        product_id: UUID of the product to edit
        
    Returns:
        Redirect to products view
    """
    name = request.form.get('name', '').strip()
    
    if not validate_input(name, 'Product name'):
        return redirect(url_for('products_view'))
    
    try:
        with get_db() as db:
            # Verify product exists
            product = db.execute(
                "SELECT * FROM Product WHERE product_id = ?", 
                (product_id,)
            ).fetchone()
            
            if not product:
                flash('Product not found.', 'error')
            else:
                db.execute(
                    "UPDATE Product SET name = ? WHERE product_id = ?", 
                    (name, product_id)
                )
                db.commit()
                flash(f'Product updated to "{name}" successfully!', 'success')
                app.logger.info(f'Updated product {product_id}: {product["name"]} -> {name}')
    except Exception as e:
        handle_database_error('updating product', e)
    
    return redirect(url_for('products_view'))

@app.route('/products/delete/<product_id>', methods=['POST'])
def delete_product(product_id: str) -> str:
    """
    Handle deleting a product.
    
    Args:
        product_id: UUID of the product to delete
        
    Returns:
        Redirect to products view
    """
    try:
        with get_db() as db:
            # Verify product exists
            product = db.execute(
                "SELECT * FROM Product WHERE product_id = ?", 
                (product_id,)
            ).fetchone()
            
            if not product:
                flash('Product not found.', 'error')
            else:
                # Check for movement history
                movements = db.execute(
                    "SELECT COUNT(*) as count FROM ProductMovement WHERE product_id = ?", 
                    (product_id,)
                ).fetchone()
                
                if movements['count'] > 0:
                    flash(
                        f'Cannot delete product "{product["name"]}" because it has movement history.', 
                        'error'
                    )
                else:
                    db.execute("DELETE FROM Product WHERE product_id = ?", (product_id,))
                    db.commit()
                    flash(f'Product "{product["name"]}" deleted successfully!', 'success')
                    app.logger.info(f'Deleted product: {product["name"]} (ID: {product_id})')
    except Exception as e:
        handle_database_error('deleting product', e)
    
    return redirect(url_for('products_view'))

# ============================================================================
# LOCATION MANAGEMENT ROUTES
# ============================================================================

@app.route('/locations', methods=['GET'])
def locations_view() -> str:
    """
    Render the Locations management page.
    
    Returns:
        Rendered HTML template for location management
    """
    try:
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
    except Exception as e:
        handle_database_error('loading locations', e)
        return render_template('index.html', active_page='locations')

@app.route('/locations/add', methods=['POST'])
def add_location() -> str:
    """
    Handle adding a new location.
    
    Returns:
        Redirect to locations view
    """
    name = request.form.get('name', '').strip()
    
    if not validate_input(name, 'Location name'):
        return redirect(url_for('locations_view'))
    
    try:
        with get_db() as db:
            location_id = str(uuid.uuid4())
            db.execute(
                "INSERT INTO Location (location_id, name) VALUES (?, ?)", 
                (location_id, name)
            )
            db.commit()
            flash(f'Location "{name}" added successfully!', 'success')
            app.logger.info(f'Added new location: {name} (ID: {location_id})')
    except Exception as e:
        handle_database_error('adding location', e)

    return redirect(url_for('locations_view'))

@app.route('/locations/edit/<location_id>', methods=['POST'])
def edit_location(location_id: str) -> str:
    """
    Handle editing an existing location.
    
    Args:
        location_id: UUID of the location to edit
        
    Returns:
        Redirect to locations view
    """
    name = request.form.get('name', '').strip()
    
    if not validate_input(name, 'Location name'):
        return redirect(url_for('locations_view'))
    
    try:
        with get_db() as db:
            # Verify location exists
            location = db.execute(
                "SELECT * FROM Location WHERE location_id = ?", 
                (location_id,)
            ).fetchone()
            
            if not location:
                flash('Location not found.', 'error')
            else:
                db.execute(
                    "UPDATE Location SET name = ? WHERE location_id = ?", 
                    (name, location_id)
                )
                db.commit()
                flash(f'Location updated to "{name}" successfully!', 'success')
                app.logger.info(f'Updated location {location_id}: {location["name"]} -> {name}')
    except Exception as e:
        handle_database_error('updating location', e)
    
    return redirect(url_for('locations_view'))

@app.route('/locations/delete/<location_id>', methods=['POST'])
def delete_location(location_id: str) -> str:
    """
    Handle deleting a location.
    
    Args:
        location_id: UUID of the location to delete
        
    Returns:
        Redirect to locations view
    """
    try:
        with get_db() as db:
            # Verify location exists
            location = db.execute(
                "SELECT * FROM Location WHERE location_id = ?", 
                (location_id,)
            ).fetchone()
            
            if not location:
                flash('Location not found.', 'error')
            else:
                # Check for movement history
                movements = db.execute(
                    "SELECT COUNT(*) as count FROM ProductMovement WHERE from_location = ? OR to_location = ?", 
                    (location_id, location_id)
                ).fetchone()
                
                if movements['count'] > 0:
                    flash(
                        f'Cannot delete location "{location["name"]}" because it has movement history.', 
                        'error'
                    )
                else:
                    db.execute("DELETE FROM Location WHERE location_id = ?", (location_id,))
                    db.commit()
                    flash(f'Location "{location["name"]}" deleted successfully!', 'success')
                    app.logger.info(f'Deleted location: {location["name"]} (ID: {location_id})')
    except Exception as e:
        handle_database_error('deleting location', e)
    
    return redirect(url_for('locations_view'))

# ============================================================================
# MOVEMENT MANAGEMENT ROUTES
# ============================================================================

@app.route('/movements', methods=['GET'])
def movements_view() -> str:
    """
    Render the Movements tracking page.
    
    Returns:
        Rendered HTML template for movement management
    """
    try:
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
    except Exception as e:
        handle_database_error('loading movements', e)
        return render_template('index.html', active_page='movements')

@app.route('/movements/add', methods=['POST'])
def add_movement() -> str:
    """
    Handle adding a new movement record.
    
    Returns:
        Redirect to movements view
    """
    # Extract form data
    product_id = request.form.get('product_id')
    from_location = request.form.get('from_location')
    to_location = request.form.get('to_location')
    qty_str = request.form.get('qty')

    # Validate required fields
    if not product_id or not qty_str:
        flash('Product and Quantity are required.', 'error')
        return redirect(url_for('movements_view'))
    
    # Validate quantity
    try:
        qty = int(qty_str)
        if qty <= 0:
            flash('Quantity must be greater than zero.', 'error')
            return redirect(url_for('movements_view'))
    except ValueError:
        flash('Quantity must be a valid number.', 'error')
        return redirect(url_for('movements_view'))

    # Validate business rules
    if not from_location and not to_location:
        flash('Movement must have a "From" or "To" location (or both).', 'error')
        return redirect(url_for('movements_view'))
    
    # Convert empty strings to None for database
    from_location_db = from_location if from_location else None
    to_location_db = to_location if to_location else None

    # Validate same source and destination
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
            app.logger.info(f'Recorded movement: Product {product_id}, Qty {qty}, From {from_location_db}, To {to_location_db}')
    except Exception as e:
        handle_database_error('recording movement', e)

    return redirect(url_for('movements_view'))

# ============================================================================
# REPORTING ROUTES
# ============================================================================

@app.route('/report/download', methods=['GET'])
def download_report() -> str:
    """
    Generate and download a PDF inventory report.
    
    Returns:
        PDF file download or redirect on error
    """
    try:
        report_data = get_inventory_report()

        if not report_data:
            flash("No data available to generate PDF.", "error")
            return redirect(url_for("index"))

        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Add title
        styles = getSampleStyleSheet()
        title = Paragraph("📊 Inventory Report", styles['Title'])
        elements.append(title)

        # Prepare table data
        first_row = report_data[0]
        if hasattr(first_row, 'keys'):
            columns = list(first_row.keys())
            table_data = [columns] + [[str(row[col]) for col in columns] for row in report_data]
        else:
            # Fallback for tuple/list data
            num_cols = len(first_row)
            columns = [f"Column {i+1}" for i in range(num_cols)]
            table_data = [columns] + [list(map(str, row)) for row in report_data]

        # Create and style table
        table = Table(table_data, hAlign='LEFT')
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4CAF50")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)

        # Build PDF
        doc.build(elements)
        buffer.seek(0)

        app.logger.info('Generated PDF inventory report')
        return send_file(
            buffer,
            as_attachment=True,
            download_name="inventory_report.pdf",
            mimetype="application/pdf"
        )
    except Exception as e:
        handle_database_error('generating PDF report', e)
        return redirect(url_for("index"))

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    flash('Page not found.', 'error')
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    flash('An internal server error occurred.', 'error')
    app.logger.error(f'Internal server error: {str(error)}')
    return redirect(url_for('index'))

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    """Run the Flask application."""
    app.run(
        debug=Config.DEBUG,
        host=Config.HOST,
        port=Config.PORT
    )