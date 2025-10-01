from PIL import Image, ImageDraw, ImageFont

from create_podcast_header import PodcastHeaderCreator, get_podcast_name

OUTPUT = "clips/thumbnail-pc-chinese.png"

class PodcastHeaderCreatorChinese(PodcastHeaderCreator):
    def __init__(self):
        super().__init__()

    def draw_trademark(self, draw: ImageDraw.ImageDraw):
        draw.text((100, 100), "亚太深入焦点",
                  font=ImageFont.truetype("font/HanyiSentyPagodaRegular.ttf", 85), fill="yellow")
        draw.text((100, 350), "深度的分析视角",
                  font=ImageFont.truetype("font/HanyiSentyPagodaRegular.ttf", 75), fill="red")
        draw.text((20, 600), get_podcast_name(),
                  font=ImageFont.truetype("font/Bohme-Rounded.ttf", 65), fill="white")

    def get_output_file(self):
        return OUTPUT

if __name__ == "__main__":
    creator = PodcastHeaderCreatorChinese()
    creator.create_thumbnail()