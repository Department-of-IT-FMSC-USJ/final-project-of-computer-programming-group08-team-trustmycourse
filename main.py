import streamlit as st
from google import genai
from google.genai import types
from models.user import User
from models.course import Course
from models.review import Review
from models.discussion import Discussion
from models.certification import Certification
from services.trust_score import TrustScoreCalculator
from services.ai_search import AISearch
import pathlib

# ─── Page Configuration ───────────────────────────────────────────────────────
st.set_page_config(page_title="TrustMyCourse", layout="wide", page_icon=None)

# ─── Load External CSS ────────────────────────────────────────────────────────
def load_css():
    css_path = pathlib.Path("style.css")
    if css_path.exists():
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ─── Session State ────────────────────────────────────────────────────────────
if "logged_in"       not in st.session_state: st.session_state.logged_in       = False
if "user"            not in st.session_state: st.session_state.user            = None
if "page"            not in st.session_state: st.session_state.page            = "home"
if "current_course"  not in st.session_state: st.session_state.current_course  = None
if "score_result"    not in st.session_state: st.session_state.score_result    = None
if "community_links" not in st.session_state: st.session_state.community_links = None

# ─── Model Instances ──────────────────────────────────────────────────────────
user_model       = User()
course_model     = Course()
review_model     = Review()
discussion_model = Discussion()
cert_model       = Certification()
trust_calculator = TrustScoreCalculator()
ai_search        = AISearch()

# ─── Helper ───────────────────────────────────────────────────────────────────
def go_to(page):
    st.session_state.page = page
    st.rerun()

def section_header(title, subtitle=""):
    st.markdown(f"""
        <div style='margin: 24px 0 12px 0;'>
            <h3 style='color:#e8f5e9; margin:0; font-size:17px; font-weight:600;
                       letter-spacing:0.3px; border-left:3px solid #4caf50;
                       padding-left:10px;'>{title}</h3>
            {"<p style='color:#a5c8a8; font-size:12px; margin:4px 0 0 13px;'>" + subtitle + "</p>" if subtitle else ""}
        </div>
    """, unsafe_allow_html=True)


