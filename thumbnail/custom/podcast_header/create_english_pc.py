from PIL import Image, ImageDraw, ImageFont

from thumbnail.custom.podcast_header.create_podcast_header import PodcastHeaderCreator, get_podcast_name

OUTPUT = "clips/thumbnail-pc-english.png"

class PodcastHeaderCreatorEnglish(PodcastHeaderCreator):
    def __init__(self):
        super().__init__()

    def draw_trademark(self, draw: ImageDraw.ImageDraw):
        draw.text((45, 100), "Asia Pacific Deep Dive",
                  font=ImageFont.truetype("font/Gendy.otf", 70), fill="yellow")
        draw.text((200, 280), "in-depth",
                  font=ImageFont.truetype("font/Gendy.otf", 115), fill="red")
        draw.text((200, 420), "analysis",
                  font=ImageFont.truetype("font/Gendy.otf", 115), fill="red")
        draw.text((20, 600), get_podcast_name(),
                  font=ImageFont.truetype("font/Bohme-Rounded.ttf", 65), fill="white")

    def get_output_file(self):
        return OUTPUT

if __name__ == "__main__":
    creator = PodcastHeaderCreatorEnglish()
    creator.create_thumbnail()
