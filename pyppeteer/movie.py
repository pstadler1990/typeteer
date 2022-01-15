from moviepy.editor import *


class Movie:
    def __init__(self):
        self.clips = []

    def movie_add_image_clip(self, image_file: str, duration: int = 2):
        image_clip = ImageClip(image_file).set_duration(duration)
        self.clips.append(image_clip)

    def render_final_clip(self):
        final_clip = concatenate_videoclips(self.clips, method='compose')
        final_clip.write_videofile("test.mp4", fps=25)
