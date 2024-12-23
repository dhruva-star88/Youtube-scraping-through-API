from googleapiclient.discovery import build

api_key = "AIzaSyDxQjG52UM8OFRB2Uqq8PaCWm8RnhxDw7E"

youtube = build("youtube", "v3", developerKey=api_key)
playlist_id = "UUiT9RITQ9PW6BhXK0y2jaeg"
def get_video_ids(youtube, playlist_id):
    request = youtube.playlistItems().list(
        part="contentDetails",
        playlistId = playlist_id,
        maxResults = 50
    )
    response = request.execute()
    
    video_ids = []
    for i in range(len(response["items"])):
        video_ids.append(response["items"][i]["contentDetails"]["videoId"])
        
    next_page_tokens = response.get("nextPageToken")
    more_pages = True
    
    while(more_pages):
        if next_page_tokens is None:
            more_pages = False
        else:
            request = youtube.playlistItems().list(
            part="contentDetails",
            playlistId = playlist_id,
            maxResults = 50,
            pageToken = next_page_tokens) #to get the ids from next page
            
            response = request.execute()
    
            for i in range(len(response["items"])):
                video_ids.append(response["items"][i]["contentDetails"]["videoId"])
                
            next_page_tokens = response.get("nextPageToken")
        
    return video_ids

print(get_video_ids(youtube, playlist_id))