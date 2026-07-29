import feedparser
import gspread
import time
from urllib.parse import urlsplit, urlunsplit
from newspaper import Article
import re

def get_article_summary(url):
    try:
        article = Article(url)
        article.download()
        article.parse()

        text = article.text

        if not text:
            return ""

        sentences = text.split(".")
        summary = ".".join(sentences[:2]).strip()

        if summary:
            summary += "."

        return summary

    except Exception:
        return ""
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
    "https://www.edtechreview.in/feed/"]

tag_mapping = {

    # Teachers
    "teacher":"Teachers",
    "teachers":"Teachers",
    "teaching":"Teaching",
    "educator":"Teachers",
    "educators":"Teachers",
    "faculty":"Faculty",
    "professor":"Professor",
    "lecturer":"Faculty",
    "principal":"School Leadership",
    "headmaster":"School Leadership",
    "headmistress":"School Leadership",

    # Teaching
    "pedagogy":"Pedagogy",
    "lesson plan":"Lesson Planning",
    "lesson planning":"Lesson Planning",
    "classroom":"Classroom",
    "classroom management":"Classroom Management",
    "teaching methods":"Teaching Methods",
    "teaching strategy":"Teaching Methods",
    "curriculum":"Curriculum",
    "syllabus":"Curriculum",
    "assessment":"Assessment",
    "evaluation":"Assessment",
    "learning":"Learning",
    "instruction":"Teaching",
    "learning outcomes":"Learning Outcomes",

    # School
    "school":"School",
    "schools":"School",

    # Teacher Training
    "teacher training":"Teacher Training",
    "professional development":"Professional Development",
    "upskilling":"Professional Development",
    "reskilling":"Professional Development",
    "workshop":"Workshop",
    "seminar":"Seminar",
    "conference":"Conference",
    "webinar":"Webinar",

    # Education Policy
    "education":"Education",
    "education policy":"Education Policy",
    "education reform":"Education Policy",
    "education ministry":"Government",
    "ministry of education":"Government",
    "department of education":"Government",
    "cbse":"CBSE",
    "icse":"ICSE",
    "gseb":"GSEB",
    "ncert":"NCERT",
    "ugc":"UGC",
    "aicte":"AICTE",

    # Exams
    "exam":"Exams",
    "exams":"Exams",
    "board exam":"Board Exams",
    "board exams":"Board Exams",
    "result":"Results",
    "results":"Results",
    "answer key":"Answer Key",
    "admission":"Admissions",
    "admissions":"Admissions",
    "registration":"Registration",
    "application":"Application",
    "cutoff":"Cutoff",
    "merit list":"Merit List",
    "counselling":"Counselling",
    "seat allotment":"Seat Allotment",

    # Competitive Exams
    "neet":"NEET",
    "jee":"JEE",
    "jee mains":"JEE",
    "jee advanced":"JEE",
    "cuet":"CUET",
    "ugc net":"UGC NET",
    "net":"UGC NET",
    "set":"SET",
    "gate":"GATE",
    "cat":"CAT",
    "clat":"CLAT",
    "upsc":"UPSC",
    "ssc":"SSC",

    # Technology
    "edtech":"EdTech",
    "digital learning":"Digital Learning",
    "online learning":"Online Learning",
    "e-learning":"Online Learning",
    "virtual classroom":"Online Learning",
    "smart classroom":"Smart Classroom",
    "artificial intelligence":"Artificial Intelligence",
    "ai":"Artificial Intelligence",
    "machine learning":"Machine Learning",
    "coding":"Coding",
    "robotics":"Robotics",
    "stem":"STEM",

    # NGO
    "ngo":"NGO",
    "foundation":"Foundation",
    "charity":"NGO",
    "nonprofit":"NGO",
    "non-profit":"NGO",
    "literacy":"Literacy",
    "child education":"Child Education",
    "girl education":"Girls Education",
    "inclusive education":"Inclusive Education",
    "special education":"Special Education",
    "community learning":"Community Learning",

    # Research
    "research":"Research",
    "innovation":"Innovation",
    "teaching resources":"Teaching Resources",
    "classroom resources":"Teaching Resources",
    "best practices":"Best Practices",

    # Wellbeing
    "mental health":"Mental Health",
    "wellbeing":"Wellbeing",
    "student support":"Student Support"
}
# ----------------------------
# Education Keywords
# ----------------------------

