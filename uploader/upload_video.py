import os,sys

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_video(
    credentials,
    video,
    title,
    description,
    thumbnail,
    privacy_status="private"):
    youtube = build("youtube", "v3", credentials=credentials)
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": [],  # Add tags if needed
            # 'categoryId': '22'  # Change the category ID if needed
        },
        "status": {"privacyStatus": privacy_status},
    }

    # Upload the video
    media = MediaFileUpload(video)
    response = (
        youtube.videos()
        .insert(part="snippet,status", body=request_body, media_body=media)
        .execute()
    )
    print(f"Video uploaded successfully. id: {response['id']}")


def get_credentials(cred_path):
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    if os.path.exists(cred_path):
        return InstalledAppFlow.from_client_secrets_file(
            cred_path, scopes
        ).run_local_server(port=0, open_browser=False)
    print("Specify valid API credentials in 'client_secret.json'")
    return None

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(f"Usage: <video_file> <title> <description_file> <thumbnail_file>")
        sys.exit(1)

    client_secret_json = os.environ['GOOGLE_CLIENT_SECRET_JSON']
    cred = get_credentials(client_secret_json)
    upload_video(cred,
                 sys.argv[1],
                 sys.argv[2],
                 open(sys.argv[3], 'r').read(),
                 sys.argv[4])
    #upload_video(cred,
    #             "clips/English.mp4",
    #             "Test Video from API",
    #             "This is a test video uploaded via YouTube API",
    #             "clips/thumbnail-english.jpg")
