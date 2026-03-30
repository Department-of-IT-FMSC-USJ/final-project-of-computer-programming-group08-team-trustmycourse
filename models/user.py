import hashlib
from database.connection import DatabaseConnection


class User:
    """Handles user registration, login, and profile operations."""

    def __init__(self):
        self.db = DatabaseConnection()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, email, password, role="student", institution="", country=""):
        """Register a new user."""
        self.db.connect()
        existing = self.db.fetch_one(
            "SELECT user_id FROM users WHERE email = %s", (email,)
        )
        if existing:
            self.db.disconnect()
            return {"success": False, "message": "Email already registered"}

        hashed = self.hash_password(password)
        query = """
            INSERT INTO users (username, email, password, role, institution, country)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        user_id = self.db.execute_query(query, (username, email, hashed, role, institution, country))
        self.db.disconnect()

        if user_id:
            return {"success": True, "message": "Registration successful", "user_id": user_id}
        return {"success": False, "message": "Registration failed"}

    def login(self, email, password):
        self.db.connect()
        hashed = self.hash_password(password)
        user = self.db.fetch_one(
            "SELECT * FROM users WHERE email = %s AND password = %s",
            (email, hashed)
        )
        self.db.disconnect()
        if user:
            return {"success": True, "user": user}
        return {"success": False, "message": "Invalid email or password"}

    def get_user_by_id(self, user_id):
        self.db.connect()
        user = self.db.fetch_one(
            "SELECT user_id, username, email, role, institution, country, created_at FROM users WHERE user_id = %s",
            (user_id,)
        )
        self.db.disconnect()
        return user