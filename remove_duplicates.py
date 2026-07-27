import gspread

# Google Sheets Connection
gc = gspread.service_account(filename="google_creds.json")
sh = gc.open("Prachi_Explore_News_Beta_Staging").sheet1

# Read all data
records = sh.get_all_values()

seen = set()
rows_to_keep = []

duplicates = []

# Keep header
rows_to_keep.append(records[0])

# Remove duplicates
for sheet_row, row in enumerate(records[1:], start=2):  # Sheet row starts from 2

    title = row[0].strip()
    url = row[1].strip()

    key = (title.lower(), url)

    if key not in seen:
        seen.add(key)
        rows_to_keep.append(row)
    else:
        duplicates.append((sheet_row, title))

# Print duplicate details
print("\n" + "=" * 60)
print("DUPLICATE ARTICLES FOUND")
print("=" * 60)

if duplicates:
    for row_no, title in duplicates:
        print(f"Row {row_no} deleted -> {title}")
else:
    print("No duplicates found.")

# Clear sheet
sh.clear()

# Upload cleaned data
sh.update("A1", rows_to_keep)

print("\n" + "=" * 60)
print("DUPLICATE REMOVAL COMPLETED")
print("=" * 60)
print(f"Duplicates Removed : {len(duplicates)}")
print(f"Total Unique Articles : {len(rows_to_keep)-1}")
print("=" * 60)