from moviepy.editor import *


def movie_add_image_clip(image_file: str, duration: int, start_time: int, clips: []):
    image_clip = ImageClip(image_file).set_duration(duration)
    clips.append(image_clip.set_start(start_time))


class Movie:
    def __init__(self):
        self.clips = []

    def movie_create_composite_clip(self, clips: []):
        self.clips.append(CompositeVideoClip(clips))

    def render_final_clip(self):
        # final_clip = concatenate_videoclips(self.clips, method='compose')
        # TODO: If we want to use concatenate, we need to subtract the delta between the
        # next and the previous compositevideoclips, as each concatenated compositevideoclip
        # is seen as a new, separate clip, starting at time mark 0s.
        # Therefore, we need to find the smallest time mark for all clips per root_clips (see generator.py l35)
        # and substract this value from every start time for all clips of that specific root_clips
        final_clip = CompositeVideoClip(self.clips)
        final_clip.write_videofile("test.mp4", fps=25)