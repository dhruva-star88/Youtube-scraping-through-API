import json

# Load the JSON file
with open("news.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Get the length of the JSON object
length = len(data["items"])

title = []
# Loop through the list of items directly
for item in data["items"]:
    title.append(item["snippet"]["title"])

print(f"Number of key-value pairs in the JSON object: {length}")

print(len(title))