import feedparser
import gspread

# ----------------------------
# Google Sheets Connection
# ----------------------------

gc = gspread.service_account(filename="google_creds.json")
sh = gc.open("Explore_News_Beta_Staging").sheet1

# ----------------------------
# RSS Feeds
# ----------------------------

rss_urls = [
    "https://edutopia.org",
    
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
    "academic","academics","academy","education policy",
    "higher education","primary education","secondary education",
    "k-12","kindergarten","nursery","preschool","tuition",
    "coaching","institute","institution","faculty","professor",
    "lecturer","principal","headmaster","headmistress",

    # Indian Boards
    "cbse","icse","gseb","state board","board exam",

    # Competitive Exams
    "neet","jee","jee mains","jee advanced","cuet",
    "upsc","ssc","gpsc","mpsc","bpsc","railway exam",
    "ugc net","net","set","gate","cat","mat","clat",
    "nift","nid","aiims","iit","iim","nit","iiit",
    "admission","entrance","exam","exams","result",
    "results","rank","cutoff","merit","selection",
    "counselling","application","registration",

    # Scholarships
    "scholarship","scholarships","financial aid",
    "stipend","grant","education loan","fellowship",

    # EdTech
    "edtech","online learning","e-learning",
    "digital learning","virtual classroom",
    "smart classroom","lms","mooc","coursera",
    "udemy","byju","unacademy","vedantu",
    "physics wallah","pw",

    # Subjects
    "science","mathematics","math","physics",
    "chemistry","biology","computer science",
    "coding","programming","robotics","artificial intelligence",
    "machine learning","data science","engineering",
    "medical education","commerce","arts",

    # Research
    "research","innovation","laboratory",
    "publication","journal","stem","skill development",

    # Government
    "ugc","aicte","ncert","scert","ncf",
    "nta","education ministry","ministry of education",
    "department of education","education department",

    # Schools & Universities
    "hostel","library","campus placement",
    "placement","placements","internship",
    "career guidance","student welfare",

    # NGO & Non-Profit
    "ngo","non-profit","nonprofit","charity",
    "foundation","education foundation",
    "child education","girl education",
    "rural education","literacy",
    "inclusive education","special education",
    "education campaign","community learning",

    # Events
    "seminar","webinar","conference","workshop",
    "hackathon","competition","olympiad","quiz",

    # International
    "study abroad","exchange program",
    "international education","foreign university",

    # Misc
    "digital classroom","teacher training",
    "vocational education","distance education",
    "open university","open school","career","training"
]

# ----------------------------
# Existing URLs
# ----------------------------

existing_urls = sh.col_values(2)

print("Starting news extraction pipeline...")

# ----------------------------
# Fetch News
# ----------------------------

for url in rss_urls:

    print(f"\nChecking Feed: {url}")

    feed = feedparser.parse(url)

    print(f"Articles Found: {len(feed.entries)}")

    for entry in feed.entries:

        title = entry.get("title", "")
        summary = entry.get("summary", "")

        text = (title + " " + summary).lower()

        if any(keyword in text for keyword in keywords):

            if entry.link not in existing_urls:

                sh.append_row([
                    title,
                    entry.link,
                    "",
                    "",
                    "Draft"
                ])

                existing_urls.append(entry.link)

                print("Added:", title)

print("\nPipeline execution complete.")