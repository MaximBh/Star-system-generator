import sqlite3

DB_FILE = "data/systems.sqlite"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    """Создаёт таблицы, если их ещё нет."""
    conn = get_connection()
    cur = conn.cursor()

    # Таблица систем
    cur.execute("""
        CREATE TABLE IF NOT EXISTS systems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            star_name TEXT,
            star_type TEXT,
            star_temperature REAL,
            star_radius REAL,
            planet_count INTEGER
        )
    """)

    # Таблица планет
    cur.execute("""
        CREATE TABLE IF NOT EXISTS planets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            system_name TEXT,
            name TEXT,
            temperature_c REAL,
            size_earth REAL,
            mass_earth REAL,
            orbital_radius_au REAL,
            orbital_period_days REAL,
            planet_type TEXT,
            atmosphere TEXT,
            life_probability REAL,
            satellites INTEGER,
            image_path TEXT,
            description TEXT
        )
    """)

    conn.commit()
    conn.close()
