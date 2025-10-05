# 📦 Inventory Management System

A comprehensive, professional inventory management system built with Flask that provides complete functionality for managing products, locations, and tracking inventory movements.

## 🚀 Features

### Core Functionality
- **Product Management**: Add, edit, delete products with data integrity protection
- **Location Management**: Manage warehouses and storage locations  
- **Movement Tracking**: Record stock movements (purchases, sales, transfers)
- **Inventory Reporting**: Real-time inventory balance reports
- **PDF Export**: Download professional inventory reports

### Technical Features
- **Professional Architecture**: Clean, modular code structure
- **Type Hints**: Full type annotation for better code quality
- **Comprehensive Documentation**: Detailed docstrings and comments
- **Error Handling**: Robust error handling with user-friendly messages
- **Data Integrity**: Prevents deletion of items with movement history
- **Responsive Design**: Modern UI with Tailwind CSS
- **Smooth Animations**: Professional UI interactions

## 🛠️ Technology Stack

- **Backend**: Flask (Python 3.8+)
- **Database**: SQLite with proper foreign key constraints
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
- **PDF Generation**: ReportLab
- **Icons**: Lucide Icons

## 📋 Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)

## 🔧 Installation

1. **Clone or extract the project**
   ```bash
   cd Invention_Flask
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv .venv
   .venv\\Scripts\\activate

   # Linux/Mac
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask reportlab
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser and go to: `http://127.0.0.1:5000`

## 📁 Project Structure

```
Invention_Flask/
├── app.py                 # Main Flask application
├── database.py           # Database operations and models
├── inventory.db          # SQLite database (auto-created)
├── templates/
│   └── index.html        # Main HTML template
├── __pycache__/          # Python cache files
└── README.md            # This file
```

## 🎯 Usage Guide

### Dashboard (Inventory Report)
- View current stock levels by product and location
- Download PDF reports
- Quick overview of inventory status

### Product Management
- **Add Products**: Use the form to add new products
- **Edit Products**: Click "Edit" button on any product
- **Delete Products**: Click "Delete" with confirmation (blocked if movement history exists)

### Location Management
- **Add Locations**: Create warehouses or storage locations
- **Edit Locations**: Modify location names
- **Delete Locations**: Remove unused locations (blocked if movement history exists)

### Movement Tracking
- **Record Movements**: Track stock in/out/transfers
- **Movement Types**:
  - **Purchase**: Leave "From" empty, select "To" location
  - **Sale**: Select "From" location, leave "To" empty  
  - **Transfer**: Select both "From" and "To" locations
- **View History**: See recent movements in real-time

## 🔧 Configuration

The application supports environment variables for configuration:

```bash
# Optional environment variables
FLASK_DEBUG=True          # Enable debug mode
FLASK_HOST=127.0.0.1      # Host address
FLASK_PORT=5000           # Port number
SECRET_KEY=your_secret    # Flask secret key
```

## 🏗️ Architecture

### Application Structure
- **Factory Pattern**: Clean application initialization
- **Separation of Concerns**: Routes, database operations, and utilities are separated
- **Type Safety**: Full type hints for better code quality
- **Error Handling**: Comprehensive error handling with logging

### Database Schema
- **Products**: ID (UUID), Name (Unique)
- **Locations**: ID (UUID), Name (Unique)  
- **ProductMovements**: Timestamp, From/To Locations, Product, Quantity
- **Foreign Keys**: Proper referential integrity

### Frontend Architecture
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Progressive Enhancement**: Works without JavaScript, enhanced with JS
- **Modular CSS**: Organized styles with clear sections
- **Accessible**: Proper ARIA labels and semantic HTML

## 🔒 Data Integrity

- **Foreign Key Constraints**: Prevents orphaned records
- **Business Rules**: Enforces logical movement requirements
- **Validation**: Client and server-side validation
- **Confirmation Dialogs**: Prevents accidental deletions
- **History Protection**: Cannot delete items with movement history

## 🚨 Error Handling

- **Database Errors**: Graceful handling with user-friendly messages
- **Validation Errors**: Clear feedback for invalid inputs
- **404/500 Errors**: Professional error pages with redirects
- **Logging**: Comprehensive logging for debugging

## 🎨 UI/UX Features

- **Professional Design**: Clean, modern interface
- **Smooth Animations**: Hover effects and transitions
- **Color-Coded Actions**: Intuitive button colors (blue=primary, yellow=edit, red=delete)
- **Modal Dialogs**: Non-intrusive editing experience
- **Flash Messages**: Clear success/error notifications
- **Responsive Tables**: Mobile-friendly data display

## 🔄 Development

### Code Quality
- **PEP 8 Compliant**: Follows Python style guidelines
- **Type Hints**: Full type annotation
- **Docstrings**: Comprehensive documentation
- **Modular Design**: Easy to extend and maintain

### Adding Features
1. **New Routes**: Add to appropriate section in `app.py`
2. **Database Changes**: Modify `database.py`
3. **UI Updates**: Update `templates/index.html`
4. **Styling**: Use existing Tailwind classes for consistency

## 📈 Performance

- **Optimized Queries**: Efficient database operations
- **Minimal JavaScript**: Lightweight client-side code
- **CDN Resources**: Fast loading of external assets
- **Proper Indexing**: Database indexes for performance

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure Flask and ReportLab are installed
2. **Database Locked**: Close any existing database connections
3. **Permission Errors**: Check file permissions in project directory
4. **Port In Use**: Change port in configuration or kill existing process

### Debug Mode
- Set `FLASK_DEBUG=True` for detailed error messages
- Check browser console for JavaScript errors
- Review server logs in terminal

## 📝 License

This project is for educational and development purposes.

## 🤝 Contributing

1. Follow the existing code style and architecture
2. Add appropriate type hints and docstrings
3. Test all functionality before submitting
4. Update documentation for new features

---

**Author**: Flask Inventory System  
**Version**: 1.0.0  
**Date**: October 3, 2025