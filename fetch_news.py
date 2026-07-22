import feedparser
import gspread

# 1. Connect to Google Sheets via Service Account API
# (Ensure your 'google_creds.json' file is present in your folder)

gc = gspread.service_account(filename='google_creds.json')
sh = gc.open("Explore_News_Beta_Staging").sheet1

# 2. Add your 3 discovered RSS feeds to this list

rss_urls = [
    "https://www.edutopia.org/",
    "https://www.the74million.org/feed/",
    "https://www.insidehighered.com/rss.xml"
]

# 3. Pull existing URLs from Column B to ensure we never pull duplicates

existing_urls = sh.col_values(2)

print("Starting news extraction pipeline...")

for url in rss_urls:
    feed = feedparser.parse(url)

    for entry in feed.entries:
        # Check if the article link has already been gathered before
        if entry.link not in existing_urls:
            # Add data to the next empty row with the status 'Draft'
            sh.append_row([entry.title, entry.link, "", "", "Draft"])

            print(f"Successfully staged: {entry.title}")

print("Pipeline execution complete.")