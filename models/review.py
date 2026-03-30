from database.connection import DatabaseConnection


class Review:
    """Handles structured course reviews and scam reports."""

    def __init__(self):
        self.db = DatabaseConnection()

    def add_review(self, course_id, user_id, rating, comment,
                   lecturer_quality, content_quality,
                   certificate_recognized, beginner_friendly,
                   is_scam_report=False):
        """Add a structured review for a course."""
        self.db.connect()

        existing = self.db.fetch_one(
            "SELECT review_id FROM reviews WHERE course_id = %s AND user_id = %s",
            (course_id, user_id)
        )
        if existing:
            self.db.disconnect()
            return {"success": False, "message": "You have already reviewed this course"}

        query = """
            INSERT INTO reviews (
                course_id, user_id, rating, comment,
                lecturer_quality, content_quality,
                certificate_recognized, beginner_friendly,
                is_scam_report
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        review_id = self.db.execute_query(query, (
            course_id, user_id, rating, comment,
            lecturer_quality, content_quality,
            certificate_recognized, beginner_friendly,
            is_scam_report
        ))
        self.db.disconnect()

        if review_id:
            return {"success": True, "review_id": review_id}
        return {"success": False, "message": "Failed to add review"}

    def get_reviews_by_course(self, course_id):
        """Get all reviews for a specific course."""
        self.db.connect()
        query = """
            SELECT r.*, u.username
            FROM reviews r
            JOIN users u ON r.user_id = u.user_id
            WHERE r.course_id = %s
            ORDER BY r.created_at DESC
        """
        results = self.db.fetch_all(query, (course_id,))
        self.db.disconnect()
        return results

    def get_average_rating(self, course_id):
        """Get average rating for a course."""
        self.db.connect()
        result = self.db.fetch_one(
            "SELECT AVG(rating) as avg_rating, COUNT(*) as total FROM reviews WHERE course_id = %s",
            (course_id,)
        )
        self.db.disconnect()
        return result

    def get_scam_report_count(self, course_id):
        """Get number of scam reports for a course."""
        self.db.connect()
        result = self.db.fetch_one(
            "SELECT COUNT(*) as scam_count FROM reviews WHERE course_id = %s AND is_scam_report = TRUE",
            (course_id,)
        )
        self.db.disconnect()
        return result["scam_count"] if result else 0