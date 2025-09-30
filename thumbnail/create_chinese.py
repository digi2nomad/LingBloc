import sys
from PIL import Image, ImageDraw, ImageFont

from thumbnail.create_thumbnail import ThumbnailCreator, get_podcast_name

FONT_FILE = "font/HanyiSentyPagodaRegular.ttf"
OUTPUT = "clips/thumbnail-chinese.png"

class ThumbnailCreatorChinese(ThumbnailCreator):
    def __init__(self, output=OUTPUT, font_file=FONT_FILE):
        super().__init__()
        self.output = output
        self.font_file = font_file

    def get_font_file(self):
        return self.font_file

    def get_output_file(self):
        return self.output

    def draw_trademark(self, draw: ImageDraw.ImageDraw):
        draw.text((100,150), "  亚太",
        font=ImageFont.truetype(self.get_font_file(), 120), fill="yellow")
        draw.text((100,300), "深入焦点",
        font=ImageFont.truetype(self.get_font_file(), 120), fill="yellow")
        draw.text((30,550), get_podcast_name(),
        font=ImageFont.truetype("font/Bohme-Rounded.ttf", 65), fill="white")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} 'title text seperated with bars' 'text font size(e.g.: 125)'")
        sys.exit(1)
    creator = ThumbnailCreatorChinese()
    creator.create_thumbnail(sys.argv[1], int(sys.argv[2]))
