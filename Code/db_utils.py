import os
import sqlite3

def get_db_path():
    """Returns the absolute path to the database file in the Code directory"""
    code_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(code_dir, 'supermarket.db')

def get_connection():
    """Returns a connection to the database"""
    return sqlite3.connect(get_db_path())