from googleapiclient.discovery import build
import pandas as pd

api_key = "AIzaSyDxQjG52UM8OFRB2Uqq8PaCWm8RnhxDw7E"
channel_id = "UCiT9RITQ9PW6BhXK0y2jaeg"

youtube = build("youtube", "v3", developerKey=api_key)

def get_channel_stats(youtube, channel_id):
    request = youtube.channels().list(
        part = "snippet, contentDetails, statistics",
        id = channel_id
    )
    response = request.execute()
    print(response)
    data = response['items'][0]['snippet']['title']
    return data

print(get_channel_stats(youtube, channel_id))