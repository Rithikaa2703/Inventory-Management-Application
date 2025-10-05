import sqlite3
from datetime import datetime
import os
import uuid 

DATABASE = 'inventory.db'

def get_db():
    """Connects to the specific database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn

def init_db():
    """Initializes the database schema."""
    with get_db() as db:
        # Enable foreign keys for integrity
        db.execute('PRAGMA foreign_keys = ON;')
        
        # Products table
        db.execute('''
            CREATE TABLE IF NOT EXISTS Product (
                product_id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL
            );
        ''')
        
        # Locations table (Warehouses)
        db.execute('''
            CREATE TABLE IF NOT EXISTS Location (
                location_id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL
            );
        ''')
        
        # Movements table
        # FOREIGN KEY Note: ON DELETE NO ACTION means deleting a product/location will fail 
        # if any movement still references it, preventing data corruption.
        db.execute('''
            CREATE TABLE IF NOT EXISTS ProductMovement (
                movement_id INTEGER PRIMARY KEY,
                timestamp DATETIME NOT NULL,
                from_location TEXT,
                to_location TEXT,
                product_id TEXT NOT NULL,
                qty INTEGER NOT NULL,
                FOREIGN KEY (product_id) REFERENCES Product(product_id) ON DELETE NO ACTION,
                FOREIGN KEY (from_location) REFERENCES Location(location_id) ON DELETE NO ACTION,
                FOREIGN KEY (to_location) REFERENCES Location(location_id) ON DELETE NO ACTION
            );
        ''')
        db.commit()

# --- Utility Data Functions ---

def get_all_products():
    """Fetches all products."""
    with get_db() as db:
        return db.execute('SELECT * FROM Product ORDER BY name').fetchall()

def get_all_locations():
    """Fetches all locations."""
    with get_db() as db:
        return db.execute('SELECT * FROM Location ORDER BY name').fetchall()

def get_recent_movements():
    """Fetches the 20 most recent movements."""
    with get_db() as db:
        query = """
        SELECT 
            m.movement_id, m.timestamp, m.qty,
            p.name AS product_name,
            l_from.name AS from_location_name,
            l_to.name AS to_location_name
        FROM ProductMovement m
        JOIN Product p ON m.product_id = p.product_id
        LEFT JOIN Location l_from ON m.from_location = l_from.location_id
        LEFT JOIN Location l_to ON m.to_location = l_to.location_id
        ORDER BY m.timestamp DESC
        LIMIT 20;
        """
        return db.execute(query).fetchall()

def get_inventory_report():
    """
    Calculates the current stock balance for all products in all locations.
    """
    with get_db() as db:
        movement_summary_query = """
        WITH MovementSummary AS (
            -- Stock In (To Location)
            SELECT 
                to_location AS location_id,
                product_id,
                qty AS change_qty
            FROM ProductMovement
            WHERE to_location IS NOT NULL
            
            UNION ALL
            
            -- Stock Out (From Location)
            SELECT 
                from_location AS location_id,
                product_id,
                qty * -1 AS change_qty -- Subtract stock by making quantity negative
            FROM ProductMovement
            WHERE from_location IS NOT NULL
        )
        
        -- Final Report Query: Group and sum the changes
        SELECT 
            p.name AS product_name,
            l.name AS location_name,
            SUM(ms.change_qty) AS final_qty
        FROM MovementSummary ms
        JOIN Product p ON ms.product_id = p.product_id
        JOIN Location l ON ms.location_id = l.location_id
        GROUP BY 
            p.name, l.name
        HAVING 
            final_qty > 0
        ORDER BY 
            p.name, l.name;
        """
        
        report = db.execute(movement_summary_query).fetchall()
        return report

# --- Update Functions ---

def update_product(product_id, new_name):
    """Updates the name of an existing product."""
    with get_db() as db:
        db.execute("UPDATE Product SET name = ? WHERE product_id = ?", (new_name, product_id))
        db.commit()

def update_location(location_id, new_name):
    """Updates the name of an existing location."""
    with get_db() as db:
        db.execute("UPDATE Location SET name = ? WHERE location_id = ?", (new_name, location_id))
        db.commit()

# --- Delete Functions ---

def delete_product(product_id):
    """Deletes a product by ID. Fails if movements reference it."""
    with get_db() as db:
        # Fails if any movement uses this product_id due to FOREIGN KEY constraint
        db.execute("DELETE FROM Product WHERE product_id = ?", (product_id,))
        db.commit()

def delete_location(location_id):
    """Deletes a location by ID. Fails if movements reference it."""
    with get_db() as db:
        # Fails if any movement uses this location_id due to FOREIGN KEY constraint
        db.execute("DELETE FROM Location WHERE location_id = ?", (location_id,))
        db.commit()


def populate_initial_data():
    """Populates required test data if tables are empty."""
    with get_db() as db:
        # Check if Product table is empty
        if db.execute("SELECT COUNT(*) FROM Product").fetchone()[0] > 0:
            return  # Data already exists

        print("--- Populating initial test data ---")

        # Products (Laptop, Mouse, Keyboard)
        # Using simple IDs for initial data that won't be deleted for foreign key stability
        db.execute("INSERT INTO Product (product_id, name) VALUES (?, ?)", ('p1', 'Laptop'))
        db.execute("INSERT INTO Product (product_id, name) VALUES (?, ?)", ('p2', 'Mouse'))
        db.execute("INSERT INTO Product (product_id, name) VALUES (?, ?)", ('p3', 'Keyboard'))
        
        # Retrieve the generated IDs for movements
        products_map = {row['name']: row['product_id'] for row in db.execute("SELECT product_id, name FROM Product").fetchall()}
        
        # Locations (Location X, Y, Z)
        db.execute("INSERT INTO Location (location_id, name) VALUES (?, ?)", ('l1', 'Location X'))
        db.execute("INSERT INTO Location (location_id, name) VALUES (?, ?)", ('l2', 'Location Y'))
        db.execute("INSERT INTO Location (location_id, name) VALUES (?, ?)", ('l3', 'Location Z'))

        locations_map = {row['name']: row['location_id'] for row in db.execute("SELECT location_id, name FROM Location").fetchall()}

        p1, p2, p3 = products_map['Laptop'], products_map['Mouse'], products_map['Keyboard']
        l1, l2, l3 = locations_map['Location X'], locations_map['Location Y'], locations_map['Location Z']

        # Movements (20 records) - Timestamps are approximated
        now = datetime.now()
        
        def insert_movement(product_id, from_id, to_id, qty, offset_seconds):
            ts = now.timestamp() - offset_seconds
            db.execute("INSERT INTO ProductMovement (timestamp, from_location, to_location, product_id, qty) VALUES (?, ?, ?, ?, ?)",
                       (datetime.fromtimestamp(ts), from_id, to_id, product_id, qty))

        # 1. Initial Stock-In (3)
        insert_movement(p1, None, l1, 50, 100) # Laptop to Location X
        insert_movement(p2, None, l1, 100, 90) # Mouse to Location X
        insert_movement(p3, None, l2, 15, 80)  # Keyboard to Location Y

        # 2. Transfer Laptop (p1) from Location X (l1) to Location Y (l2) (5 movements)
        for i in range(5):
             insert_movement(p1, l1, l2, 5, 70 - i)
        
        # 3. Transfer Mouse (p2) from Location X (l1) to Location Z (l3) (5 movements)
        for i in range(5):
             insert_movement(p2, l1, l3, 10, 60 - i)
        
        # 4. Stock-Out/Sale Keyboard (p3) from Location Y (l2) (5 movements)
        for i in range(5):
             insert_movement(p3, l2, None, 2, 50 - i)

        # 5. Additional Stock-In (2 movements, bringing total to 20 records)
        insert_movement(p2, None, l1, 50, 40) # Mouse to Location X
        insert_movement(p1, None, l1, 10, 30) # Laptop to Location X
        
        db.commit()
        print("--- Initial data population complete ---")


# Initialize database on module load
if not os.path.exists(DATABASE) or os.path.getsize(DATABASE) == 0:
    init_db()
    populate_initial_data()
