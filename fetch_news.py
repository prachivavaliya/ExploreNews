import feedparser
import gspread
import time

# ----------------------------
# Google Sheets Connection
# ----------------------------

gc = gspread.service_account(filename="google_creds.json")
sh = gc.open("Explore_News_Beta_Staging").sheet1

# ----------------------------
# RSS Feeds
# ----------------------------

rss_urls = [
    "https://indianexpress.com/section/education/feed/",
    "https://www.educationworld.in/feed/",
    "https://www.livemint.com/rss/education",
    "https://www.indiatoday.in/rss/1206578",
    "https://www.thehindu.com/education/feeder/default.rss"
]

# ----------------------------
# Education Keywords
# ----------------------------

keywords = [

    # General Education
    "education","educational","school","schools","schooling",
    "student","students","teacher","teachers","teaching",
    "college","colleges","university","universities","campus",
    "classroom","learning","learner","curriculum","syllabus",
    "academic","academics","academy","higher education",
    "primary education","secondary education",
    "k-12","kindergarten","nursery","preschool",
    "tuition","coaching","institute","institution",
    "faculty","professor","lecturer","principal",
    "headmaster","headmistress",

    # Boards
    "cbse","icse","gseb","board exam","state board",

    # Entrance Exams
    "neet","jee","jee mains","jee advanced","cuet",
    "upsc","ssc","gpsc","mpsc","bpsc",
    "ugc net","net","set","gate","cat",
    "clat","mat","nift","nid",
    "iit","nit","iiit","iim","aiims",

    # Exam Process
    "exam","exams","result","results","rank",
    "cutoff","merit","admission","admissions",
    "application","registration","counselling",
    "counseling","seat allotment",

    # Scholarships
    "scholarship","scholarships","financial aid",
    "grant","stipend","fellowship","education loan",

    # EdTech
    "edtech","online learning","e-learning",
    "digital learning","virtual classroom",
    "smart classroom","lms","mooc",
    "coursera","udemy","byju","unacademy",
    "vedantu","physics wallah","pw",

    # Subjects
    "science","mathematics","math","physics",
    "chemistry","biology","computer science",
    "coding","programming","robotics",
    "artificial intelligence","machine learning",
    "data science","engineering",
    "medical education","commerce","arts",

    # Research
    "research","innovation","laboratory",
    "publication","journal","stem",
    "skill development",

    # Government Bodies
    "ugc","aicte","ncert","scert",
    "nta","education ministry",
    "ministry of education",

    # Campus
    "hostel","library","placement",
    "placements","internship",
    "career guidance","student welfare",

    # NGO
    "ngo","foundation","charity",
    "child education","girl education",
    "literacy","inclusive education",
    "special education","community learning",

    # Events
    "seminar","webinar","conference",
    "workshop","hackathon",
    "competition","olympiad","quiz",

    # International
    "study abroad","exchange program",
    "international education",
    "foreign university",

    # Misc
    "teacher training",
    "vocational education",
    "distance education",
    "open university",
    "open school",
    "career",
    "training"
]
# ----------------------------
# Existing URLs
# ----------------------------

existing_urls = set(sh.col_values(2))

print("=" * 60)
print("Starting News Extraction Pipeline...")
print("=" * 60)

# ----------------------------
# Store New Articles
# ----------------------------

new_rows = []

for url in rss_urls:

    print(f"\nChecking Feed: {url}")

    try:
        feed = feedparser.parse(url)

        if feed.bozo:
            print("Warning: Feed parsing issue.")

        print(f"Articles Found: {len(feed.entries)}")

        for entry in feed.entries:

            title = entry.get("title", "").strip()
            summary = entry.get("summary", "").strip()
            link = entry.get("link", "").strip()

            if not title or not link:
                continue

            text = (title + " " + summary).lower()

            # Check if article is education related
            if not any(keyword in text for keyword in keywords):
                continue

            # Skip duplicate URLs
            if link in existing_urls:
                continue

            # Store row (don't upload yet)
            new_rows.append([
                title,
                link,
                "",
                "",
                "Draft"
            ])

            existing_urls.add(link)

            print(f"Queued: {title}")

    except Exception as e:
        print(f"Error reading feed: {url}")
        print(e)

# ----------------------------
# Upload All Rows Together
# ----------------------------

print("\n" + "=" * 60)

if new_rows:

    print(f"Uploading {len(new_rows)} new articles...")

    try:

        sh.append_rows(
            new_rows,
            value_input_option="RAW"
        )

        print("Upload Successful!")

    except Exception as e:

        print("Upload Failed!")
        print(e)

else:

    print("No New Articles Found.")

print("=" * 60)
# ----------------------------
# Pipeline Summary
# ----------------------------

print("\n")
print("=" * 60)
print("NEWS EXTRACTION PIPELINE COMPLETED")
print("=" * 60)

print(f"Total New Articles Added : {len(new_rows)}")
print(f"Total Existing URLs      : {len(existing_urls)}")

print("=" * 60)
print("Google Sheet Updated Successfully!")
print("=" * 60)