# ─── Page: Login / Register ───────────────────────────────────────────────────
def show_auth_page():
    # ── Inject CSS for b.well-style split layout ──────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
 
    /* Hide Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
 
    /* Full-screen wrapper */
    .auth-wrapper {
        display: flex;
        min-height: 100vh;
        font-family: 'Poppins', sans-serif;
        background: #f4f6fb;
    }
 
    /* ── LEFT PANEL — image / brand ── */
    .auth-left {
        flex: 1.1;
        background: linear-gradient(135deg, #1a2a6c 0%, #2d4a9e 60%, #3a5bbf 100%);
        position: relative;
        overflow: hidden;
        display: flex;
        align-items: flex-end;
        padding: 40px;
    }
    .auth-left::before {
        content: '';
        position: absolute;
        inset: 0;
        height: 100%;
        background: url('data:image/jpeg;base64,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')
                    center/cover no-repeat;
        opacity: 0.22;
    }
    .auth-left-content {
        position: relative;
        z-index: 1;
        color: #fff;
    }
    .auth-left-tagline {
        font-size: 28px;
        font-weight: 700;
        line-height: 1.3;
        margin-bottom: 10px;
    }
    .auth-left-sub {
        font-size: 15px;
        font-weight: 300;
        opacity: 0.8;
    }
 
    /* ── RIGHT PANEL — form ── */
    .auth-right {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #ffffff;
        padding: 48px 40px;
    }
    .auth-card {
        width: 100%;
        max-width: 400px;
    }
 
    /* Logo */
    .auth-logo {
        font-size: 38px;
        font-weight: 800;
        color: #1a2a6c;
        letter-spacing: -1px;
        text-align: center;
        margin-bottom: 4px;
    }
    .auth-logo span { color: #4caf50; }
    .auth-tagline {
        text-align: center;
        font-size: 14px;
        color: #6b7a99;
        font-weight: 400;
        margin-bottom: 32px;
    }
 
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 2px solid #e8ecf4;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        flex: 1;
        justify-content: center;
        font-family: 'Poppins', sans-serif;
        font-size: 14px;
        font-weight: 500;
        color: #6b7a99;
        padding: 10px 0;
        border-bottom: 2px solid transparent;
        margin-bottom: -2px;
        background: transparent;
    }
    .stTabs [aria-selected="true"] {
        color: #1a2a6c !important;
        border-bottom: 2px solid #1a2a6c !important;
        font-weight: 600;
    }
 
    /* Inputs */
    .stTextInput > label {
        font-family: 'Poppins', sans-serif;
        font-size: 13px;
        font-weight: 500;
        color: #3a3f5c;
        margin-bottom: 4px;
    }
    .stTextInput > div > div > input {
        font-family: 'Poppins', sans-serif;
        font-size: 14px;
        border: 1.5px solid #dde3f0;
        border-radius: 8px;
        padding: 10px 14px;
        background: #f9fafd;
        color: #1a2a6c;
        transition: border-color 0.2s;
    }
    .stTextInput > div > div > input:focus {
        border-color: #1a2a6c;
        background: #fff;
        box-shadow: 0 0 0 3px rgba(26,42,108,0.08);
    }
 
    /* Selectbox */
    .stSelectbox > label {
        font-family: 'Poppins', sans-serif;
        font-size: 13px;
        font-weight: 500;
        color: #3a3f5c;
    }
 
    /* Primary button */
    .stButton > button {
        font-family: 'Poppins', sans-serif;
        font-size: 15px;
        font-weight: 600;
        background: #1a2a6c;
        color: #ffffff;
        border: none;
        border-radius: 50px;
        padding: 12px 0;
        width: 100%;
        cursor: pointer;
        transition: background 0.2s, transform 0.1s, box-shadow 0.2s;
        box-shadow: 0 4px 16px rgba(26,42,108,0.18);
    }
    .stButton > button:hover {
        background: #243580;
        box-shadow: 0 6px 20px rgba(26,42,108,0.28);
        transform: translateY(-1px);
    }
    .stButton > button:active { transform: translateY(0); }
 
    /* Helper links row */
    .auth-helpers {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 6px 0 16px 0;
        font-size: 12.5px;
    }
    .auth-helpers a {
        color: #1a2a6c;
        text-decoration: none;
        font-weight: 500;
    }
    .auth-helpers a:hover { text-decoration: underline; }
 
    /* Sign-up nudge */
    .auth-signup-nudge {
        text-align: center;
        font-size: 13px;
        color: #6b7a99;
        margin-top: 20px;
    }
    .auth-signup-nudge a {
        color: #1a2a6c;
        font-weight: 600;
        text-decoration: none;
    }
 
    /* Info note */
    .auth-note {
        font-size: 11.5px;
        color: #9aa3bc;
        margin-bottom: 12px;
        line-height: 1.5;
    }
 
    /* Footer */
    .auth-footer {
        text-align: center;
        font-size: 11px;
        color: #b0b8d0;
        margin-top: 28px;
        line-height: 1.7;
    }
    .auth-footer a { color: #6b7a99; text-decoration: none; }
    .auth-footer a:hover { text-decoration: underline; }
 
    /* Checkbox */
    .stCheckbox > label {
        font-family: 'Poppins', sans-serif;
        font-size: 13px;
        color: #3a3f5c;
    }
    </style>
    """, unsafe_allow_html=True)
 
    # ── Left panel (pure HTML — decorative) ───────────────────────────────────
    # ── Right panel rendered via Streamlit columns ─────────────────────────────
    col_l, col_r = st.columns([1.1, 1])
 
    with col_l:
        st.markdown("""
        <div class="auth-left">
            <div class="auth-left-content">
                <div class="auth-left-tagline">Verify every course.<br>Trust every credential.</div>
                <div class="auth-left-sub">TrustMyCourse — the platform educators and<br>students rely on for transparent verification.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
 
    with col_r:
        st.markdown('<div class="auth-right"><div class="auth-card">', unsafe_allow_html=True)
 
        # Logo & tagline
        st.markdown("""
        <div class="auth-logo">Trust<span>My</span>Course</div>
        <div class="auth-tagline">Course Verification Platform</div>
        """, unsafe_allow_html=True)
 
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])
 
        # ── Sign In ──
        with tab1:
            email    = st.text_input("Email Address", placeholder="Enter your email", key="login_email")
            password = st.text_input("Password", type="password", placeholder="Enter password", key="login_password")
 
            st.markdown("""
            <div class="auth-helpers">
                <label style="display:flex;align-items:center;gap:6px;cursor:pointer;">
                    <input type="checkbox" style="accent-color:#1a2a6c;width:14px;height:14px;">
                    Remember me
                </label>
                <a href="#">Forgot password?</a>
            </div>
            """, unsafe_allow_html=True)
 
            if st.button("Sign In", use_container_width=True, key="btn_signin"):
                result = user_model.login(email, password)
                if result["success"]:
                    st.session_state.logged_in = True
                    st.session_state.user = result["user"]
                    go_to("home")
                else:
                    st.error(result["message"])
 
            st.markdown("""
            <div class="auth-signup-nudge">
                Don't have an account? <a href="#">Sign up</a>
            </div>
            """, unsafe_allow_html=True)
 
        # ── Create Account ──
        with tab2:
            st.markdown('<p class="auth-note">Institution is optional — you may still be exploring your options.</p>',
                        unsafe_allow_html=True)
 
            username    = st.text_input("Username", key="reg_username")
            email       = st.text_input("Email Address", key="reg_email")
            password    = st.text_input("Password", type="password", key="reg_password")
            country     = st.text_input("Country", key="reg_country")
            institution = st.text_input("Institution / University (optional)", key="reg_institution")
            role        = st.selectbox("Account Type", ["student", "course_provider"])
 
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
 
            if st.button("Create Account", use_container_width=True, key="btn_register"):
                if not country.strip():
                    st.error("Country is required.")
                else:
                    result = user_model.register(username, email, password, role, institution, country)
                    if result["success"]:
                        st.success("Account created! Please sign in.")
                    else:
                        st.error(result["message"])
 
        # Footer
        st.markdown("""
        <div class="auth-footer">
            By creating an account or logging in, you agree to our
            <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>.<br>
            <a href="#">English (EN)</a> &nbsp;·&nbsp; <a href="#">Get Support</a>
        </div>
        """, unsafe_allow_html=True)
 
        st.markdown('</div></div>', unsafe_allow_html=True)

