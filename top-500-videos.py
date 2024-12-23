import csv
from googleapiclient.discovery import build

# Initialize YouTube API client
API_KEY = "AIzaSyCLQt1n_--BRrbQ4rU60fk3f3uAkG3M3tA"
youtube = build("youtube", "v3", developerKey=API_KEY)

def fetch_top_videos(genre, max_results=500):
    videos = []
    next_page_token = None

    while len(videos) < max_results:
        response = youtube.search().list(
            q=genre,
            type="video",
            part="id,snippet",
            maxResults=50,  # Maximum per request
            order="viewCount",  # Sort by popularity
            pageToken=next_page_token
        ).execute()

        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            description = item["snippet"].get("description", "")
            channel_title = item["snippet"]["channelTitle"]
            published_at = item["snippet"]["publishedAt"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            tags = item["snippet"].get("tags", [])
            category = item["snippet"].get("categoryId", "")
            
            videos.append({
                "Video ID": video_id,
                "Title": title,
                "Description": description,
                "Channel Title": channel_title,
                "Video URL": video_url,
                "Tags": tags,
                "Category": category,
                "Published At": published_at
            })

            if len(videos) >= max_results:
                break

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return videos


def get_video_details(video_ids):
    details = []
    for i in range(0, len(video_ids), 50):  # Process in batches of 50
        response = youtube.videos().list(
            part="statistics,contentDetails,topicDetails,snippet",  # Ensure snippet and topicDetails are included
            id=",".join(video_ids[i:i+50])
        ).execute()

        for item in response.get("items", []):
            video_id = item["id"]
            view_count = item["statistics"].get("viewCount", 0)
            comment_count = item["statistics"].get("commentCount", 0)
            duration = item["contentDetails"]["duration"]
            captions_available = item["contentDetails"].get("caption", "false")
            
            # Safely access topicDetails
            topic_details = item.get("topicDetails", {}).get("topicCategories", [])

            # Safely access snippet
            snippet = item.get("snippet", {})
            location = snippet.get("location", "N/A")

            details.append({
                "Video ID": video_id,
                "View Count": view_count,
                "Comment Count": comment_count,
                "Duration": duration,
                "Captions Available": captions_available,
                "Topic Details": topic_details,
                "Location": location
            })

    return details



def save_to_csv(videos, filename="videos.csv"):
    # Define the field names for the CSV file
    fieldnames = [
        "Video ID", "Title", "Description", "Channel Title", 
        "Keyword Tags", "YouTube Video Category", "Topic Details", 
        "Video Published at", "Video Duration", "View Count", 
        "Comment Count", "Captions Available", "Caption Text", "Location"
    ]
    
    # Open the file and write the data
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # Write the header
        writer.writeheader()
        
        # Write video data
        for video in videos:
            # Ensure only fields in `fieldnames` are written
            filtered_video = {key: video.get(key, "") for key in fieldnames}
            writer.writerow(filtered_video)


def main():
    genre = input("Enter the genre (e.g., 'science-fiction'): ")
    max_results = 500  # Change this to the number of videos you want to fetch

    # Fetch top videos based on genre
    videos = fetch_top_videos(genre, max_results)

    # Extract video IDs for the details
    video_ids = [video["Video ID"] for video in videos]

    # Fetch additional video details
    video_details = get_video_details(video_ids)

    # Merge the data (top video data + additional details)
    for i, video in enumerate(videos):
        if i < len(video_details):
            video.update(video_details[i])

    # Save all the collected data to a CSV file
    save_to_csv(videos)

    print(f"Data saved to video_details.csv with {len(videos)} videos.")


if __name__ == "__main__":
    main()
