from google import genai
from google.genai import types
from database.connection import DatabaseConnection


class AISearch:
    """
    Uses Gemini AI with Google Search Grounding (RAG) to search
    accreditation and legitimacy information about courses.
    """

    def __init__(self):
        self.api_key = "AIzaSyAb6aOtzr4IPvk24IL_PCGW_jQ3GpvsZH4"  # Change this
        self.client  = genai.Client(api_key=self.api_key)
        self.db      = DatabaseConnection()

    def search_course_legitimacy(self, course_name, institution, country):
        """
        Search for course accreditation and legitimacy using Google Search Grounding.
        Returns structured information used to calculate trust score.
        """
        query = f"""
        You are verifying the legitimacy of an online course for students.
        Evaluate the following carefully:

        - Course Name : {course_name}
        - Institution : {institution}
        - Country     : {country}

        Answer each question with YES or NO and a short reason.

        IMPORTANT RULES you must follow:
        - For question 3 (SCAM_WARNING): Answer YES ONLY if the institution or this
          specific course is itself fraudulent or operating illegally.
          Answer NO if the only scam reports found are third-party phishing scams,
          fake certificates, or criminals impersonating the institution.
          A legitimate university being impersonated by scammers does NOT count as a scam warning.
        - For question 2 (COURSE_ACCREDITED): A certificate course on Coursera, edX, or
          similar platforms offered by a recognized university counts as YES if the
          university itself is accredited, even without a separate course-level accreditation body.

        Answer in this exact format:
        ACCREDITED_BY_GOVERNMENT: YES/NO - reason
        COURSE_ACCREDITED: YES/NO - reason
        SCAM_WARNING: YES/NO - reason
        ON_OFFICIAL_SITE: YES/NO - reason
        SUMMARY: one paragraph overall verdict
        """

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=query,
            config=types.GenerateContentConfig(
                tools=[types.Tool(
                    google_search=types.GoogleSearch()
                )]
            )
        )

        response_text = response.text
        self._save_search_log(course_name, query, response_text)
        return self._parse_response(response_text)

    def _parse_response(self, response_text):
        """Parse AI response into structured dictionary."""
        result = {
            "accredited_by_government": False,
            "course_accredited":        False,
            "scam_warning":             False,
            "on_official_site":         False,
            "summary":                  "",
            "raw_response":             response_text
        }

        lines = response_text.upper().split("\n")
        for line in lines:
            if "ACCREDITED_BY_GOVERNMENT:" in line:
                result["accredited_by_government"] = "YES" in line
            elif "COURSE_ACCREDITED:" in line:
                result["course_accredited"] = "YES" in line
            elif "SCAM_WARNING:" in line:
                result["scam_warning"] = "YES" in line
            elif "ON_OFFICIAL_SITE:" in line:
                result["on_official_site"] = "YES" in line

        for line in response_text.split("\n"):
            if "SUMMARY:" in line.upper():
                result["summary"] = line.split(":", 1)[-1].strip()

        return result

    def _save_search_log(self, course_name, query, response):
        """Save AI search result to the database log."""
        self.db.connect()
        self.db.execute_query(
            "INSERT INTO ai_search_log (query_used, ai_response) VALUES (%s, %s)",
            (query, response)
        )
        self.db.disconnect()