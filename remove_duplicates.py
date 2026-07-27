import gspread

# Google Sheets Connection
gc = gspread.service_account(filename="google_creds.json")
sh = gc.open("Prachi_Explore_News_Beta_Staging").sheet1

# Read all data
records = sh.get_all_values()

seen = set()
rows_to_keep = []

# Keep header
rows_to_keep.append(records[0])

# Remove duplicates
for row in records[1:]:

    title = row[0].strip().lower()
    url = row[1].strip()

    key = (title, url)

    if key not in seen:
        seen.add(key)
        rows_to_keep.append(row)

# Clear sheet
sh.clear()

# Upload cleaned data
sh.update("A1", rows_to_keep)

print(f"Duplicates Removed!")
print(f"Total Unique Articles: {len(rows_to_keep)-1}")