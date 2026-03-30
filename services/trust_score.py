from services.ai_search import AISearch
from models.review import Review
from models.course import Course


# ── Well-known legitimate course platforms (not universities but still trusted) ──
KNOWN_PLATFORMS = [
    "udemy", "coursera", "edx", "linkedin learning", "skillshare",
    "pluralsight", "codecademy", "freecodecamp", "khan academy",
    "futurelearn", "udacity", "datacamp", "brilliant", "alison",
    "openlearn", "swayam", "nptel", "google", "microsoft", "amazon",
    "ibm", "meta", "deeplearning.ai", "simplilearn", "great learning"
]


class TrustScoreCalculator:
    """
    Calculates the trust score for a course.

    Scoring Breakdown (Total: 100):
    - Institution accredited by government/UGC : 35 points
    - Course offered by accredited institution  : 25 points
    - Listed on official education website      : 20 points
    - No scam warning (institution itself)      : -10 penalty
    - Community rating >= 3.5                   : 10 points
    - Known platform bonus (Udemy, Coursera etc): 20 points (if not already scoring on accreditation)
    """

    def __init__(self):
        self.ai_search    = AISearch()
        self.review_model = Review()
        self.course_model = Course()

    def _is_known_platform(self, institution):
        """Check if the institution is a well-known course platform."""
        institution_lower = institution.lower()
        return any(platform in institution_lower for platform in KNOWN_PLATFORMS)

    def calculate(self, course_id, course_name, institution, country):

        score     = 0
        breakdown = {}

        # ── Step 1: AI Search ──
        print(f"Verifying '{course_name}' by '{institution}'...")
        ai_result = self.ai_search.search_course_legitimacy(course_name, institution, country)

        is_known = self._is_known_platform(institution)

        # ── Government / UGC accreditation ──
        if ai_result["accredited_by_government"]:
            score += 35
            breakdown["Institution Accreditation"] = "+35 ✅"
        elif is_known:
            # Known platforms like Udemy are not universities but are legitimate
            score += 20
            breakdown["Institution Accreditation"] = "+20 ✅ (Recognized Platform)"
        else:
            breakdown["Institution Accreditation"] = "+0 ❌"

        # ── Course accreditation ──
        if ai_result["course_accredited"]:
            score += 25
            breakdown["Course Accreditation"] = "+25 ✅"
        elif is_known:
            # Courses on known platforms are generally legitimate even without formal accreditation
            score += 15
            breakdown["Course Accreditation"] = "+15 ✅ (Listed on Recognized Platform)"
        else:
            breakdown["Course Accreditation"] = "+0 ❌"

        # ── Listed on official site ──
        if ai_result["on_official_site"]:
            score += 20
            breakdown["Listed on Official Site"] = "+20 ✅"
        else:
            breakdown["Listed on Official Site"] = "+0 ❌"

        # ── Scam warning — only if institution ITSELF is fraudulent ──
        if ai_result["scam_warning"]:
            score -= 10
            breakdown["Scam Warning (Institution)"] = "-10 ⚠️"
        else:
            breakdown["Scam Warning (Institution)"] = "None ✅"

        # ── Community Reviews ──
        rating_data = self.review_model.get_average_rating(course_id)
        avg_rating  = float(rating_data["avg_rating"]) if rating_data and rating_data["avg_rating"] else 0
        total       = int(rating_data["total"]) if rating_data else 0

        if avg_rating >= 3.5:
            score += 10
            breakdown["Community Rating"] = f"+10 ✅ (avg {avg_rating:.1f}/5 from {total} review(s))"
        elif total == 0:
            breakdown["Community Rating"] = "No reviews yet"
        else:
            breakdown["Community Rating"] = f"+0 ❌ (avg {avg_rating:.1f}/5 from {total} review(s))"

        # ── DB Scam Reports ──
        scam_count = self.review_model.get_scam_report_count(course_id)
        if scam_count == 0:
            breakdown["User Scam Reports"] = "None reported ✅"
        else:
            score -= (scam_count * 5)
            breakdown["User Scam Reports"] = f"-{scam_count * 5} ⚠️ ({scam_count} report(s))"

        # ── Clamp 0–100 ──
        score = max(0, min(100, score))

        # ── Save to DB ──
        self.course_model.update_trust_score(course_id, score)

        return {
            "course_id":   course_id,
            "trust_score": score,
            "breakdown":   breakdown,
            "ai_summary":  ai_result.get("summary", ""),
            "label":       self._get_label(score)
        }

    def _get_label(self, score):
        if score >= 80:
            return "✅ Highly Trusted"
        elif score >= 65:
            return "🟡 Trusted"
        elif score >= 50:
            return "🟠 Moderately Trusted"
        elif score >= 35:
            return "⚠️ Low Trust - Verify Before Enrolling"
        else:
            return "🚫 Not Recommended - Possible Scam"