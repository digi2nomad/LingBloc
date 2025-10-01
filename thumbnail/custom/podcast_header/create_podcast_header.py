from PIL import Image, ImageDraw

PODCAST_NAME = "clips/podcast-name.txt"
TEMPLATE = "clips/thumbnail-podcast.png"

def get_podcast_name():
    with open(PODCAST_NAME, "r") as f:
        return f.read().strip()

class PodcastHeaderCreator:
    def __init__(self):
        pass

    def draw_trademark(self, draw):
        raise NotImplementedError("Subclasses must implement this method")

    def get_output_file(self):
        raise NotImplementedError("Subclasses must implement this method")

    def create_thumbnail(
            self,
            template=TEMPLATE,
            ):
        base = Image.open(template).convert('RGBA')
        image = Image.new('RGBA', base.size)
        draw = ImageDraw.Draw(image)
        self.draw_trademark(draw)
        out = Image.alpha_composite(base, image)
        out.save(self.get_output_file())

if __name__ == "__main__":
    creator = PodcastHeaderCreator()
    creator.create_thumbnail()