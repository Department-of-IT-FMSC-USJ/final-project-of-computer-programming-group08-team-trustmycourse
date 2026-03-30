from database.connection import DatabaseConnection


class Discussion:
    """Handles course discussion board — questions and replies per course."""

    def __init__(self):
        self.db = DatabaseConnection()

    def post_question(self, course_id, user_id, message):
        """Post a new question on a course discussion board."""
        self.db.connect()
        query = """
            INSERT INTO course_discussions (course_id, user_id, parent_id, message)
            VALUES (%s, %s, NULL, %s)
        """
        discussion_id = self.db.execute_query(query, (course_id, user_id, message))
        self.db.disconnect()

        if discussion_id:
            return {"success": True, "discussion_id": discussion_id}
        return {"success": False, "message": "Failed to post question"}

    def post_reply(self, course_id, user_id, parent_id, message):
        """Post a reply to an existing question."""
        self.db.connect()
        query = """
            INSERT INTO course_discussions (course_id, user_id, parent_id, message)
            VALUES (%s, %s, %s, %s)
        """
        discussion_id = self.db.execute_query(query, (course_id, user_id, parent_id, message))
        self.db.disconnect()

        if discussion_id:
            return {"success": True, "discussion_id": discussion_id}
        return {"success": False, "message": "Failed to post reply"}

    def get_questions(self, course_id):
        """Get all top-level questions for a course."""
        self.db.connect()
        query = """
            SELECT d.*, u.username
            FROM course_discussions d
            JOIN users u ON d.user_id = u.user_id
            WHERE d.course_id = %s AND d.parent_id IS NULL
            ORDER BY d.created_at DESC
        """
        results = self.db.fetch_all(query, (course_id,))
        self.db.disconnect()
        return results

    def get_replies(self, parent_id):
        """Get all replies for a specific question."""
        self.db.connect()
        query = """
            SELECT d.*, u.username
            FROM course_discussions d
            JOIN users u ON d.user_id = u.user_id
            WHERE d.parent_id = %s
            ORDER BY d.created_at ASC
        """
        results = self.db.fetch_all(query, (parent_id,))
        self.db.disconnect()
        return results