# ─── Page: Home / Search ──────────────────────────────────────────────────────
def show_home_page():
    st.markdown(f"""
        <div style='margin-bottom:8px;'>
            <h2 style='color:#e8f5e9; margin:0; font-size:22px;'>Course Verification</h2>
            <p style='color:#a5c8a8; font-size:13px; margin:4px 0 0 0;'>
                Welcome back, {st.session_state.user['username']}
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.divider()

    with st.form("search_form"):
        col1, col2 = st.columns(2)
        with col1:
            course_name = st.text_input("Course Name")
            institution = st.text_input("Institution / Provider")
        with col2:
            country    = st.text_input("Country")
            course_url = st.text_input("Course URL (optional)")
        submitted = st.form_submit_button("Search & Verify", use_container_width=True)

    if submitted and course_name and institution:
        with st.spinner("Verifying course... This may take a moment."):
            result    = course_model.add_course(course_name, institution, institution, country, course_url)
            course_id = result.get("course_id")
            if not course_id:
                courses = course_model.search_courses(course_name)
                if courses:
                    course_id = courses[0]["course_id"]
            score_result = trust_calculator.calculate(course_id, course_name, institution, country)

        st.session_state.current_course = {
            "course_id": course_id, "course_name": course_name,
            "institution": institution, "country": country, "course_url": course_url,
        }
        st.session_state.score_result    = score_result
        st.session_state.community_links = None

    if st.session_state.current_course and st.session_state.score_result:
        c            = st.session_state.current_course
        score_result = st.session_state.score_result
        course_id    = c["course_id"]

        st.divider()
        st.markdown(f"""
            <h3 style='color:#e8f5e9; font-size:18px; margin:0 0 16px 0;'>
                Results — {c['course_name']}
            </h3>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 2])
        with col1:
            score = score_result["trust_score"]
            if score >= 80:
                color = "#4caf50"; bg = "#0f2a10"; border = "#4caf50"; status = "Highly Trusted"
            elif score >= 65:
                color = "#fdd835"; bg = "#2a2200"; border = "#fdd835"; status = "Trusted"
            elif score >= 50:
                color = "#ff9800"; bg = "#2a1800"; border = "#ff9800"; status = "Moderately Trusted"
            elif score >= 35:
                color = "#ef5350"; bg = "#2a0e0e"; border = "#ef5350"; status = "Low Trust"
            else:
                color = "#b71c1c"; bg = "#1a0808"; border = "#b71c1c"; status = "Not Recommended"

            certified = course_model.get_course_by_id(course_id)
            badge     = "TrustMyCourse Certified" if certified and certified["is_certified"] else ""

            st.markdown(f"""
                <div style='
                    text-align:center; padding:32px 20px;
                    border-radius:12px; background:{bg};
                    border:2px solid {border};
                    box-shadow:0 0 20px {border}33;
                '>
                    <div style='font-size:72px; font-weight:800; color:{color};
                                line-height:1; font-family:Inter,sans-serif;
                                text-shadow:0 0 16px {border}88;'>{score}</div>
                    <div style='color:#a5c8a8; font-size:13px; margin:8px 0 4px 0;'>
                        Trust Score / 100
                    </div>
                    <div style='color:{color}; font-size:14px; font-weight:600;
                                margin:8px 0; letter-spacing:0.5px;'>{status}</div>
                    {"<div style='color:#fdd835; font-size:12px; margin-top:10px; font-weight:500;'>" + badge + "</div>" if badge else ""}
                </div>
            """, unsafe_allow_html=True)

        with col2:
            section_header("Score Breakdown")
            for factor, points in score_result["breakdown"].items():
                st.markdown(f"""
                    <div style='display:flex; justify-content:space-between;
                                padding:8px 12px; margin:4px 0;
                                background:#132215; border-radius:6px;
                                border:1px solid #1e3a20;'>
                        <span style='color:#e8f5e9; font-size:13px;'>{factor}</span>
                        <span style='color:#4caf50; font-size:13px; font-weight:600;'>{points}</span>
                    </div>
                """, unsafe_allow_html=True)

            if score_result.get("ai_summary"):
                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                st.markdown(f"""
                    <div style='background:#132215; border:1px solid #1e3a20;
                                border-left:3px solid #4caf50; border-radius:8px;
                                padding:12px 16px; font-size:13px; color:#a5c8a8;'>
                        <span style='color:#4caf50; font-weight:600; font-size:12px;
                                     letter-spacing:0.5px;'>AI SUMMARY</span><br>
                        <span style='color:#e8f5e9;'>{score_result['ai_summary']}</span>
                    </div>
                """, unsafe_allow_html=True)

        st.divider()
        show_community_links(c["course_name"], c["institution"])
        st.divider()
        show_reviews_section(course_id)
        st.divider()
        show_discussion_board(course_id)


