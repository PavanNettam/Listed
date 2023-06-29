import json
from googleapiclient.discovery import build
import yaml
from yaml.loader import SafeLoader

def scrape_youtube_channels(query, num_results, api_key):
    api_service_name = "youtube"
    api_version = "v3"
    
    youtube = build(api_service_name, api_version, developerKey=api_key)
    
    channels = []
    page_token = None
    while len(channels) < num_results:
        request = youtube.search().list(
            part="snippet",
            q=query,
            type="channel",
            maxResults=min(num_results - len(channels), 50),
            pageToken=page_token
        )
        response = request.execute()
        
        for item in response["items"]:
            channel_id = item["id"]["channelId"]
            channels.append("https://www.youtube.com/channel/"+channel_id)
        
        if "nextPageToken" in response:
            page_token = response["nextPageToken"]
        else:
            break
    
    return channels[:num_results]

# Driver Code
api_key = ""
with open('secure.yaml') as f:
    data = yaml.load(f, Loader=SafeLoader)
    api_key = data

query = "site:youtube.com openinapp.co"
num_results = 10000
channels = scrape_youtube_channels(query, num_results, api_key)

output = json.dumps(channels, indent=4)
filename = "youtube_channels.json"
with open(filename, "w") as file:
    file.write(output)

print(f"Results saved to {filename} successfully.")
