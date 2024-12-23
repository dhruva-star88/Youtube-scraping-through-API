import csv
from googleapiclient.discovery import build
from pytube import YouTube
from datetime import datetime, timedelta
import isodate 
from geopy.geocoders import Nominatim

def fetch_captions(video_id):
    try:
        yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        captions = yt.captions  # Fetch captions object

        if not captions:  # If no captions are available at all
            return "No Captions Available"
        
        # Try fetching English captions
        if "en" in captions:
            caption = captions["en"]
            caption_format = caption.format  # Get the caption format (srt, vtt, etc.)
            if caption_format == "srt":
                return caption.generate_srt_captions()  # SRT format
            elif caption_format == "vtt":
                return caption.generate_webvtt_captions()  # WebVTT format
            elif caption_format == "xml":
                return caption.generate_xml_captions()  # XML format
            else:
                return f"Captions available in {caption_format} format, but unsupported format"
        
        # Fallback: If English captions aren't available, check for other languages
        for caption in captions.all():
            caption_format = caption.format  # Get the caption format (srt, vtt, etc.)
            if caption_format == "srt":
                return caption.generate_srt_captions()
            elif caption_format == "vtt":
                return caption.generate_webvtt_captions()
            elif caption_format == "xml":
                return caption.generate_xml_captions()
            else:
                return f"Captions available in {caption_format} format, but unsupported format"
        
        return "No Captions Available"  # If no captions in any language

    except Exception as e:
        return f"Error fetching captions: {str(e)}"
    
    
print(fetch_captions("5RDSkR8_AQ0"))