# ─── Community Links ──────────────────────────────────────────────────────────
BLOCKED_DOMAINS = [
    "onlyfans.com", "reddit.com/u/", "reddit.com/user/",
    "twitter.com", "x.com", "tiktok.com", "instagram.com",
    "pornhub.com", "xvideos.com"
]

def is_safe_link(url):
    url_lower = url.lower()
    return not any(b in url_lower for b in BLOCKED_DOMAINS)

def is_working_link(url):
    import requests
    try:
        r = requests.head(url, timeout=5, allow_redirects=True)
        return r.status_code < 400
    except:
        return False

def show_community_links(course_name, institution):
    section_header("Community Discussions",
                   "External links where students discuss this course — verified and filtered for safety")

    if st.session_state.community_links is None:
        if st.button("Find Community Links", key="community_search_btn"):
            with st.spinner("Searching and verifying links..."):
                query = f"""
                Find online community discussions where students talk about the course
                "{course_name}" offered by "{institution}".
                Only return links from: Reddit subreddits (r/), Quora, Stack Overflow,
                official course forums, or educational sites.
                Do NOT return Reddit user profiles, social media profiles, or adult content.

                Return results ONLY in this exact format, one per line:
                PLATFORM: [name] | LINK: [full url] | DESCRIPTION: [one sentence]
                Maximum 6 results.
                """
                client   = genai.Client(api_key=ai_search.api_key)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=query,
                    config=types.GenerateContentConfig(
                        tools=[types.Tool(google_search=types.GoogleSearch())]
                    )
                )
                safe_links = []
                for line in response.text.split("\n"):
                    if "PLATFORM:" in line and "LINK:" in line and "DESCRIPTION:" in line:
                        try:
                            platform    = line.split("PLATFORM:")[1].split("|")[0].strip()
                            url         = line.split("LINK:")[1].split("|")[0].strip()
                            description = line.split("DESCRIPTION:")[1].strip()
                            if is_safe_link(url) and is_working_link(url):
                                safe_links.append({"platform": platform, "url": url, "description": description})
                        except:
                            continue
                st.session_state.community_links = safe_links
                st.rerun()
    else:
        links = st.session_state.community_links
        if not links:
            st.markdown("""
                <div style='background:#132215; border:1px solid #1e3a20; border-radius:8px;
                            padding:14px 16px; color:#a5c8a8; font-size:13px;'>
                    No verified community links found for this course.
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style='color:#4caf50; font-size:12px; font-weight:600;
                            letter-spacing:0.5px; margin-bottom:10px;'>
                    {len(links)} VERIFIED LINK(S) FOUND
                </div>
            """, unsafe_allow_html=True)
            for link in links:
                st.markdown(f"""
                    <div style='background:#132215; border:1px solid #1e3a20;
                                border-radius:8px; padding:14px 16px; margin:6px 0;'>
                        <div style='color:#e8f5e9; font-size:13px; font-weight:600;
                                    margin-bottom:4px;'>{link['platform']}</div>
                        <a href="{link['url']}" target="_blank"
                           style='color:#4caf50; font-size:12px;
                                  text-decoration:none;'>{link['url']}</a>
                        <div style='color:#a5c8a8; font-size:12px;
                                    margin-top:6px;'>{link['description']}</div>
                    </div>
                """, unsafe_allow_html=True)

        if st.button("Search Again", key="community_refresh_btn"):
            st.session_state.community_links = None
            st.rerun()


