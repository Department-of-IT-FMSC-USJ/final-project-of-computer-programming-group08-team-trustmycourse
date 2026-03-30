import mysql.connector
from mysql.connector import Error


class DatabaseConnection:
    """Handles MySQL database connection and CRUD operations."""

    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = ""   # Change this
        self.database = "trustmycourse"
        self.connection = None

    def connect(self):
        """Establish database connection."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
        except Error as e:
            print(f"Error connecting to database: {e}")

    def disconnect(self):
        """Close the database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")

    def execute_query(self, query, params=None):
        """Execute INSERT, UPDATE, DELETE queries."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Query error: {e}")
            self.connection.rollback()
            return None

    def fetch_one(self, query, params=None):
        """Fetch a single record."""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            return cursor.fetchone()
        except Error as e:
            print(f"Fetch error: {e}")
            return None

    def fetch_all(self, query, params=None):
        """Fetch multiple records."""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            return cursor.fetchall()
        except Error as e:
            print(f"Fetch error: {e}")
            return []