import feedparser
import gspread
import re
from urllib.parse import urlsplit, urlunsplit
from newspaper import Article
import os
from dotenv import load_dotenv
from groq import Groq

# ----------------------------
# Groq API
# ----------------------------
load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)
# ----------------------------
# Google Sheets Connection
# ----------------------------
gc = gspread.service_account(filename="google_creds.json")
sh = gc.open("Prachi_Explore_News_Beta_Staging").sheet1


# ----------------------------
# RSS Feeds
# ----------------------------
rss_urls = [
    "https://indianexpress.com/section/education/feed/",
    "https://www.educationworld.in/feed/",
    "https://www.livemint.com/rss/education",
    "https://www.indiatoday.in/rss/1206578",
    "https://www.thehindu.com/education/feeder/default.rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/Education.xml",
    "https://www.careerindia.com/rss/feeds/education-news-fb.xml",
    "https://www.hindustantimes.com/feeds/rss/education/news/rssfeed.xml",
    "https://www.edtechreview.in/feed/"
]


# ----------------------------
# Normalize URL
# ----------------------------
def normalize_url(url):
    parts = urlsplit(url)
    return urlunsplit((
        parts.scheme,
        parts.netloc,
        parts.path.rstrip("/"),
        "",
        ""
    ))


# ----------------------------
# Download Article
# ----------------------------
def get_article_text(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text.strip()
    except Exception:
        return ""


# ----------------------------
# AI Summary
# ----------------------------
def get_ai_summary(title, article_text):

    if not article_text:
        return ""

    prompt = f"""
You are an education news editor.

Write a professional summary in exactly 2 sentences.

Title:
{title}

Article:
{article_text[:3500]}

Return ONLY the summary.
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        return completion.choices[0].message.content.strip()

    except Exception as e:
        print("Groq Error:", e)
        return ""
    # ----------------------------
# Tag Mapping
# ----------------------------

tag_mapping = {

    # Education
    "education": "Education",
    "school": "School",
    "schools": "School",
    "teacher": "Teachers",
    "teachers": "Teachers",
    "teaching": "Teaching",
    "student": "Students",
    "students": "Students",
    "classroom": "Classroom",
    "curriculum": "Curriculum",
    "learning": "Learning",
    "faculty": "Faculty",
    "professor": "Professor",
    "principal": "School Leadership",

    # Boards
    "cbse": "CBSE",
    "icse": "ICSE",
    "gseb": "GSEB",
    "ugc": "UGC",
    "aicte": "AICTE",
    "ncert": "NCERT",

    # Exams
    "exam": "Exams",
    "exams": "Exams",
    "result": "Results",
    "results": "Results",
    "admission": "Admissions",
    "admissions": "Admissions",
    "answer key": "Answer Key",
    "counselling": "Counselling",
    "cutoff": "Cutoff",
    "registration": "Registration",
    "application": "Application",

    # Competitive Exams
    "neet": "NEET",
    "jee": "JEE",
    "cuet": "CUET",
    "gate": "GATE",
    "cat": "CAT",
    "clat": "CLAT",
    "upsc": "UPSC",
    "ssc": "SSC",

    # EdTech
    "edtech": "EdTech",
    "artificial intelligence": "Artificial Intelligence",
    "machine learning": "Machine Learning",
    "robotics": "Robotics",
    "coding": "Coding",
    "stem": "STEM",

    # Digital Wellness
    "digital wellness": "Digital Wellness",
    "screen time": "Digital Wellness",
    "parental control": "Parental Control",
    "online learning": "Online Learning",
    "digital learning": "Digital Learning",
    "e-learning": "Online Learning",
    "smart classroom": "Smart Classroom",

    # Wellbeing
    "mental health": "Mental Health",
    "wellbeing": "Wellbeing",
    "student support": "Student Support",

    # NGO
    "ngo": "NGO",
    "foundation": "Foundation",
    "literacy": "Literacy",
    "inclusive education": "Inclusive Education",
    "special education": "Special Education",

    # Research
    "research": "Research",
    "innovation": "Innovation"
}

# ----------------------------
# Education Keywords
# ----------------------------

keywords = list(tag_mapping.keys())

# ----------------------------
# Words that indicate the article
# is NOT mainly education.
# ----------------------------

negative_keywords = [

    "murder",
    "crime",
    "felony",
    "felonies",
    "charged",
    "arrest",
    "arrested",
    "shooting",
    "bomb",
    "terrorist",
    "terrorism",
    "violence",
    "riot",
    "war",
    "earthquake",
    "flood",
    "cyclone",
    "hurricane",
    "election",
    "politics",
    "political",
    "parliament",
    "lok sabha",
    "rajya sabha",
    "minister accused",
    "court case",
    "supreme court",
    "high court",
    "police",
    "hazing",
    "fraternity",
    "assault"
]
# ----------------------------
# Existing URLs & Titles
# ----------------------------

existing_urls = set(
    normalize_url(url)
    for url in sh.col_values(2)
    if url.strip()
)

existing_titles = set(
    title.strip().lower()
    for title in sh.col_values(1)
    if title.strip()
)

print("=" * 60)
print("Starting News Extraction Pipeline...")
print("=" * 60)

# ----------------------------
# Read RSS Feeds
# ----------------------------

for feed_url in rss_urls:

    print(f"\nChecking Feed: {feed_url}")

    try:

        feed = feedparser.parse(feed_url)

        print(f"Articles Found: {len(feed.entries)}")

        for entry in feed.entries:

            title = entry.get("title", "").strip()
            link = normalize_url(entry.get("link", "").strip())

            if not title or not link:
                continue

            # ----------------------------
            # Duplicate Check
            # ----------------------------

            if link in existing_urls:
                print("Duplicate URL")
                continue

            if title.lower() in existing_titles:
                print("Duplicate Title")
                continue

            # ----------------------------
            # RSS Summary
            # ----------------------------

            rss_summary = entry.get("summary", "")
            rss_summary = re.sub("<.*?>", "", rss_summary)
            rss_summary = rss_summary.replace("\n", " ").strip()

            # ----------------------------
            # Download Full Article
            # ----------------------------

            article_text = get_article_text(link)

            if article_text:
                normal_summary = ".".join(
                    article_text.split(".")[:2]
                ).strip()
            else:
                normal_summary = rss_summary

            # ----------------------------
            # Text used for filtering
            # ----------------------------

            text = (
                title + " " +
                normal_summary + " " +
                article_text
            ).lower()

            # ----------------------------
            # Education Keyword Filter
            # ----------------------------

            matched_keywords = [
                k for k in keywords
                if k in text
            ]

            if len(matched_keywords) == 0:
                print("Skipped (No Education Keyword)")
                continue

            # ----------------------------
            # Negative Keyword Filter
            # ----------------------------

            negative_matches = [
                k for k in negative_keywords
                if k in text
            ]

            if len(negative_matches) >= 3:
                print("Skipped (Looks Non-Education)")
                continue

            # ----------------------------
            # Generate Tags
            # ----------------------------

            tags = []

            for keyword, tag in tag_mapping.items():

                if keyword in text:

                    if tag not in tags:
                        tags.append(tag)

            tags = ", ".join(tags[:3])

            # ----------------------------
            # AI Summary
            # ----------------------------

            ai_input = article_text if article_text else normal_summary

            ai_summary = get_ai_summary(
                title,
                ai_input[:3500]
            )

            # ----------------------------
            # Save to Google Sheet
            # ----------------------------

            sh.append_row([
                title,
                link,
                normal_summary,
                tags,
                "Draft",
                ai_summary
            ])

            existing_urls.add(link)
            existing_titles.add(title.lower())

            print("Added:", title)

    except Exception as e:

        print("Feed Error:", feed_url)
        print(e)
        