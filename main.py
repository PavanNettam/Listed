import requests
from bs4 import BeautifulSoup
import json
from googlesearch import search
from googleapiclient.discovery import build
import time
import yaml
from yaml.loader import SafeLoader

api_key = ""
with open('secure.yaml') as f:
    data = yaml.load(f, Loader=SafeLoader)
    api_key = data

def get_google_results(query, num_results):
    url = f"https://www.google.com/search?q={query}&num={num_results}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def parse_google_results(html):
    soup = BeautifulSoup(html, "html.parser")
    results = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href is not None and href.startswith("/url?q="):
            url = href.replace("/url?q=", "")
            if "youtube.com" in url and "openinapp.co" in url:
                results.append(url)
    return results

def get_youtube_channel(url):
    channel_url = url.split("/channel/", 1)[1].split("/", 1)[0]
    return channel_url

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

query = "site:youtube.com openinapp.co"
num_results = 10000
channels = scrape_youtube_channels(query, num_results, api_key)

output = json.dumps(channels, indent=4)
filename = "youtube_channels.json"
with open(filename, "w") as file:
    file.write(output)

print(f"Results saved to {filename} successfully.")
