from database.connection import DatabaseConnection


class Certification:
    """Handles TrustMyCourse certification requests."""

    def __init__(self):
        self.db = DatabaseConnection()

    def submit_request(self, course_id, provider_user_id):
        """Submit a certification request for a course."""
        self.db.connect()

        # Check if a pending request already exists
        existing = self.db.fetch_one(
            """SELECT request_id FROM certification_requests
               WHERE course_id = %s AND status = 'pending'""",
            (course_id,)
        )
        if existing:
            self.db.disconnect()
            return {"success": False, "message": "A pending request already exists for this course"}

        query = """
            INSERT INTO certification_requests (course_id, provider_user_id)
            VALUES (%s, %s)
        """
        request_id = self.db.execute_query(query, (course_id, provider_user_id))
        self.db.disconnect()

        if request_id:
            return {"success": True, "request_id": request_id, "message": "Certification request submitted"}
        return {"success": False, "message": "Failed to submit request"}

    def get_all_requests(self):
        """Get all certification requests (for admin)."""
        self.db.connect()
        query = """
            SELECT cr.*, c.course_name, c.provider_name, u.username, u.email
            FROM certification_requests cr
            JOIN courses c ON cr.course_id = c.course_id
            JOIN users u ON cr.provider_user_id = u.user_id
            ORDER BY cr.requested_at DESC
        """
        results = self.db.fetch_all(query)
        self.db.disconnect()
        return results

    def get_pending_requests(self):
        """Get only pending certification requests."""
        self.db.connect()
        query = """
            SELECT cr.*, c.course_name, u.username
            FROM certification_requests cr
            JOIN courses c ON cr.course_id = c.course_id
            JOIN users u ON cr.provider_user_id = u.user_id
            WHERE cr.status = 'pending'
        """
        results = self.db.fetch_all(query)
        self.db.disconnect()
        return results

    def approve_request(self, request_id, course_id):
        """Approve a certification request."""
        self.db.connect()
        query = """
            UPDATE certification_requests
            SET status = 'approved', reviewed_at = NOW()
            WHERE request_id = %s
        """
        self.db.execute_query(query, (request_id,))

        # Also mark the course as certified
        self.db.execute_query(
            "UPDATE courses SET is_certified = TRUE WHERE course_id = %s",
            (course_id,)
        )
        self.db.disconnect()
        return {"success": True, "message": "Request approved and course certified"}

    def reject_request(self, request_id):
        """Reject a certification request."""
        self.db.connect()
        query = """
            UPDATE certification_requests
            SET status = 'rejected', reviewed_at = NOW()
            WHERE request_id = %s
        """
        result = self.db.execute_query(query, (request_id,))
        self.db.disconnect()
        return {"success": True, "message": "Request rejected"}