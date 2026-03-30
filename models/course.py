from database.connection import DatabaseConnection


class Course:
    """Handles course-related database operations."""

    def __init__(self):
        self.db = DatabaseConnection()

    def add_course(self, course_name, provider_name, institution, country, course_url=""):
        """Add a new course to the database."""
        self.db.connect()

        # Check if course already exists
        existing = self.db.fetch_one(
            "SELECT course_id FROM courses WHERE course_name = %s AND provider_name = %s",
            (course_name, provider_name)
        )
        if existing:
            self.db.disconnect()
            return {"success": False, "message": "Course already exists", "course_id": existing["course_id"]}

        query = """
            INSERT INTO courses (course_name, provider_name, institution, country, course_url)
            VALUES (%s, %s, %s, %s, %s)
        """
        course_id = self.db.execute_query(query, (course_name, provider_name, institution, country, course_url))
        self.db.disconnect()

        if course_id:
            return {"success": True, "course_id": course_id}
        return {"success": False, "message": "Failed to add course"}

    def get_course_by_id(self, course_id):
        """Get course details by ID."""
        self.db.connect()
        course = self.db.fetch_one(
            "SELECT * FROM courses WHERE course_id = %s", (course_id,)
        )
        self.db.disconnect()
        return course

    def search_courses(self, keyword):
        """Search courses by name, provider, or institution."""
        self.db.connect()
        query = """
            SELECT * FROM courses
            WHERE course_name LIKE %s
            OR provider_name LIKE %s
            OR institution LIKE %s
        """
        keyword_pattern = f"%{keyword}%"
        results = self.db.fetch_all(query, (keyword_pattern, keyword_pattern, keyword_pattern))
        self.db.disconnect()
        return results

    def update_trust_score(self, course_id, score):
        """Update the trust score of a course."""
        self.db.connect()
        query = "UPDATE courses SET trust_score = %s WHERE course_id = %s"
        result = self.db.execute_query(query, (score, course_id))
        self.db.disconnect()
        return result is not None

    def set_certified(self, course_id, status=True):
        """Mark a course as TrustMyCourse certified."""
        self.db.connect()
        query = "UPDATE courses SET is_certified = %s WHERE course_id = %s"
        result = self.db.execute_query(query, (status, course_id))
        self.db.disconnect()
        return result is not None

    def get_all_courses(self):
        """Get all courses."""
        self.db.connect()
        results = self.db.fetch_all("SELECT * FROM courses ORDER BY trust_score DESC")
        self.db.disconnect()
        return results