import csv
from googleapiclient.discovery import build
from pytube import YouTube
from datetime import datetime, timedelta
import isodate 


# Initialize YouTube API client
API_KEY = "AIzaSyCLQt1n_--BRrbQ4rU60fk3f3uAkG3M3tA"
youtube = build("youtube", "v3", developerKey=API_KEY)

# Convert of duration from ISO format
def convert_duration(iso_duration):
    try:
        duration = isodate.parse_duration(iso_duration)
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    except Exception:
        return "Invalid Duration"
    
def convert_published_at(iso_datetime):
    try:
        dt = datetime.fromisoformat(iso_datetime.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "Invalid DateTime"
    
    
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
        print("Fetched Data: ",response)
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            description = item["snippet"].get("description", "")
            channel_title = item["snippet"]["channelTitle"]
            iso_published_at = item["snippet"].get("publishedAt", "")
            published_at = convert_published_at(iso_published_at)
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
            part="statistics,contentDetails,topicDetails,snippet,recordingDetails",  # Ensure snippet and topicDetails are included
            id=",".join(video_ids[i:i+50])
        ).execute()
        print("Details Data: ",response)
        for item in response.get("items", []):
            video_id = item["id"]
            view_count = item["statistics"].get("viewCount", 0)
            comment_count = item["statistics"].get("commentCount", 0)
            iso_duration = item["contentDetails"]["duration"]
            duration = convert_duration(iso_duration)
            captions_available = "true" if "caption" in item["contentDetails"] else "false"
            
            # Safely access topicDetails
            topic_details = item.get("topicDetails", {}).get("topicCategories", [])

            # Safely access snippet
            rec = item.get("recordingDetails", {})
            location = rec.get("location", "N/A")

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


def fetch_captions(video_id):
    try:
        yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        captions = yt.captions.get_by_language_code("en")
        if "en" in captions:  # Check for English captions
            return captions["en"].generate_srt_captions()
        
        # If no English captions, fetch the first available language
        for code, caption in captions.items():
            return caption.generate_srt_captions()
        
        return "No Captions Available"
    except Exception as e:
        return f"Error fetching captions: {str(e)}"


def save_to_csv(videos, filename="videos.csv"):
    # Define the field names for the CSV file
    fieldnames = [
        "Video ID", "Title", "Description", "Channel Title", 
        "Video URL", "Tags", "Category", "Published At",
        "View Count", "Comment Count", "Duration","Topic Details", 
        "Captions Available", "Caption Text", "Location"
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
            if video.get("Captions Available") == "true":
                video["Caption Text"] = fetch_captions(video["Video ID"])

    # Save all the collected data to a CSV file
    save_to_csv(videos)

    print(f"Data saved to video_details.csv with {len(videos)} videos.")


if __name__ == "__main__":
    main()
