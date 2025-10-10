import json
import sys

class Video:
    def __init__(self, title, description, thumbnail, video, playlists, tags):
        self.title = title
        self.description = description
        self.thumbnail = thumbnail
        self.video = video
        self.playlists = playlists
        self.tags = tags

def load_json(json_file: str):
    data = None
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            authentication = data.get('authentication')
            if authentication:
                password = authentication.get('password')
                email = authentication.get('email')
            files = data.get('files')
            if files:
                videos = []
                for file in files:
                    title = file.get('title')
                    description = file.get('description')
                    thumbnail = file.get('thumbnail')
                    video = file.get('video')
                    playlists = file.get('playlists')
                    if playlists:
                        for playlist in playlists:
                            print(playlist)
                    tags = file.get('tags')
                    if tags:
                        for tag in tags:
                            print(tag)
                    videos.append(Video(title, description, thumbnail, video, playlists, tags))
    except FileNotFoundError:
        print(f"Error: File {json_file} not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {json_file}")
        sys.exit(1)
    return email, password, videos

if __name__ == "__main__":
    load_json("clips/upload.json")