keywords = [

    # Teachers
    "teacher","teachers","teaching","educator","educators",
    "faculty","professor","lecturer","principal",
    "headmaster","headmistress","school leader",

    # Teaching
    "pedagogy","lesson plan","lesson planning",
    "classroom","classroom management",
    "teaching methods","teaching strategy",
    "curriculum","syllabus","assessment",
    "evaluation","learning","instruction",
    "learning outcomes",

    # Schools
    "school","schools","primary school",
    "secondary school","high school",

    # Teacher Training
    "teacher training",
    "professional development",
    "upskilling",
    "reskilling",
    "workshop",
    "seminar",
    "conference",
    "webinar",

    # Education Policy
    "education",
    "education policy",
    "education reform",
    "education ministry",
    "ministry of education",
    "department of education",
    "cbse",
    "icse",
    "gseb",
    "ncert",
    "ugc",
    "aicte",

    # Exam Updates
    "exam",
    "exams",
    "board exam",
    "board exams",
    "result",
    "results",
    "answer key",
    "admission",
    "admissions",
    "registration",
    "application",
    "cutoff",
    "merit list",
    "counselling",
    "seat allotment",

    # Major Exams
    "neet",
    "jee",
    "jee mains",
    "jee advanced",
    "cuet",
    "ugc net",
    "net",
    "set",
    "gate",
    "cat",
    "clat",
    "upsc",
    "ssc",

    # EdTech
    "edtech",
    "digital learning",
    "online learning",
    "e-learning",
    "virtual classroom",
    "smart classroom",
    "artificial intelligence",
    "ai",
    "machine learning",
    "coding",
    "robotics",
    "stem",

    # NGO
    "ngo",
    "foundation",
    "charity",
    "nonprofit",
    "non-profit",
    "literacy",
    "child education",
    "girl education",
    "inclusive education",
    "special education",
    "community learning",

    # Research
    "research",
    "innovation",
    "teaching resources",
    "classroom resources",
    "best practices",

    # Wellbeing
    "mental health",
    "wellbeing",
    "student support"
]
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
# Existing URLs
# ----------------------------

existing_urls = set(sh.col_values(2))
existing_titles = set(
    title.strip().lower()
    for title in sh.col_values(1)
    if title.strip()
)

print("=" * 60)
print("Starting News Extraction Pipeline...")
print("=" * 60)

# ----------------------------
# Store New Articles
# ----------------------------

new_rows = []
queued_urls = set()
queued_titles = set()

for url in rss_urls:

    print(f"\nChecking Feed: {url}")

    try:
        feed = feedparser.parse(url)

        if feed.bozo:
            print("Warning: Feed parsing issue.")

        print(f"Articles Found: {len(feed.entries)}")

        
        for entry in feed.entries:        

         link = entry.link

         if entry.link in existing_urls:
           continue

        title = entry.title

        summary = get_article_summary(entry.link)
        if not summary:
         summary = entry.get("summary", "")
         summary = re.sub("<.*?>", "", summary)
         summary = summary.replace("\n", " ").strip() 
         summary = summary[:100]

        text = (title + " " + summary).lower()

        tags = []

        for keyword, tag in tag_mapping.items():

         if keyword.lower() in text:

            tags.append(tag)

         tags = list(dict.fromkeys(tags))

        tags = ", ".join(tags[:3])

        sh.append_row([
        title,
        entry.link,
        summary,
        tags,
        "Draft"
    ])

        existing_urls.add(entry.link)

        print("Added:", title)






        existing_urls.add(link)
        existing_titles.add(title.lower())

        queued_urls.add(link)
        queued_titles.add(title.lower())

        print(f"Queued: {title}")

    except Exception as e:
        print(f"Error reading feed: {url}")
        print(e)

# ----------------------------
# Upload All Rows Together
# ----------------------------



print("\n" + "=" * 60)
print(f"New Articles Added : {len(queued_urls)}")

print("=" * 60)
# ----------------------------
# Pipeline Summary
# ----------------------------

print("\n")
print("=" * 60)
print("NEWS EXTRACTION PIPELINE COMPLETED")
print("=" * 60)

print(f"Total New Articles Added : {len(queued_urls)}")
print(f"Total Existing URLs      : {len(existing_urls)}")

all_rows = sh.get_all_values()

print(f"Total Rows in Sheet : {len(all_rows) - 1}")

print("=" * 60)
print("Google Sheet Updated Successfully!")
print("=" * 60)
