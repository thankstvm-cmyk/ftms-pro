import sqlite3

def create_database():
    conn = sqlite3.connect("ftms.db")
    cursor = conn.cursor()

    # VEHICLES TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_number TEXT UNIQUE NOT NULL,
        brand TEXT,
        model TEXT,
        year INTEGER,
        ton_capacity TEXT,
        body_type TEXT,
        chiller TEXT,
        tail_lift TEXT,
        tank_capacity REAL,
        expected_kmpl REAL,
        image_path TEXT,
        status TEXT
    )
    """)

    # DRIVERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS drivers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        driver_name TEXT NOT NULL,
        license_number TEXT,
        license_expiry DATE,
        contact_number TEXT,
        status TEXT
    )
    """)

    # ODOMETER ENTRIES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS odometer_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id INTEGER,
        date DATE,
        morning_reading REAL,
        evening_reading REAL,
        FOREIGN KEY(vehicle_id) REFERENCES vehicles(id)
    )
    """)

    # FUEL ENTRIES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fuel_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id INTEGER,
        driver_id INTEGER,
        date DATE,
        odometer_reading REAL,
        litres REAL,
        total_cost REAL,
        fuel_station TEXT,
        bill_number TEXT,
        FOREIGN KEY(vehicle_id) REFERENCES vehicles(id),
        FOREIGN KEY(driver_id) REFERENCES drivers(id)
    )
    """)

    # ACCIDENTS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id INTEGER,
        driver_id INTEGER,
        accident_date DATE,
        location TEXT,
        fault_status TEXT,
        police_report_no TEXT,
        repair_cost REAL,
        downtime_days INTEGER,
        status TEXT,
        FOREIGN KEY(vehicle_id) REFERENCES vehicles(id),
        FOREIGN KEY(driver_id) REFERENCES drivers(id)
    )
    """)

    # BREAKDOWNS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS breakdowns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id INTEGER,
        driver_id INTEGER,
        breakdown_date DATE,
        location TEXT,
        problem_description TEXT,
        repair_cost REAL,
        downtime_days INTEGER,
        status TEXT,
        FOREIGN KEY(vehicle_id) REFERENCES vehicles(id),
        FOREIGN KEY(driver_id) REFERENCES drivers(id)
    )
    """)

    # REPAIRS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS repairs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id INTEGER,
        repair_date DATE,
        repair_type TEXT,
        workshop TEXT,
        cost REAL,
        remarks TEXT,
        FOREIGN KEY(vehicle_id) REFERENCES vehicles(id)
    )
    """)

    # BATTERY REPLACEMENTS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS battery_replacements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id INTEGER,
        brand TEXT,
        serial_number TEXT,
        installation_date DATE,
        warranty_months INTEGER,
        cost REAL,
        replaced_by TEXT,
        old_returned TEXT,
        discount REAL,
        FOREIGN KEY(vehicle_id) REFERENCES vehicles(id)
    )
    """)

    # TYRE REPLACEMENTS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tyre_replacements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id INTEGER,
        brand TEXT,
        size TEXT,
        position TEXT,
        installation_date DATE,
        cost REAL,
        old_returned TEXT,
        FOREIGN KEY(vehicle_id) REFERENCES vehicles(id)
    )
    """)

    # ADMIN BASELINE TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin_baseline (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ton_capacity TEXT,
        body_type TEXT,
        chiller TEXT,
        tail_lift TEXT,
        default_kmpl REAL
    )
    """)

    conn.commit()
    conn.close()
    print("FTMS Database Created Successfully!")

if __name__ == "__main__":
    create_database()