# ─── Reviews ─────────────────────────────────────────────────────────────────
def show_reviews_section(course_id):
    section_header("Student Reviews", "Structured feedback from students who have taken this course")

    reviews = review_model.get_reviews_by_course(course_id)
    if reviews:
        for r in reviews:
            scam_tag = "<span style='color:#ef5350; font-size:11px; font-weight:600; letter-spacing:0.5px;'>SCAM REPORT</span>" if r['is_scam_report'] else ""
            cert_val = "Yes" if r.get('certificate_recognized') else "No"
            bfr_val  = "Yes" if r.get('beginner_friendly') else "No"
            st.markdown(f"""
                <div style='background:#132215; border:1px solid #1e3a20;
                            border-radius:10px; padding:16px 20px; margin:8px 0;'>
                    <div style='display:flex; justify-content:space-between; margin-bottom:10px;'>
                        <span style='color:#e8f5e9; font-size:14px; font-weight:600;'>{r['username']}</span>
                        {scam_tag}
                    </div>
                    <div style='display:flex; gap:20px; margin-bottom:10px; flex-wrap:wrap;'>
                        <span style='color:#a5c8a8; font-size:12px;'>Overall: <b style="color:#fdd835">{"★" * r['rating']}{"☆" * (5 - r['rating'])}</b></span>
                        <span style='color:#a5c8a8; font-size:12px;'>Lecturers: <b style="color:#fdd835">{"★" * r.get('lecturer_quality', 0)}{"☆" * (5 - r.get('lecturer_quality', 0))}</b></span>
                        <span style='color:#a5c8a8; font-size:12px;'>Content: <b style="color:#fdd835">{"★" * r.get('content_quality', 0)}{"☆" * (5 - r.get('content_quality', 0))}</b></span>
                        <span style='color:#a5c8a8; font-size:12px;'>Certificate Recognized: <b style="color:#e8f5e9">{cert_val}</b></span>
                        <span style='color:#a5c8a8; font-size:12px;'>Beginner Friendly: <b style="color:#e8f5e9">{bfr_val}</b></span>
                    </div>
                    <div style='color:#e8f5e9; font-size:13px; line-height:1.6;'>{r['comment']}</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style='background:#132215; border:1px solid #1e3a20; border-radius:8px;
                        padding:14px 16px; color:#a5c8a8; font-size:13px;'>
                No reviews yet. Be the first to share your experience.
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    section_header("Write a Review", "Help other students make a safe and informed decision")

    # ── Star rating session state ──
    for key, default in [("rating", 3), ("lecturer_quality", 3), ("content_quality", 3)]:
        if f"review_{key}" not in st.session_state:
            st.session_state[f"review_{key}"] = default

    def star_row(label, key):
        current = st.session_state[f"review_{key}"]
        st.markdown(f"<p style='color:#a5c8a8; font-size:13px; margin:8px 0 4px 0; font-weight:500;'>{label}</p>", unsafe_allow_html=True)
        cols = st.columns(5)
        for i in range(1, 6):
            with cols[i - 1]:
                star_color = "#fdd835" if i <= current else "#1e3a20"
                if st.button(
                    "★",
                    key=f"{key}_star_{i}",
                    help=f"{i} star{'s' if i > 1 else ''}",
                ):
                    st.session_state[f"review_{key}"] = i
                    st.rerun()
                st.markdown(
                    f"<style>div[data-testid='stButton'] button[title='{i} star{'s' if i > 1 else ''}'] "
                    f"{{background:transparent !important; color:{star_color} !important; "
                    f"font-size:28px !important; border:none !important; "
                    f"padding:0 !important; min-height:0 !important;}}</style>",
                    unsafe_allow_html=True
                )

    star_row("Overall Rating", "rating")
    star_row("Lecturer Quality", "lecturer_quality")
    star_row("Content Quality", "content_quality")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    with st.form("review_form"):
        col1, col2 = st.columns(2)
        with col1:
            certificate_recognized = st.radio(
                "Is the certificate recognized by employers?", ["Yes", "No"], horizontal=True
            )
        with col2:
            beginner_friendly = st.radio(
                "Is this course beginner friendly?", ["Yes", "No"], horizontal=True
            )
        is_scam = st.checkbox("Report this course as a scam")
        comment = st.text_area(
            "Your Review",
            placeholder="Share your experience — lecturers, content quality, job relevance..."
        )
        if st.form_submit_button("Submit Review", use_container_width=True):
            rev_result = review_model.add_review(
                course_id, st.session_state.user["user_id"],
                st.session_state["review_rating"],
                comment,
                st.session_state["review_lecturer_quality"],
                st.session_state["review_content_quality"],
                certificate_recognized == "Yes",
                beginner_friendly == "Yes",
                is_scam
            )
            if rev_result["success"]:
                st.session_state["review_rating"] = 3
                st.session_state["review_lecturer_quality"] = 3
                st.session_state["review_content_quality"] = 3
                st.success("Review submitted. Thank you.")
            else:
                st.error(rev_result["message"])


# ─── Discussion Board ─────────────────────────────────────────────────────────
def show_discussion_board(course_id):
    section_header("Discussion Board",
                   "Ask questions about this course — other students will answer")

    with st.form("question_form", clear_on_submit=True):
        question_text = st.text_input(
            "Your Question",
            placeholder="e.g. Is this course recognized in Sri Lanka?"
        )
        if st.form_submit_button("Post Question", use_container_width=True):
            if question_text.strip():
                result = discussion_model.post_question(
                    course_id, st.session_state.user["user_id"], question_text
                )
                if result["success"]:
                    st.success("Question posted.")
                else:
                    st.error("Failed to post question.")

    questions = discussion_model.get_questions(course_id)
    if not questions:
        st.markdown("""
            <div style='background:#132215; border:1px solid #1e3a20; border-radius:8px;
                        padding:14px 16px; color:#a5c8a8; font-size:13px;'>
                No questions yet. Be the first to ask.
            </div>
        """, unsafe_allow_html=True)
    else:
        for q in questions:
            st.markdown(f"""
                <div style='background:#0f2218; border:1px solid #1e3a20;
                            border-left:3px solid #4caf50;
                            border-radius:8px; padding:14px 16px; margin:10px 0 4px 0;'>
                    <div style='display:flex; justify-content:space-between; margin-bottom:6px;'>
                        <span style='color:#4caf50; font-size:12px; font-weight:600;'>{q['username']}</span>
                        <span style='color:#a5c8a8; font-size:11px;'>{str(q['created_at'])[:16]}</span>
                    </div>
                    <div style='color:#e8f5e9; font-size:13px;'>{q['message']}</div>
                </div>
            """, unsafe_allow_html=True)

            replies = discussion_model.get_replies(q["discussion_id"])
            for reply in replies:
                st.markdown(f"""
                    <div style='background:#132215; border:1px solid #1e3a20;
                                border-radius:8px; padding:12px 16px;
                                margin:3px 0 3px 28px;'>
                        <div style='display:flex; justify-content:space-between; margin-bottom:4px;'>
                            <span style='color:#81c784; font-size:12px; font-weight:600;'>{reply['username']}</span>
                            <span style='color:#a5c8a8; font-size:11px;'>{str(reply['created_at'])[:16]}</span>
                        </div>
                        <div style='color:#e8f5e9; font-size:13px;'>{reply['message']}</div>
                    </div>
                """, unsafe_allow_html=True)

            with st.form(f"reply_form_{q['discussion_id']}", clear_on_submit=True):
                reply_text = st.text_input("Reply", key=f"reply_input_{q['discussion_id']}")
                if st.form_submit_button("Post Reply"):
                    if reply_text.strip():
                        result = discussion_model.post_reply(
                            course_id, st.session_state.user["user_id"],
                            q["discussion_id"], reply_text
                        )
                        if result["success"]:
                            st.success("Reply posted.")
                        else:
                            st.error("Failed to post reply.")


# ─── Page: Certification ──────────────────────────────────────────────────────
def show_certification_page():
    st.markdown("""
        <h2 style='color:#e8f5e9; font-size:22px; margin-bottom:4px;'>
            Certification Request
        </h2>
        <p style='color:#a5c8a8; font-size:13px; margin:0 0 20px 0;'>
            Submit your course for TrustMyCourse verification and earn a certified badge.
        </p>
    """, unsafe_allow_html=True)
    st.divider()

    with st.form("cert_form"):
        course_id = st.number_input("Course ID", min_value=1, step=1)
        st.markdown("<p style='color:#a5c8a8; font-size:12px;'>Search for your course on the home page first to get its Course ID.</p>", unsafe_allow_html=True)
        if st.form_submit_button("Submit Request", use_container_width=True):
            result = cert_model.submit_request(course_id, st.session_state.user["user_id"])
            if result["success"]:
                st.success(result["message"])
            else:
                st.error(result["message"])


# ─── Page: Admin Panel ────────────────────────────────────────────────────────
def show_admin_page():
    if st.session_state.user["role"] != "admin":
        st.error("Access denied.")
        return

    st.markdown("""
        <h2 style='color:#e8f5e9; font-size:22px; margin-bottom:4px;'>Admin Panel</h2>
        <p style='color:#a5c8a8; font-size:13px; margin:0 0 20px 0;'>
            Manage certification requests and platform activity.
        </p>
    """, unsafe_allow_html=True)
    st.divider()

    section_header("Pending Certification Requests")
    requests = cert_model.get_pending_requests()
    if requests:
        for req in requests:
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.markdown(f"""
                    <div style='background:#132215; border:1px solid #1e3a20;
                                border-radius:8px; padding:12px 16px;'>
                        <div style='color:#e8f5e9; font-size:13px; font-weight:600;'>{req['course_name']}</div>
                        <div style='color:#a5c8a8; font-size:12px; margin-top:2px;'>Submitted by {req['username']}</div>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("Approve", key=f"approve_{req['request_id']}"):
                    cert_model.approve_request(req["request_id"], req["course_id"])
                    st.success("Approved.")
                    st.rerun()
            with col3:
                if st.button("Reject", key=f"reject_{req['request_id']}"):
                    cert_model.reject_request(req["request_id"])
                    st.warning("Rejected.")
                    st.rerun()
    else:
        st.markdown("""
            <div style='background:#132215; border:1px solid #1e3a20; border-radius:8px;
                        padding:14px 16px; color:#a5c8a8; font-size:13px;'>
                No pending certification requests.
            </div>
        """, unsafe_allow_html=True)


# ─── Sidebar ──────────────────────────────────────────────────────────────────
def show_sidebar():
    with st.sidebar:
        st.markdown("""
            <div style='padding:20px 0 16px 0;'>
                <div style='color:#4caf50; font-size:20px; font-weight:700;
                            letter-spacing:0.5px;'>TrustMyCourse</div>
                <div style='color:#a5c8a8; font-size:11px; margin-top:2px;'>
                    Course Verification Platform
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.divider()

        st.markdown(f"""
            <div style='background:#132215; border:1px solid #1e3a20;
                        border-radius:8px; padding:10px 14px; margin-bottom:16px;'>
                <div style='color:#e8f5e9; font-size:13px; font-weight:600;'>
                    {st.session_state.user['username']}
                </div>
                <div style='color:#a5c8a8; font-size:11px; margin-top:2px; text-transform:capitalize;'>
                    {st.session_state.user['role']}
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("Home", use_container_width=True):
            go_to("home")
        if st.session_state.user["role"] == "course_provider":
            if st.button("Get Certified", use_container_width=True):
                go_to("certification")
        if st.session_state.user["role"] == "admin":
            if st.button("Admin Panel", use_container_width=True):
                go_to("admin")

        st.divider()

        if st.button("Sign Out", use_container_width=True):
            st.session_state.logged_in       = False
            st.session_state.user            = None
            st.session_state.current_course  = None
            st.session_state.score_result    = None
            st.session_state.community_links = None
            go_to("home")


# ─── Router ───────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    show_auth_page()
else:
    show_sidebar()
    page = st.session_state.page
    if page == "home":
        show_home_page()
    elif page == "certification":
        show_certification_page()
    elif page == "admin":
        show_admin_page()