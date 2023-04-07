IMAGE_PROMPT = """
provide a figure named {filename}. The description is: {description}.

Please understand and answer the image based on this information. The image understanding is complete, so don't try to understand the image again.

USER INPUT
============
"""


AUDIO_PROMPT = """
provide a audio named {filename}. The description is: {description}.

Please understand and answer the audio based on this information. The audio understanding is complete, so don't try to understand the audio again.

USER INPUT
============
"""

VIDEO_PROMPT = """
provide a video named {filename}. The description is: {description}.

Please understand and answer the video based on this information. The video understanding is complete, so don't try to understand the video again.

USER INPUT
============
"""

DATAFRAME_PROMPT = """
provide a dataframe named {filename}. The description is: {description}.

You are able to use the dataframe to answer the question.
You have to act like an data analyst who can do an effective analysis through dataframe.

USER INPUT
============
"""
