import sqlite3
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "students.db")

def init_db():
    """Initialize the database with the students table"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            attendance REAL,
            study_hours REAL,
            previous_grades REAL,
            assignments_completed REAL,
            participation INTEGER,
            performance REAL,
            risk_level TEXT,
            major TEXT,
            year_of_study TEXT,
            gender TEXT,
            ethnicity TEXT,
            parent_education TEXT,
            family_income TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_students(df):
    """Add new students to the database (upsert)"""
    conn = sqlite3.connect(DB_NAME)
    # Using 'replace' to handle duplicates (updates existing records)
    # Ideally we'd use upsert, but replace is simpler for this scope
    df.to_sql('students', conn, if_exists='replace', index=False)
    conn.close()
    return len(df)

def get_all_students():
    """Retrieve all students from the database"""
    if not os.path.exists(DB_NAME):
        return []
    
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql_query("SELECT * FROM students", conn)
        return df.to_dict('records')
    except Exception:
        return []
    finally:
        conn.close()

def get_student_dataframe():
    """Retrieve all students as a pandas DataFrame"""
    if not os.path.exists(DB_NAME):
        return pd.DataFrame()
    
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql_query("SELECT * FROM students", conn)
        return df
    except Exception:
        return pd.DataFrame()
    finally:
        conn.close()

def clear_data():
    """Clear all data from the database"""
    if os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("DELETE FROM students")
        conn.commit()
        conn.close()
