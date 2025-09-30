import sys
from PIL import Image, ImageDraw, ImageFont

PODCAST_NAME = "clips/podcast-name.txt"

START_OFFSET_TEXT = (850, 105)
TEXTCOLOR = (255, 0, 0, 255)
LINE_SPACING = 140
SEPARATOR = "|"


def get_podcast_name():
    with open(PODCAST_NAME, "r") as f:
        return f.read().strip()


class ThumbnailCreator:
    def __init__(self):
        raise NotImplementedError("Subclasses must implement this method")

    def get_template_file(self):
        raise NotImplementedError("Subclasses must implement this method")

    def get_font_file(self):
        raise NotImplementedError("Subclasses must implement this method")

    def get_output_file(self):
        raise NotImplementedError("Subclasses must implement this method")

    def draw_trademark(self, draw):
        raise NotImplementedError("Subclasses must implement this method")

    def create_thumbnail(self,
                         text,
                         font_size,
                         template=get_template_file(),
                         output=get_output_file(),
                         font_file=get_font_file(),
                         text_color=TEXTCOLOR,
                         start_offset=START_OFFSET_TEXT,
                         line_spacing=LINE_SPACING):
        base = Image.open(template).convert('RGBA')
        image = Image.new('RGBA', base.size)
        font = ImageFont.truetype(font_file, font_size)
        draw = ImageDraw.Draw(image)
        offset = start_offset

        for i, line in enumerate(text.split(SEPARATOR)):
            left, top = offset
            top += i * line_spacing
            new_offset = (left, top)
            draw.text(new_offset, line, font=font, fill=text_color)
        self.draw_trademark(draw)
        draw.line((0, 0, 0, 765), fill="yellow", width=10)
        draw.line((0, 0, 1410, 0), fill="yellow", width=10)
        draw.line((0, 765, 1410, 765), fill="yellow", width=10)
        draw.line((1410, 765, 1410, 0), fill="yellow", width=20)
        out = Image.alpha_composite(base, image)
        out.save(output)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} 'title text seperated with bars' 'text font size(e.g.: 165)'")
        sys.exit(1)
    creator = ThumbnailCreator()
    creator.create_thumbnail(sys.argv[1], int(sys.argv[2]))